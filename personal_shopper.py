# Sistema Personal Shopper - VERSIÓN WEB (STREAMLIT)
import streamlit as st
from typing import List, Dict
from openpyxl import Workbook

TAX_TEXAS = 0.0825
DOLAR = 18
MARGEN = 0.25

if "inventario" not in st.session_state:
    st.session_state.inventario = []
    st.session_state.ventas = []
    st.session_state.clientes = {}

inventario = st.session_state.inventario
ventas = st.session_state.ventas
clientes = st.session_state.clientes

def calcular_costo(precio_usd):
    return round(precio_usd * (1 + TAX_TEXAS) * DOLAR, 2)

def calcular_precio(precio_usd, margen=None):
    if margen is None:
        margen = MARGEN
    return round(calcular_costo(precio_usd) * (1 + margen), 2)

def obtener_cliente(nombre):
    if nombre not in clientes:
        clientes[nombre] = {"deuda": 0, "abonado": 0, "ganancia": 0, "compras": []}
    return clientes[nombre]

st.title("🛍️ Personal Shopper PRO")

menu = st.sidebar.selectbox("Menú", [
    "Agregar producto",
    "Ver inventario",
    "Registrar venta",
    "Registrar abono",
    "Generar ticket",
    "Resumen admin",
    "Exportar Excel"
])

if menu == "Agregar producto":
    nombre = st.text_input("Nombre")
    precio_usd = st.number_input("Precio USD", min_value=0.0)

    modo = st.radio("Tipo de precio", ["Default", "Margen personalizado", "Manual"])

    if modo == "Manual":
        precio = st.number_input("Precio final MXN", min_value=0.0)
    elif modo == "Margen personalizado":
        margen = st.number_input("Margen", value=0.3)
        precio = calcular_precio(precio_usd, margen)
    else:
        precio = calcular_precio(precio_usd)

    if st.button("Agregar"):
        costo = calcular_costo(precio_usd)
        inventario.append({"nombre": nombre, "costo": costo, "precio": precio})
        st.success("Producto agregado")

elif menu == "Ver inventario":
    st.write(inventario)

elif menu == "Registrar venta":
    cliente_nombre = st.text_input("Cliente")
    productos = [p["nombre"] for p in inventario]

    if productos:
        producto_nombre = st.selectbox("Producto", productos)
        cantidad = st.number_input("Cantidad", min_value=1)

        if st.button("Vender"):
            index = productos.index(producto_nombre)
            producto = inventario[index]
            cliente = obtener_cliente(cliente_nombre)

            total = producto["precio"] * cantidad
            costo = producto["costo"] * cantidad
            ganancia = total - costo

            venta = {"cliente": cliente_nombre, "producto": producto_nombre, "cantidad": cantidad, "total": total, "ganancia": ganancia}

            ventas.append(venta)
            cliente["deuda"] += total
            cliente["ganancia"] += ganancia
            cliente["compras"].append(venta)

            st.success("Venta registrada")
    else:
        st.warning("Agrega productos primero")

elif menu == "Registrar abono":
    cliente_nombre = st.text_input("Cliente")
    monto = st.number_input("Monto", min_value=0.0)

    if st.button("Registrar"):
        cliente = obtener_cliente(cliente_nombre)
        cliente["abonado"] += monto
        cliente["deuda"] -= monto
        st.success("Abono registrado")

elif menu == "Generar ticket":
    cliente_nombre = st.text_input("Cliente")

    if st.button("Generar"):
        cliente = obtener_cliente(cliente_nombre)

        ticket = f"🧾 {cliente_nombre}\n"
        for c in cliente["compras"]:
            ticket += f"{c['producto']} x{c['cantidad']} = ${c['total']}\n"

        ticket += f"Total: ${cliente['deuda'] + cliente['abonado']}\n"
        ticket += f"Abonado: ${cliente['abonado']}\n"
        ticket += f"Debe: ${cliente['deuda']}"

        st.text_area("Ticket", ticket)

elif menu == "Resumen admin":
    total = sum(v["total"] for v in ventas)
    ganancia = sum(v["ganancia"] for v in ventas)

    st.write("Ventas totales:", total)
    st.write("Ganancia total:", ganancia)

    ranking = sorted(clientes.items(), key=lambda x: x[1]["ganancia"], reverse=True)
    st.write("Ranking:", ranking)

elif menu == "Exportar Excel":
    if st.button("Generar Excel"):
        wb = Workbook()
        ws = wb.active
        ws.append(["Cliente", "Producto", "Cantidad", "Total", "Ganancia"])

        for v in ventas:
            ws.append([v["cliente"], v["producto"], v["cantidad"], v["total"], v["ganancia"]])

        wb.save("reporte.xlsx")
        st.success("Excel generado")
