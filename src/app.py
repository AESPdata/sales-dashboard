import streamlit as st # Importa la librería principal de Streamlit
import pandas as pd # Importa Pandas para manipulación de datos
import datetime # Importa datetime para manejar fechas

# Importa las funciones personalizadas desde los módulos locales
from src.data_handler import load_data 
# Importa todas las funciones de utilidad y trazado
from src.utils import calculate_qtd_metrics, get_last_n_orders, calculate_country_performance, get_quarterly_data, get_running_totals_by_week, get_seller_performance_data, get_available_quarters, calculate_city_performance, get_seller_performance_over_time_data
from src.plots import plot_running_totals, plot_quarterly_metrics, plot_country_performance, plot_seller_performance, plot_city_performance, plot_seller_performance_over_time

# --- Configuración de la página de Streamlit ---
# Configura el layout de la página como 'wide' para aprovechar el ancho completo
# y el título de la página que aparece en la pestaña del navegador.
st.set_page_config(layout="wide", page_title="Reporte de Ventas de Licencias de Software")

# --- Título Principal del Dashboard ---
# Muestra el título principal del reporte en la parte superior de la aplicación.
st.title("REPORTE DE VENTAS DE LICENCIAS DE SOFTWARE") 

# --- Barra lateral para controles y filtros ---
st.sidebar.header("Opciones de Datos") # Encabezado para la sección de opciones de datos
data_source = st.sidebar.selectbox(
    "Seleccionar fuente de datos:", # Etiqueta para el selector
    ("simulated", "csv", "excel", "hardcoded", "database"),
    help="Elige de dónde cargar los datos de ventas. 'simulated' generará datos aleatorios." # Texto de ayuda
)

# Carga los datos utilizando la función load_data del data_handler.
# El tipo de fuente de datos se selecciona desde la barra lateral.
df_sales = load_data(source_type=data_source) 

# Asegurarse de que la columna 'Date' es de tipo datetime para operaciones de filtrado y análisis
df_sales['Date'] = pd.to_datetime(df_sales['Date'])

# --- Filtros Globales ---
st.sidebar.header("Filtros Globales") # Encabezado para la sección de filtros

# Filtro por Producto (Partner)
product_filter = st.sidebar.radio(
    "Producto (Partner):", # Etiqueta del filtro 
    ("Product 1", "Product 2") # Opciones de productos (mantener nombres originales si son identificadores de producto)
)

# Filtro por Tipo de Licencia o Renovación (License or MR)
license_type_filter = st.sidebar.radio(
    "Tipo de Licencia o Renovación:", # Etiqueta del filtro
    ("(Todos)", "Licencia", "Renovación") 
)
# Ajustar el valor de filtro si se selecciona la opción traducida
if license_type_filter == "Licencia":
    internal_license_type_filter = "License"
elif license_type_filter == "Renovación":
    internal_license_type_filter = "Maintenance Renewal"
else:
    internal_license_type_filter = "(Todos)"

# Filtro por Región
# Obtiene las regiones únicas del DataFrame y añade "Todos" como opción para seleccionar todas.
regions = ["Todos"] + sorted(df_sales['Region'].unique().tolist())
region_filter = st.sidebar.selectbox(
    "Región:", # Etiqueta del filtro 
    regions # Lista de regiones disponibles
)
# Ajustar el valor de filtro si se selecciona la opción traducida
if region_filter == "Todos":
    internal_region_filter = "All"
else:
    internal_region_filter = region_filter


# --- Aplicar Filtros Globales ---
filtered_df = df_sales[df_sales['Product'] == product_filter].copy() # Filtrar por producto

if internal_license_type_filter != "(Todos)":
    filtered_df = filtered_df[filtered_df['License_Type'] == internal_license_type_filter].copy()

if internal_region_filter != "All":
    filtered_df = filtered_df[filtered_df['Region'] == internal_region_filter].copy()


# --- Selector de Períodos para KPIs y Running Totals ---
st.sidebar.header("Períodos para KPIs y Gráficos") 
all_available_quarters = get_available_quarters(filtered_df)

# Por defecto, selecciona los últimos 4 trimestres si existen
default_selected_quarters = []
if len(all_available_quarters) >= 4:
    default_selected_quarters = all_available_quarters[-4:]
elif len(all_available_quarters) > 0:
    default_selected_quarters = all_available_quarters # Si hay menos de 4, selecciona todos

selected_quarters = st.sidebar.multiselect(
    "Seleccionar Trimestres a Visualizar:",
    options=all_available_quarters,
    default=default_selected_quarters,
    help="Selecciona uno o más trimestres para ver sus métricas y el gráfico de totales acumulados." # Texto de ayuda 
)

