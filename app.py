import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURACIÓN DE LA BASE DE DATOS LOCAL ---
DB_FILE = "beer_game_db.json"
ROLES = ["Minorista", "Mayorista", "Distribuidor", "Fábrica"]

DEMANDA_CLIENTE = {str(i): (4 if i <= 4 else 8) for i in range(1, 50)}

def cargar_bd():
    if not os.path.exists(DB_FILE):
        guardar_bd({"semana": 1, "pedidos": {}})
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_bd(datos):
    with open(DB_FILE, "w") as f:
        json.dump(datos, f)

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Beer Game - EBC", layout="centered")

st.title("🍺 El Juego de la Cerveza")
st.markdown("**Unidad 3:** Teoría de Sistemas y Logística Integral | **Prof.** Ricardo Jarquin")

bd = cargar_bd()
semana_actual = bd["semana"]
str_semana = str(semana_actual)

if str_semana not in bd["pedidos"]:
    bd["pedidos"][str_semana] = {}
    guardar_bd(bd)

st.sidebar.title("Configuración")
rol = st.sidebar.selectbox("Selecciona tu Rol:", ["Profesor (Monitor)"] + ROLES)

st.sidebar.divider()
st.sidebar.info(f"📅 **Semana Actual del Juego:** {semana_actual}")

if rol == "Profesor (Monitor)":
    st.header("📊 Panel de Control Directivo")
    st.subheader(f"Estatus de la Semana {semana_actual}")
    pedidos_semana = bd["pedidos"][str_semana]
    
    col_roles = st.columns(4)
    todos_pidieron = True
    
    for i, r in enumerate(ROLES):
        with col_roles[i]:
            if r in pedidos_semana:
                st.success(f"**{r}**\n\n✅ Pidió: {pedidos_semana[r]}")
            else:
                st.error(f"**{r}**\n\n⏳ Esperando...")
                todos_pidieron = False

    st.divider()
    
    if todos_pidieron:
        st.info("Todos los equipos han enviado sus pedidos. Puedes avanzar.")
        if st.button("Avanzar a la Semana " + str(semana_actual + 1), type="primary"):
            bd["semana"] += 1
            guardar_bd(bd)
            st.rerun()
    else:
        st.warning("Faltan equipos por pedir.")

    with st.expander("⚙️ Opciones de Administrador"):
        if st.button("Reiniciar Juego Completo"):
            guardar_bd({"semana": 1, "pedidos": {}})
            st.rerun()

    st.divider()
    st.subheader("📈 Análisis del Efecto Látigo (Bullwhip Effect)")
    
    historial = []
    for sem in range(1, semana_actual + 1):
        s = str(sem)
        fila = {"Semana": sem, "Demanda Real": DEMANDA_CLIENTE[s]}
        if s in bd["pedidos"]:
            for r in ROLES:
                fila[r] = bd["pedidos"][s].get(r, 0)
        historial.append(fila)
    
    df_grafica = pd.DataFrame(historial).set_index("Semana")
    st.line_chart(df_grafica)

else:
    st.header(f"🏢 Rol: {rol}")
    ya_pidio = rol in bd["pedidos"][str_semana]
    
    if ya_pidio:
        st.success("✅ Ya enviaste tu pedido de esta semana.")
        st.metric(label="Tu pedido fue de:", value=f"{bd['pedidos'][str_semana][rol]} cajas")
        st.info("Espera a que el profesor avance a la siguiente semana.")
    else:
        st.warning(f"⚠️ Es tu turno. Estamos en la **Semana {semana_actual}**.")
        with st.form(key=f"form_pedido_{semana_actual}"):
            cantidad = st.number_input("¿Cuántas cajas vas a pedir?", min_value=0, max_value=500, value=10, step=1)
            submit = st.form_submit_button("Enviar Pedido 🚚", type="primary")
            
            if submit:
                bd["pedidos"][str_semana][rol] = cantidad
                guardar_bd(bd)
                st.success("¡Pedido registrado exitosamente!")
                st.rerun()
