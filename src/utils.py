import pandas as pd
import numpy as np
import datetime

def generate_simulated_data(num_records=1000):
    """
    Genera datos de ventas simulados para el dashboard.
    Estos datos permiten probar el dashboard sin necesidad de una fuente de datos real.

    Args:
        num_records (int): Número de registros de ventas a generar.

    Returns:
        pd.DataFrame: DataFrame con datos de ventas simulados.
    """
    np.random.seed(42) # Se establece una semilla para que los datos sean reproducibles

    # Fechas simuladas que abarcan varios trimestres, similar a la imagen de referencia (2012-2016 Q2)
    start_date = datetime.date(2012, 1, 1)
    end_date = datetime.date(2016, 6, 15) # Hasta el segundo trimestre de 2016
    
    # Genera fechas aleatorias dentro del rango especificado
    dates = pd.to_datetime([start_date + datetime.timedelta(days=np.random.randint(0, (end_date - start_date).days)) for _ in range(num_records)])

    # Listas de valores posibles para las columnas categóricas
    products = ['Product 1', 'Product 2']
    license_types = ['License', 'Maintenance Renewal']
    regions = ['UK', 'NO', 'GR', 'IT', 'SP', 'LU', 'US', 'CA', 'DE', 'FR'] # Añadimos más regiones
    companies = [f'Company {i}' for i in range(1, 21)] # 20 empresas para tener variedad en las órdenes
    sales_managers = [f'Vendedor_{i}' for i in range(1, 16)] # 15 Vendedores distintos (traducido)

    # Definir algunas ciudades por región para simular datos más realistas
    region_cities = {
        'UK': ['London', 'Manchester', 'Edinburgh'],
        'NO': ['Oslo', 'Bergen'],
        'GR': ['Athens', 'Thessaloniki'],
        'IT': ['Rome', 'Milan', 'Naples'],
        'SP': ['Madrid', 'Barcelona', 'Seville'],
        'LU': ['Luxembourg City'],
        'US': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
        'CA': ['Toronto', 'Vancouver', 'Montreal'],
        'DE': ['Berlin', 'Munich', 'Hamburg'],
        'FR': ['Paris', 'Marseille', 'Lyon']
    }
    
    # Crear una lista de ciudades basada en las regiones seleccionadas aleatoriamente
    cities = [np.random.choice(region_cities[region]) for region in np.random.choice(regions, num_records, p=[0.15, 0.12, 0.08, 0.08, 0.07, 0.05, 0.15, 0.1, 0.1, 0.1])]


    # Creación del diccionario de datos con valores aleatorios
    data = {
        'Date': dates, # Fechas de las transacciones
        'Product': np.random.choice(products, num_records), # Producto asociado a la venta
        'License_Type': np.random.choice(license_types, num_records), # Tipo de licencia (nueva o renovación)
        'Region': np.random.choice(regions, num_records, p=[0.15, 0.12, 0.08, 0.08, 0.07, 0.05, 0.15, 0.1, 0.1, 0.1]), # Región con distribución de probabilidad
        'City': cities, # Ciudad de la transacción
        'Company': np.random.choice(companies, num_records), # Empresa que realizó la compra
        'Amount': np.random.randint(100, 5000, num_records), # Monto de la venta
        'Transactions': np.random.randint(1, 5, num_records), # Número de transacciones por venta (simulado)
        'Active_Clients': np.random.randint(0, 2, num_records), # 1 si el cliente se considera activo, 0 si no
        'Sales_Manager': np.random.choice(sales_managers, num_records), # Vendedor asignado a la transacción
        'Admins': np.random.randint(0, 10, num_records), # Cantidad de licencias de administradores vendidas
        'Designers': np.random.randint(0, 8, num_records), # Cantidad de licencias de diseñadores vendidas
        'Servers': np.random.randint(0, 5, num_records), # Cantidad de licencias de servidores vendidas
    }

    df = pd.DataFrame(data) # Crea un DataFrame de Pandas a partir del diccionario de datos

    return df