# Encontrar el "trimestre actual" para el cálculo de KPIs (el último trimestre seleccionado o el último disponible si no se seleccionó nada)
current_analysis_quarter_label = None
current_analysis_date = None

if selected_quarters:
    # Si hay trimestres seleccionados, tomamos el último de ellos para el KPI "actual"
    current_analysis_quarter_label = sorted(selected_quarters)[-1]
    # Intentamos obtener la fecha de fin del trimestre para calculate_qtd_metrics
    year = int(current_analysis_quarter_label[:4])
    q_num = int(current_analysis_quarter_label[5])
    
    if q_num == 1:
        # Convertir a Timestamp para asegurar la compatibilidad de tipos
        current_analysis_date = pd.Timestamp(year, 3, 31) 
    elif q_num == 2:
        current_analysis_date = pd.Timestamp(year, 6, 30)
    elif q_num == 3:
        current_analysis_date = pd.Timestamp(year, 9, 30)
    else: # Q4
        current_analysis_date = pd.Timestamp(year, 12, 31)
else:
    # Si no hay trimestres seleccionados, usamos el último trimestre disponible en los datos filtrados
    if all_available_quarters:
        last_available_quarter = all_available_quarters[-1]
        year = int(last_available_quarter[:4])
        q_num = int(last_available_quarter[5])
        if q_num == 1:
            current_analysis_date = pd.Timestamp(year, 3, 31)
        elif q_num == 2:
            current_analysis_date = pd.Timestamp(year, 6, 30)
        elif q_num == 3:
            current_analysis_date = pd.Timestamp(year, 9, 30)
        else: # Q4
            current_analysis_date = pd.Timestamp(year, 12, 31)
    else:
        # Fallback a la fecha actual si no hay datos disponibles en absoluto
        current_analysis_date = pd.Timestamp(datetime.date.today()) 

# --- Layout del Dashboard: Columnas Principales ---
col1, col2 = st.columns([0.7, 0.3]) 

with col1:
    # --- Sección de Métricas Clave (KPIs) ---
    st.subheader(f"Métricas Clave para {current_analysis_quarter_label if current_analysis_quarter_label else 'Período Seleccionado'}") # El ultimo trimestre
    
    # Filtrar el df para calcular los KPIs solo para el trimestre seleccionado como "actual"
    kpi_df_for_calc = filtered_df
    if current_analysis_date:
        kpi_current_year = current_analysis_date.year
        kpi_current_quarter_num = (current_analysis_date.month - 1) // 3 + 1
        
        if kpi_current_quarter_num == 1:
            # Convertir a Timestamp para asegurar la compatibilidad de tipos
            kpi_qtd_start = pd.Timestamp(f'{kpi_current_year}-01-01')
        elif kpi_current_quarter_num == 2:
            kpi_qtd_start = pd.Timestamp(f'{kpi_current_year}-04-01')
        elif kpi_current_quarter_num == 3:
            kpi_qtd_start = pd.Timestamp(f'{kpi_current_year}-07-01')
        else: # Q4
            kpi_qtd_start = pd.Timestamp(f'{kpi_current_year}-10-01')
        
        # Filtrar solo las transacciones del trimestre de current_analysis_date hasta esa fecha
        # Ambas variables (filtered_df['Date'] y kpi_qtd_start/current_analysis_date) son ahora Timestamps.
        kpi_df_for_calc = filtered_df[(filtered_df['Date'] >= kpi_qtd_start) & (filtered_df['Date'] <= current_analysis_date)].copy()
    
    # Pasar current_analysis_date como objeto date, ya que calculate_qtd_metrics lo convierte a pd.Timestamp internamente
    # No es necesario convertirlo aquí, la función ya lo maneja.
    qtd_metrics = calculate_qtd_metrics(kpi_df_for_calc, current_analysis_date.date())

    st.markdown("---") # Separador visual

    # Mostrar métricas en formato de columnas
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.metric(label="Días Restantes del Trimestre", value=qtd_metrics["Days Left EOQ"]) 
    with kpi_col2:
        st.metric(label="Transacciones Trimestrales (QTD)", value=qtd_metrics["QTD Transactions"]) 
    with kpi_col3:
        st.metric(label="Clientes Activos Trimestre (QTD)", value=qtd_metrics["QTD Active Clients"])
    with kpi_col4:
        st.metric(label="Gerentes de Venta Únicos (QTD)", value=qtd_metrics["QTD SAMs"])

    kpi_col1_2, kpi_col2_2, kpi_col3_2, kpi_col4_2 = st.columns(4)
    with kpi_col1_2:
        st.metric(label="Ventas del Trimestre (QTD)", value=f"${qtd_metrics['QTD Sales']:,}")
    with kpi_col2_2:
        st.metric(label="Administradores", value=qtd_metrics["Admins"])
    with kpi_col3_2:
        st.metric(label="Diseñadores", value=qtd_metrics["Designers"])
    with kpi_col4_2:
        st.metric(label="Servidores", value=qtd_metrics["Servers"])
    st.markdown("---") # Otro separador visual

    # --- Gráfico de Índice (Running Totals) ---
    st.subheader("Totales Acumulados") 
    # Pasa los trimestres seleccionados a la función de trazado
    if selected_quarters:
        df_running_totals = get_running_totals_by_week(filtered_df, selected_quarters)
        plot_running_totals(df_running_totals, selected_quarters)
    else:
        st.info("Por favor, selecciona al menos un trimestre para visualizar los Totales Acumulados.")


