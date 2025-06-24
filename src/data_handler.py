import pandas as pd
from src.utils import generate_simulated_data

def load_data(source_type="simulated", file_path=r"C:\Users\Usuario\Downloads\Sales_Dashboard\data\Dataset_Prueba.xlsx"):
    """
    Carga los datos de ventas desde diferentes fuentes configurables.
    Esto permite cambiar fácilmente entre datos simulados, CSV, hardcodeados o de una base de datos.

    Args:
        source_type (str): Tipo de fuente de datos a utilizar. Puede ser:
                           'simulated': Genera datos aleatorios.
                           'csv': Carga datos desde un archivo CSV.
                           'database': (No implementado en este ejemplo) Conexión a una base de datos.
                           'hardcoded': Utiliza un pequeño conjunto de datos definidos directamente en el código.
                           'excel': Carga datos desde un archivo Excel (.xlsx).
        file_path (str): Ruta al archivo de datos si source_type es 'csv' o 'excel'.

    Returns:
        pd.DataFrame: DataFrame de Pandas con los datos de ventas cargados.
    """
    if source_type == "simulated":
        # Genera datos simulados si la fuente seleccionada es 'simulated'
        df = generate_simulated_data()
        print("Datos simulados generados.")
        return df
    elif source_type == "csv":
        try:
            # Intenta cargar datos desde un archivo CSV.
            df = pd.read_csv(file_path)
            # Asegura que la columna 'Date' sea de tipo datetime para operaciones de fecha/hora
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"Datos cargados desde {file_path}.")
            return df
        except FileNotFoundError:
            # Si el archivo CSV no se encuentra, imprime un error y genera datos simulados como fallback.
            print(f"Error: Archivo CSV no encontrado en {file_path}. Generando datos simulados como fallback.")
            return generate_simulated_data()
        except Exception as e:
            # Captura cualquier otro error durante la carga del CSV y usa datos simulados.
            print(f"Error al cargar datos desde CSV: {e}. Generando datos simulados como fallback.")
            return generate_simulated_data()
    elif source_type == "excel": # <-- Nueva opción para Excel
        try:
            # Carga datos desde un archivo Excel (.xlsx)
            # Es posible que necesites instalar 'openpyxl': pip install openpyxl
            df = pd.read_excel(file_path) 
            # Asegura que la columna 'Date' sea de tipo datetime
            df['Date'] = pd.to_datetime(df['Date'])
            print(f"Datos cargados desde {file_path}.")
            return df
        except FileNotFoundError:
            print(f"Error: Archivo Excel no encontrado en {file_path}. Generando datos simulados como fallback.")
            return generate_simulated_data()
        except ImportError:
            print("Error: La librería 'openpyxl' no está instalada. Necesaria para leer archivos .xlsx. Por favor, instala: pip install openpyxl. Generando datos simulados como fallback.")
            return generate_simulated_data()
        except Exception as e:
            print(f"Error al cargar datos desde Excel: {e}. Generando datos simulados como fallback.")
            return generate_simulated_data()
    elif source_type == "hardcoded":
        # Datos hardcodeados: un pequeño conjunto de datos de ejemplo para pruebas rápidas.
        data = {
            'Date': pd.to_datetime(['2016-04-01', '2016-04-05', '2016-04-10', '2016-04-15', '2016-04-20', '2016-04-25']),
            'Product': ['Product 1', 'Product 2', 'Product 1', 'Product 1', 'Product 2', 'Product 1'],
            'License_Type': ['License', 'Maintenance Renewal', 'License', 'License', 'License', 'Maintenance Renewal'],
            'Region': ['UK', 'NO', 'GR', 'UK', 'IT', 'SP'],
            'City': ['London', 'Oslo', 'Athens', 'Manchester', 'Rome', 'Madrid'], # Añadir columna City
            'Company': ['Company A', 'Company B', 'Company C', 'Company D', 'Company E', 'Company F'],
            'Amount': [1500, 2000, 500, 1200, 800, 2500],
            'Transactions': [1, 1, 1, 1, 1, 1],
            'Active_Clients': [1, 1, 1, 1, 1, 1],
            'Sales_Manager': ['Vendedor_1', 'Vendedor_2', 'Vendedor_3', 'Vendedor_1', 'Vendedor_2', 'Vendedor_3'], # Añadir columna Sales_Manager
            'Admins': [5, 2, 0, 3, 1, 4],
            'Designers': [3, 1, 0, 2, 0, 2],
            'Servers': [1, 0, 0, 1, 0, 1],
        }
        df = pd.DataFrame(data) # Crea un DataFrame a partir de los datos definidos
        print("Datos hardcodeados cargados.")
        return df
    elif source_type == "database":
        # Este bloque está reservado para la lógica de carga desde una base de datos.
        print("Carga desde base de datos no implementada en este ejemplo. Generando datos simulados como fallback.")
        return generate_simulated_data()
    else:
        print("Tipo de fuente de datos no válido. Generando datos simulados.")
        return generate_simulated_data()