def calculate_qtd_metrics(df, current_date):
    """
    Calcula las métricas QTD (Quarter To Date - Del inicio del trimestre hasta la fecha actual)
    a partir del DataFrame de ventas.

    Args:
        df (pd.DataFrame): DataFrame de ventas filtrado.
        current_date (datetime.date): Fecha actual para calcular el QTD.

    Returns:
        dict: Un diccionario con las métricas QTD calculadas.
    """
    # Convertir la fecha actual a formato datetime para una comparación precisa
    current_datetime = pd.to_datetime(current_date)

    # Determinar el inicio del trimestre actual basado en la fecha actual
    current_year = current_datetime.year
    current_quarter_num = (current_datetime.month - 1) // 3 + 1 # 1 para Q1, 2 para Q2, etc.
    
    # Definir el inicio y fin del trimestre actual
    if current_quarter_num == 1:
        qtd_start = pd.to_datetime(f'{current_year}-01-01')
        qtd_end = pd.to_datetime(f'{current_year}-03-31')
    elif current_quarter_num == 2:
        qtd_start = pd.to_datetime(f'{current_year}-04-01')
        qtd_end = pd.to_datetime(f'{current_year}-06-30')
    elif current_quarter_num == 3:
        qtd_start = pd.to_datetime(f'{current_year}-07-01')
        qtd_end = pd.to_datetime(f'{current_year}-09-30')
    else: # Cuarto trimestre (Q4)
        qtd_start = pd.to_datetime(f'{current_year}-10-01')
        qtd_end = pd.to_datetime(f'{current_year}-12-31')

    # Filtrar el DataFrame para incluir solo las transacciones dentro del trimestre actual
    # y hasta la fecha actual de análisis
    qtd_df = df[(df['Date'] >= qtd_start) & (df['Date'] <= current_datetime)].copy()

    # Calcular Días restantes para fin de trimestre (EOQ - End Of Quarter)
    # Si la fecha actual es anterior al fin del trimestre, calcula los días restantes.
    days_left_eoq = (qtd_end.date() - current_date).days if current_date <= qtd_end.date() else 0

    # Calcular las métricas QTD sumando o contando valores únicos
    qtd_transactions = qtd_df['Transactions'].sum() if not qtd_df.empty else 0
    qtd_active_clients = qtd_df['Company'].nunique() if not qtd_df.empty else 0 # Clientes únicos que han realizado transacciones
    # Modificado: SAMs ahora se refiere a los Sales_Manager únicos que han realizado ventas en el QTD
    qtd_sams = qtd_df['Sales_Manager'].nunique() if not qtd_df.empty else 0 
    qtd_sales = qtd_df['Amount'].sum() if not qtd_df.empty else 0

    # Licencias vendidas por tipo (suma directa de las columnas respectivas)
    admins_licenses = qtd_df['Admins'].sum() if not qtd_df.empty else 0
    designers_licenses = qtd_df['Designers'].sum() if not qtd_df.empty else 0
    servers_licenses = qtd_df['Servers'].sum() if not qtd_df.empty else 0

    return {
        "Days Left EOQ": days_left_eoq,
        "QTD Transactions": qtd_transactions,
        "QTD Active Clients": qtd_active_clients,
        "QTD SAMs": qtd_sams, # Ahora muestra el conteo de SAMs únicos
        "QTD Sales": qtd_sales,
        "Admins": admins_licenses,
        "Designers": designers_licenses,
        "Servers": servers_licenses
    }

def get_last_n_orders(df, n=5):
    """
    Obtiene las últimas N órdenes (transacciones) del DataFrame de ventas,
    ordenadas por fecha de forma descendente.

    Args:
        df (pd.DataFrame): DataFrame de ventas.
        n (int): Número de órdenes más recientes a retornar.

    Returns:
        pd.DataFrame: DataFrame con las últimas N órdenes, incluyendo
                      'Company' (empresa) y 'Amount' (monto).
    """
    # Asegurarse de que la columna 'Date' es de tipo datetime y ordenar por fecha descendente
    df['Date'] = pd.to_datetime(df['Date'])
    last_orders = df.sort_values(by='Date', ascending=False).head(n)
    
    # Seleccionar solo las columnas relevantes para la visualización de órdenes
    return last_orders[['Company', 'Amount']]

