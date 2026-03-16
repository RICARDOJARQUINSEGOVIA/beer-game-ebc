import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURACIÓN DE LA BASE DE DATOS LOCAL ---
DB_FILE = "beer_game_db.json"
ROLES = ["Minorista", "Mayorista", "Distribuidor", "Fábrica"]

# Demanda oculta y Noticias para generar "Ruido" en el sistema (Psicología del Efecto Látigo)
DEMANDA_CLIENTE = {str(i): (4 if i <= 4 else 8) for i in range(1, 50)}
NOTICIAS = {
    1: "🟢 El mercado está tranquilo. Las ventas fluyen con normalidad.",
    3: "🟡 RUMOR: Se pronostica una ola de calor para el próximo mes.",
    5: "🔴 ¡ÚLTIMA HORA! Un video viral de un cantante bebiendo nuestra cerveza ha disparado el interés.",
    8: "🟡 NOTICIA: Termina la ola de calor. Los supermercados reportan pasillos llenos.",
    10: "🔴 CRISIS: Los clientes se quejan de estantes vacíos en las tiendas."
}

# --- SISTEMA DE ACCESOS (PINES) ---
PASSWORDS = {
    "Profesor (Monitor)": "adminebc",
    "Minorista": "1111",
    "Mayorista": "2222",
    "Distribuidor": "3333",
    "Fábrica": "4444"
}

def cargar_bd():
    if not os.path.exists(DB_FILE):
        guardar_bd({"semana": 1, "pedidos": {}})
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_bd(datos):
    with open(DB_FILE, "w") as f:
        json.dump(datos, f)

# --- INICIO DE LA APP ---
st.set_page_config(page_title="Beer Game - EBC", page_icon="🍺", layout="centered")

st.title("🍺 El Juego de la Cerveza: Edición EBC")
st.markdown("*¿Podrás sobrevivir al Efecto Látigo sin quebrar a tu empresa?*")

bd = cargar_bd()
semana_actual = bd["semana"]
str_semana = str(semana_actual)

if str_semana not in bd["pedidos"]:
    bd["pedidos"][str_semana] = {}
    guardar_bd(bd)

# --- MENÚ LATERAL Y LOGIN ---
st.sidebar.title("🔐 Acceso de Seguridad")
rol = st.sidebar.selectbox("Selecciona tu División:", ["Profesor (Monitor)"] + ROLES)
password = st.sidebar.text_input("Ingresa tu PIN de acceso:", type="password")

if password != PASSWORDS[rol]:
    st.warning("⚠️ Ingresa el PIN correcto para acceder a tu panel de control.")
    st.sidebar.info("Tip para el profe: El PIN del profesor es 'adminebc'. Los de los alumnos son 1111, 2222, 3333 y 4444.")
    st.stop() # Detiene la ejecución para que no vean el resto de la página

st.sidebar.success("Acceso concedido.")
st.sidebar.divider()
st.sidebar.metric(label="📅 Semana Actual", value=semana_actual)

# --- VISTA DEL PROFESOR (MONITOR) ---
if rol == "Profesor (Monitor)":
    st.header("👑 Centro de Mando Directivo")
    st.write("Bienvenido, Profesor Jarquin. Aquí controla el flujo del juego.")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**Semana Actual:** {semana_actual}")
    with col_info2:
        noticia_actual = NOTICIAS.get(semana_actual, "Noticias sin novedades importantes esta semana.")
        st.warning(f"**Titular de la Semana:** {noticia_actual}")

    st.subheader("Estatus de los Equipos")
    pedidos_semana = bd["pedidos"][str_semana]
    col_roles = st.columns(4)
    todos_pidieron = True
    
    for i, r in enumerate(ROLES):
        with col_roles[i]:
            if r in pedidos_semana:
                st.success(f"**{r}**\n\n📦 Envió pedido")
            else:
                st.error(f"**{r}**\n\n⏳ Pensando...")
                todos_pidieron = False

    st.divider()
    
    if todos_pidieron:
        st.success("✅ Toda la cadena ha emitido sus órdenes. El mercado está listo para avanzar.")
        if st.button(f"🚀 Avanzar a la Semana {semana_actual + 1}", type="primary", use_container_width=True):
            bd["semana"] += 1
            guardar_bd(bd)
            st.rerun()
    else:
        st.warning("Faltan decisiones en la cadena. No puedes avanzar el tiempo aún.")

    with st.expander("⚙️ Opciones de Administrador / Reiniciar"):
        st.write("Usa esto solo si se equivocaron o terminó la clase.")
        if st.button("🚨 Reiniciar Juego Completo"):
            guardar_bd({"semana": 1, "pedidos": {}})
            st.rerun()

    st.divider()
    st.subheader("📈 El Efecto Látigo en Vivo")
    
    historial = []
    for sem in range(1, semana_actual + 1):
        s = str(sem)
        fila = {"Semana": sem, "Demanda Consumidor": DEMANDA_CLIENTE[s]}
        if s in bd["pedidos"]:
            for r in ROLES:
                fila[r] = bd["pedidos"][s].get(r, 0)
        historial.append(fila)
    
    df_grafica = pd.DataFrame(historial).set_index("Semana")
    st.line_chart(df_grafica, height=400)

# --- VISTA DE LOS ALUMNOS (JUGADORES) ---
else:
    st.header(f"🏢 División: {rol}")
    
    # Noticiero para generar presión psicológica
    noticia = NOTICIAS.get(semana_actual, "")
    if noticia:
        st.error(f"📰 **BOLETÍN DEL MERCADO:** {noticia}")
    else:
        st.info("📰 **BOLETÍN:** Mercado estable. Toma tus decisiones con calma.")

    ya_pidio = rol in bd["pedidos"][str_semana]
    
    if ya_pidio:
        st.success("✅ Orden de compra enviada exitosamente al proveedor.")
        st.metric(label="Tu pedido emitido fue de:", value=f"{bd['pedidos'][str_semana][rol]} unidades")
        st.write("---")
        st.write("☕ El reloj está en pausa. Espera a que el resto de la cadena termine de analizar sus números para avanzar a la siguiente semana.")
    else:
        st.warning("⚠️ SE REQUIERE ACCIÓN: Ingresa tu orden de compra.")
        st.write("Recuerda tu objetivo logístico: Minimizar costos de inventario sin caer en desabasto.")
        
        with st.form(key=f"form_pedido_{semana_actual}"):
            st.write("### Hoja de Pedido - Semana", semana_actual)
            cantidad = st.number_input("Cantidad a solicitar a tu proveedor (cajas):", min_value=0, max_value=1000, value=0, step=1)
            
            submit = st.form_submit_button("Firmar y Enviar Orden 📝", type="primary", use_container_width=True)
            
            if submit:
                bd["pedidos"][str_semana][rol] = cantidad
                guardar_bd(bd)
                st.rerun()