with col2:
    # --- Sección de Últimas 5 Órdenes ---
    st.subheader("Últimas 5 Órdenes")
    last_orders_df = get_last_n_orders(filtered_df)
    if not last_orders_df.empty:
        last_orders_df['Amount'] = last_orders_df['Amount'].apply(lambda x: f"$ {x:,.0f}")
        # Renombra las columnas para la tabla si es necesario
        st.table(last_orders_df.rename(columns={'Company': 'Empresa', 'Amount': 'Monto'})) 
    else:
        st.info("No hay órdenes recientes para mostrar con los filtros seleccionados.") 

    st.markdown("---") # Separador visual

    # --- Sección de Rendimiento por País/Ciudad ---
    st.subheader("Rendimiento por Ubicación") # Nuevo subtítulo más general
    
    # Selector para alternar entre vista por país y por ciudad
    location_view_mode = st.radio(
        "Ver rendimiento por:", 
        ("País", "Ciudad") # Opciones traducidas
    )

    if location_view_mode == "País":
        country_performance_df = calculate_country_performance(filtered_df)
        if not country_performance_df.empty:
            plot_country_performance(country_performance_df)
        else:
            st.info("No hay datos de rendimiento por país para mostrar con los filtros seleccionados.") # Mensaje traducido
    else: # "Ciudad"
        city_performance_df = calculate_city_performance(filtered_df)
        if not city_performance_df.empty:
            plot_city_performance(city_performance_df)
        else:
            st.info("No hay datos de rendimiento por ciudad para mostrar con los filtros seleccionados.") # Mensaje traducido


# --- Gráfico de Métricas Trimestrales Detalladas ---
st.subheader("Métricas Trimestrales") 
quarterly_metrics_df = get_quarterly_data(filtered_df)
if selected_quarters:
    plot_quarterly_metrics(quarterly_metrics_df, selected_quarters)
else:
    st.info("Por favor, selecciona al menos un trimestre para visualizar las Métricas Trimestrales.") # Mensaje traducido

# --- Nuevo Gráfico: Desempeño de Vendedores ---
st.subheader("Desempeño de Ventas por Gerente de Ventas") 

# Selector para tipo de visualización de vendedores
seller_view_mode = st.radio(
    "Ver desempeño de vendedor por:", 
    ("Agregado por País/Producto/Tipo de Venta", "A lo Largo del Tiempo") 
)

if seller_view_mode == "Agregado por País/Producto/Tipo de Venta":
    seller_performance_df = get_seller_performance_data(filtered_df)
    if not seller_performance_df.empty:
        plot_seller_performance(seller_performance_df)
    else:
        st.info("No hay datos de desempeño de vendedores para mostrar con los filtros seleccionados.") 
else: # "A lo Largo del Tiempo"
    # Selector para la granularidad temporal (Mes o Trimestre)
    time_granularity = st.selectbox(
        "Granularidad de tiempo:",
        ("Trimestre", "Mes"), 
        help="Elige si ver el desempeño por mes o por trimestre." # Texto de ayuda
    )
    
    # Ajustar el valor interno de la granularidad
    internal_time_granularity = 'quarter' if time_granularity == 'Trimestre' else 'month'

    seller_time_performance_df = get_seller_performance_over_time_data(filtered_df, internal_time_granularity)
    if not seller_time_performance_df.empty:
        plot_seller_performance_over_time(seller_time_performance_df, internal_time_granularity)
    else:
        st.info("No hay datos de desempeño de vendedores en el tiempo para mostrar con los filtros seleccionados.")

# --- Nota al pie de página sobre la conversión de moneda ---
st.markdown("""
    <small>Los montos se muestran como dinero entregado a los proveedores. Para el Producto 1 se muestra en USD; para el Producto 2 en GBP (Libras Esterlinas). Los montos en EUR para los países europeos se convierten a una tasa de 1.35.</small>
""", unsafe_allow_html=True) # Permite renderizar HTML en el markdown