def calculate_country_performance(df):
    """
    Calcula el rendimiento de ventas (monto total) por cada país o región.

    Args:
        df (pd.DataFrame): DataFrame de ventas.

    Returns:
        pd.DataFrame: DataFrame con el total de ventas por país, ordenado de mayor a menor monto.
                      Incluye una columna 'Formatted_Amount' para una visualización amigable.
    """
    # Agrupa el DataFrame por 'Region' (región) y suma el 'Amount' (monto) para cada una
    country_perf = df.groupby('Region')['Amount'].sum().reset_index()
    country_perf = country_perf.sort_values(by='Amount', ascending=False) # Ordena de mayor a menor venta
    
    # Formatear montos para una mejor visualización (ej. $451K en lugar de 451000)
    country_perf['Formatted_Amount'] = country_perf['Amount'].apply(
        lambda x: f"${x/1000:.0f}K" if x >= 1000 and x < 1000000 else (
                  f"${x/1000000:.1f}M" if x >= 1000000 else f"${x:,.0f}" # .1f para M
        )
    )
    return country_perf

def calculate_city_performance(df):
    """
    Calcula el rendimiento de ventas (monto total) por cada ciudad.

    Args:
        df (pd.DataFrame): DataFrame de ventas.

    Returns:
        pd.DataFrame: DataFrame con el total de ventas por ciudad, ordenado de mayor a menor monto.
                      Incluye una columna 'Formatted_Amount' para una visualización amigable.
    """
    # Agrupa el DataFrame por 'City' y suma el 'Amount' para cada una
    city_perf = df.groupby('City')['Amount'].sum().reset_index()
    city_perf = city_perf.sort_values(by='Amount', ascending=False) # Ordena de mayor a menor venta
    
    # Formatear montos para una mejor visualización
    city_perf['Formatted_Amount'] = city_perf['Amount'].apply(
        lambda x: f"${x/1000:.0f}K" if x >= 1000 and x < 1000000 else (
                  f"${x/1000000:.1f}M" if x >= 1000000 else f"${x:,.0f}"
        )
    )
    return city_perf

def get_quarterly_data(df):
    """
    Prepara los datos para los gráficos de métricas trimestrales.
    Agrupa los datos por trimestre y calcula métricas relevantes como suma de ventas,
    transacciones, clientes activos, SAMs, y licencias por tipo.

    Args:
        df (pd.DataFrame): DataFrame de ventas.

    Returns:
        pd.DataFrame: DataFrame con métricas agregadas por trimestre.
    """
    # Asegurarse de que 'Date' sea de tipo datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Crear una columna de trimestre (ej. '2016Q2') a partir de la fecha
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    
    # Agrupar por trimestre y calcular las métricas sumando o contando valores únicos
    quarterly_metrics = df.groupby('Quarter').agg(
        Amount=('Amount', 'sum'), # Suma total de ventas por trimestre
        Transactions=('Transactions', 'sum'), # Suma total de transacciones por trimestre
        Active_Clients=('Company', 'nunique'), # Conteo de clientes únicos por trimestre
        SAMs=('Sales_Manager', 'nunique'), # Conteo de Sales Managers únicos que tuvieron ventas
        Admins=('Admins', 'sum'), # Suma de licencias de Admins
        Designers=('Designers', 'sum'), # Suma de licencias de Designers
        Servers=('Servers', 'sum') # Suma de licencias de Servers
    ).reset_index() # Resetea el índice para que 'Quarter' sea una columna normal
    
    # Ordenar el DataFrame por año y número de trimestre para asegurar la secuencia correcta en los gráficos
    quarterly_metrics['Year'] = quarterly_metrics['Quarter'].apply(lambda x: int(x[:4]))
    quarterly_metrics['Q_Num'] = quarterly_metrics['Quarter'].apply(lambda x: int(x[5]))
    quarterly_metrics = quarterly_metrics.sort_values(by=['Year', 'Q_Num']).drop(columns=['Year', 'Q_Num'])
    
    return quarterly_metrics

