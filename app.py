import streamlit as st
import pandas as pd
import json
import os

# --- CONFIGURACIÓN DE LA BASE DE DATOS LOCAL ---
DB_FILE = "beer_game_db.json"
ROLES = ["Minorista", "Mayorista", "Distribuidor", "Fábrica"]

# Demanda oculta y Noticias
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

# --- INICIO DE LA APP Y CONFIGURACIÓN ---
st.set_page_config(page_title="Beer Game - EBC", page_icon="🍺", layout="wide")

# --- GESTIÓN DE SESIÓN (LOGIN PERSISTENTE) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.rol = None

# PANTALLA DE LOGIN Y REGLAS (Si no ha iniciado sesión)
if not st.session_state.logged_in:
    st.title("🍺 El Juego de la Cerveza: Edición EBC")
    st.markdown("*Simulador de Logística Integral y Efecto Látigo*")
    
    col_login, col_reglas = st.columns([1, 2])
    
    with col_login:
        st.subheader("🔐 Acceso de Seguridad")
        rol_input = st.selectbox("Selecciona tu División:", ["Profesor (Monitor)"] + ROLES)
        password_input = st.text_input("Ingresa tu PIN de acceso:", type="password")
        
        if st.button("Iniciar Sesión", type="primary", use_container_width=True):
            if password_input == PASSWORDS.get(rol_input):
                st.session_state.logged_in = True
                st.session_state.rol = rol_input
                st.rerun()
            else:
                st.error("⚠️ PIN incorrecto. Intenta de nuevo.")
                
    with col_reglas:
        st.info("""
        **📋 REGLAS OPERATIVAS DE LA CADENA DE SUMINISTRO:**
        
        * **Demanda Base:** Históricamente, el cliente final pide **4 cajas por semana**.
        * **Nivel de Servicio:** El objetivo de toda la cadena es cumplir con el **100% de la demanda** (Cero ventas perdidas).
        * **Política de Costos:** * 📦 Mantener inventario sobrante cuesta **$0.50** por caja a la semana. 
            * 🚫 Quedarse en desabasto (venta perdida) cuesta **$1.00** por caja.
        * **Regla de Comunicación:** Está estrictamente prohibido hablar, hacer señas o compartir pantallas con los otros eslabones de la cadena.
        """)
    st.stop() # Detiene la ejecución aquí si no están logueados

# --- SI YA INICIÓ SESIÓN (EL JUEGO) ---
rol = st.session_state.rol

bd = cargar_bd()
semana_actual = bd["semana"]
str_semana = str(semana_actual)

if str_semana not in bd["pedidos"]:
    bd["pedidos"][str_semana] = {}
    guardar_bd(bd)

# --- MENÚ LATERAL (SIDEBAR) ---
st.sidebar.success(f"👤 Conectado como: **{rol}**")
if st.sidebar.button("🚪 Cerrar Sesión"):
    st.session_state.logged_in = False
    st.session_state.rol = None
    st.rerun()

st.sidebar.divider()
st.sidebar.metric(label="📅 Semana Actual", value=semana_actual)

with st.sidebar.expander("📋 Recordatorio de Costos"):
    st.write("- **Meta:** 100% Nivel de Servicio")
    st.write("- **Costo Inventario:** $0.50/caja")
    st.write("- **Costo Desabasto:** $1.00/caja")

