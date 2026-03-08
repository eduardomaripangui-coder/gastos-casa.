import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Gastos Casa 2026", layout="centered")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer datos existentes de la hoja
try:
    df = conn.read()
except:
    # Si la hoja está vacía, crear estructura básica
    df = pd.DataFrame(columns=["Fecha", "Servicio", "Monto", "Pagador", "Eduardo_Debe", "Andre_Debe", "Mario_Debe", "Estado"])

st.title("🏠 Nuestra Casa: Eduardo, Andre y Mario")
st.markdown("---")

# Menú lateral
menu = ["📈 Ver Resumen y Deudas", "➕ Registrar Nuevo Gasto"]
choice = st.sidebar.radio("Navegación", menu)

if choice == "➕ Registrar Nuevo Gasto":
    st.subheader("Registrar Movimiento Histórico")
    st.info("Formato de monto: Digita 1072 para registrar 10.72")
    
    with st.form("nuevo_gasto"):
        fecha = st.text_input("Fecha (dd/mm/yy)", value=datetime.now().strftime("%d/%m/%y"))
        servicio = st.text_input("Servicio (Luz, Agua, Gas, etc.)")
        monto_raw = st.text_input("Monto (sin puntos ni comas)")
        pagador = st.selectbox("¿Quién pagó?", ["Eduardo", "Andre", "Mario"])
        
        submit = st.form_submit_button("Guardar en la Nube")
        
        if submit:
            if not monto_raw or not servicio:
                st.error("Por favor completa el servicio y el monto.")
            else:
                try:
                    # Lógica de decimales automáticos (1072 -> 10.72)
                    monto = float(monto_raw) / 100
                    
                    # Cálculos de cuotas (40%, 40%, 20%)
                    e_d = monto * 0.40 if pagador != "Eduardo" else 0
                    a_d = monto * 0.40 if pagador != "Andre" else 0
                    m_d = monto * 0.20 if pagador != "Mario" else 0
                    
                    # Crear nueva fila
                    nueva_fila = pd.DataFrame([{
                        "Fecha": fecha,
                        "Servicio": servicio,
                        "Monto": monto,
                        "Pagador": pagador,
                        "Eduardo_Debe": e_d,
                        "Andre_Debe": a_d,
                        "Mario_Debe": m_d,
                        "Estado": "Pendiente"
                    }])
                    
                    # Actualizar Google Sheets
                    df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(data=df_actualizado)
                    st.success(f"✅ Registrado: {servicio} por ${monto:,.2f}")
                except ValueError:
                    st.error("El monto debe ser solo números.")

elif choice == "📈 Ver Resumen y Deudas":
    st.subheader("Estado de Cuentas")
    
    if not df.empty:
        # Mostrar tabla de historial
        st.dataframe(df.style.format({"Monto": "{:.2f}", "Eduardo_Debe": "{:.2f}", "Andre_Debe": "{:.2f}", "Mario_Debe": "{:.2f}"}))
        
        st.divider()
        
        # Totales acumulados
        st.subheader("📉 Deudas Pendientes Totales")
        c1, c2, c3 = st.columns(3)
        
        total_e = df["Eduardo_Debe"].sum()
        total_a = df["Andre_Debe"].sum()
        total_m = df["Mario_Debe"].sum()
        
        c1.metric("Eduardo Debe", f"${total_e:,.2f}")
        c2.metric("Andre Debe", f"${total_a:,.2f}")
        c3.metric("Mario Debe", f"${total_m:,.2f}")
    else:
        st.warning("Aún no hay datos registrados en el Excel.")