def get_running_totals_by_week(df, selected_quarters_labels):
    """
    Calcula las ventas acumuladas semanales para los trimestres seleccionados.
    
    Args:
        df (pd.DataFrame): DataFrame de ventas.
        selected_quarters_labels (list): Lista de etiquetas de trimestre (ej. ['2016Q1', '2016Q2']) a visualizar.

    Returns:
        pd.DataFrame: DataFrame con las ventas acumuladas por semana y trimestre para los trimestres seleccionados.
                      Incluye una columna 'Comparison_Type' para el resaltado.
    """
    df['Date'] = pd.to_datetime(df['Date']) # Asegurarse de que 'Date' sea de tipo datetime
    df['Quarter'] = df['Date'].dt.to_period('Q')
    
    quarter_weeks_data = []

    # Filtrar el DataFrame original para incluir solo los trimestres seleccionados
    df_filtered_by_quarters = df[df['Quarter'].astype(str).isin(selected_quarters_labels)].copy()

    # Itera sobre cada trimestre seleccionado para calcular las ventas acumuladas por semana
    for quarter, quarter_df in df_filtered_by_quarters.groupby('Quarter'):
        if quarter_df.empty:
            continue

        quarter_start_date = quarter.start_time
        quarter_df['Days_Since_Q_Start'] = (quarter_df['Date'] - quarter_start_date).dt.days
        quarter_df['Week_Number'] = (quarter_df['Days_Since_Q_Start'] // 7) + 1
        quarter_df = quarter_df[quarter_df['Week_Number'] <= 14] # Limitar a 14 semanas por trimestre
        
        weekly_sales = quarter_df.groupby('Week_Number')['Amount'].sum().reset_index()
        weekly_sales['Running_Total'] = weekly_sales['Amount'].cumsum()
        weekly_sales['Quarter_Label'] = str(quarter)
        
        quarter_weeks_data.append(weekly_sales)
        
    if not quarter_weeks_data:
        return pd.DataFrame()

    running_totals_df = pd.concat(quarter_weeks_data)
    
    # Asignar un 'Comparison_Type' genérico para diferenciar en el gráfico si se desea,
    # o simplemente usar Quarter_Label como color.
    running_totals_df['Comparison_Type'] = 'Selected' 
    
    return running_totals_df


def get_seller_performance_data(df):
    """
    Agrega los datos de ventas para mostrar el desempeño de los vendedores
    por país, producto y tipo de venta.

    Args:
        df (pd.DataFrame): DataFrame de ventas filtrado.

    Returns:
        pd.DataFrame: DataFrame agregado con las ventas totales por Sales_Manager,
                      Region, Product y License_Type.
    """
    # Agrupar por las dimensiones clave y sumar el monto de ventas
    seller_perf_df = df.groupby(['Sales_Manager', 'Region', 'Product', 'License_Type'])['Amount'].sum().reset_index()
    
    # Ordenar por el monto de ventas para que el gráfico sea más fácil de leer
    seller_perf_df = seller_perf_df.sort_values(by='Amount', ascending=False)
    
    return seller_perf_df

def get_seller_performance_over_time_data(df, time_granularity='quarter'):
    """
    Agrega los datos de ventas para mostrar el desempeño de los vendedores a lo largo del tiempo.

    Args:
        df (pd.DataFrame): DataFrame de ventas filtrado.
        time_granularity (str): 'month' o 'quarter' para la agregación temporal.

    Returns:
        pd.DataFrame: DataFrame agregado con las ventas totales por Sales_Manager y periodo.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    
    if time_granularity == 'month':
        df['Period'] = df['Date'].dt.to_period('M').astype(str)
    else: # default to 'quarter'
        df['Period'] = df['Date'].dt.to_period('Q').astype(str)

    # Agrupar por Sales_Manager y Period, y sumar el monto
    seller_time_perf_df = df.groupby(['Sales_Manager', 'Period'])['Amount'].sum().reset_index()
    
    # Ordenar por periodo para una visualización correcta de la serie temporal
    seller_time_perf_df['Sort_Period'] = seller_time_perf_df['Period'].astype('period[Q]') if time_granularity == 'quarter' else seller_time_perf_df['Period'].astype('period[M]')
    seller_time_perf_df = seller_time_perf_df.sort_values(by=['Sales_Manager', 'Sort_Period']).drop(columns='Sort_Period')
    
    return seller_time_perf_df


def get_available_quarters(df):
    """
    Obtiene una lista de todos los trimestres únicos presentes en el DataFrame de ventas,
    ordenados cronológicamente.

    Args:
        df (pd.DataFrame): DataFrame de ventas.

    Returns:
        list: Lista de strings de trimestres (ej. ['2012Q1', '2012Q2', ...]).
    """
    if df.empty:
        return []
    
    df['Date'] = pd.to_datetime(df['Date'])
    # Convertir a periodo trimestral y luego a string, obtener únicos y ordenar
    quarters = df['Date'].dt.to_period('Q').astype(str).unique().tolist()
    
    # Ordenar los trimestres cronológicamente
    # Convertir a PeriodDtype para una ordenación correcta y luego de nuevo a string
    sorted_quarters = pd.Series(quarters).astype('period[Q]').sort_values().astype(str).tolist()
    
    return sorted_quarters