# --- VISTA DEL PROFESOR (MONITOR) ---
if rol == "Profesor (Monitor)":
    st.title("👑 Centro de Mando Directivo")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.info(f"**Semana Actual:** {semana_actual}")
    with col_info2:
        noticia_actual = NOTICIAS.get(semana_actual, "Sin novedades importantes esta semana.")
        st.warning(f"**Titular de la Semana:** {noticia_actual}")

    st.subheader("Estatus de los Equipos")
    pedidos_semana = bd["pedidos"][str_semana]
    col_roles = st.columns(4)
    todos_pidieron = True
    
    for i, r in enumerate(ROLES):
        with col_roles[i]:
            if r in pedidos_semana:
                st.success(f"**{r}**\n\n📦 Pidió: {pedidos_semana[r]}")
            else:
                st.error(f"**{r}**\n\n⏳ Pensando...")
                todos_pidieron = False

    st.divider()
    
    if todos_pidieron:
        st.success("✅ Toda la cadena ha emitido sus órdenes. Puedes avanzar el tiempo.")
        if st.button(f"🚀 Avanzar a la Semana {semana_actual + 1}", type="primary", use_container_width=True):
            bd["semana"] += 1
            guardar_bd(bd)
            st.rerun()
    else:
        st.warning("Faltan decisiones en la cadena. No puedes avanzar el tiempo aún.")
        if st.button("🔄 Refrescar Estatus"):
            st.rerun()

    with st.expander("⚙️ Opciones de Administrador / Reiniciar"):
        if st.button("🚨 Reiniciar Juego Completo"):
            guardar_bd({"semana": 1, "pedidos": {}})
            st.rerun()

    st.divider()
    st.subheader("📈 Análisis Financiero y Efecto Látigo")
    
    historial = []
    for sem in range(1, semana_actual + 1):
        s = str(sem)
        fila = {"Semana": sem, "Demanda Consumidor": DEMANDA_CLIENTE[s]}
        if s in bd["pedidos"]:
            for r in ROLES:
                fila[r] = bd["pedidos"][s].get(r, 0)
        historial.append(fila)
    
    df_grafica = pd.DataFrame(historial).set_index("Semana")
    
    # --- CÁLCULO DE COSTOS ESTIMADOS Y EXPLICACIÓN CLARA ---
    if not df_grafica.empty:
        total_demanda = df_grafica["Demanda Consumidor"].sum()
        total_fabrica = df_grafica["Fábrica"].sum() if "Fábrica" in df_grafica.columns else 0
        
        # Balance del sistema: Todo lo que entró (Fábrica) vs lo que salió (Demanda)
        balance = total_fabrica - total_demanda
        
        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric("Demanda Total (Salidas)", total_demanda, help="Suma acumulada de todas las cajas requeridas por el consumidor final.")
        with col_met2:
            st.metric("Producción Total (Entradas)", total_fabrica, help="Suma acumulada de todas las cajas inyectadas al sistema por la Fábrica.")
        with col_met3:
            if balance > 0:
                costo = balance * 0.50
                st.metric("Penalización Acumulada", f"${costo:.2f}", delta=f"+{balance} cajas atrapadas (Exceso)", delta_color="inverse", help="Se cobra $0.50 por cada caja sobrante.")
            elif balance < 0:
                costo = abs(balance) * 1.00
                st.metric("Penalización Acumulada", f"${costo:.2f}", delta=f"{balance} cajas faltantes (Escasez)", delta_color="inverse", help="Se cobra $1.00 por cada venta perdida.")
            else:
                st.metric("Estado de la Cadena", "Equilibrio", delta="$0.00 penalización", delta_color="normal")

        # Explicación pedagógica para la clase
        with st.expander("📖 ¿Cómo se calcula esta penalización y por qué ocurre? (Abre para explicar a la clase)"):
            st.markdown(f"""
            **La Matemática del Sistema:**
            El costo financiero no se calcula de forma aislada, sino evaluando la Cadena de Suministro como **un solo sistema**. Hasta la semana {semana_actual}:
            
            1. El mercado pidió un total de **{total_demanda} cajas**.
            2. La Fábrica inyectó al sistema un total de **{total_fabrica} cajas**.
            3. La diferencia entre lo que entra y sale es de **{balance} cajas**.
            
            **¿Por qué hay un desfase? (El Efecto Látigo)**
            Cuando el Minorista se asusta y pide de más, la información viaja con retraso (desfase de semanas). La Fábrica produce creyendo que hay una súper demanda. Como resultado, las cajas se quedan **"atrapadas"** en los almacenes intermedios (Distribuidor y Mayorista) o en los camiones de transporte.
            
            * 🔴 **Si el balance es Positivo (Exceso):** Hay {balance if balance > 0 else 0} cajas atoradas en la cadena. A un costo de mantenimiento de **$0.50** por caja, la empresa está quemando flujo de efectivo.
            * 🔴 **Si el balance es Negativo (Desabasto):** Faltaron {abs(balance) if balance < 0 else 0} cajas para surtir. A un costo de oportunidad de **$1.00** por caja, la empresa está perdiendo clientes y ventas directas.
            
            *Conclusión Logística: Si los 4 eslabones hubieran visto la demanda real del cliente desde la semana 1, la fábrica habría producido exactamente {total_demanda} cajas, la penalización sería $0.00 y la empresa sería altamente rentable.*
            """)

    st.line_chart(df_grafica, height=400)

# --- VISTA DE LOS ALUMNOS (JUGADORES) ---
else:
    st.title(f"🏢 División: {rol}")
    
    noticia = NOTICIAS.get(semana_actual, "")
    if noticia:
        st.error(f"📰 **BOLETÍN DEL MERCADO:** {noticia}")
    else:
        st.info("📰 **BOLETÍN:** Mercado estable. Toma tus decisiones con calma.")

    ya_pidio = rol in bd["pedidos"][str_semana]
    
    if ya_pidio:
        st.success("✅ Orden de compra enviada exitosamente al proveedor.")
        st.metric(label="Tu pedido emitido fue de:", value=f"{bd['pedidos'][str_semana][rol]} cajas")
        st.write("---")
        st.write("☕ El reloj está en pausa. Espera a que el resto de la cadena termine su análisis para avanzar a la siguiente semana.")
        
        if st.button("🔄 Actualizar Estatus para ver si ya avanzamos", use_container_width=True):
            st.rerun()
    else:
        st.warning("⚠️ SE REQUIERE ACCIÓN: Ingresa tu orden de compra.")
        
        with st.form(key=f"form_pedido_{semana_actual}"):
            st.write("### Hoja de Pedido - Semana", semana_actual)
            cantidad = st.number_input("Cantidad a solicitar a tu proveedor (cajas):", min_value=0, max_value=2000, value=0, step=1)
            
            submit = st.form_submit_button("Firmar y Enviar Orden 📝", type="primary", use_container_width=True)
            
            if submit:
                bd["pedidos"][str_semana][rol] = cantidad
                guardar_bd(bd)
                st.rerun()
