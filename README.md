# Dashboard Ejecutivo de Ventas de Licencias de Software

Este proyecto implementa un dashboard interactivo de ventas de licencias de software utilizando Streamlit. Permite a los usuarios visualizar el desempeño de las ventas por trimestre, comparar con períodos anteriores, filtrar por producto y región, y analizar métricas clave.

## Características:
- Métricas clave destacadas (Días restantes EOQ, Transacciones QTD, Clientes Activos QTD, SAMs QTD, Ventas QTD, Licencias vendidas por tipo).
- Gráfico de índice para comparación de ventas acumuladas trimestrales.
- Gráfico de barras para métricas trimestrales detalladas.
- Filtros interactivos por producto, tipo de licencia/renovación y región.
- Lista de las últimas 5 órdenes.
- Rendimiento por país.
- Soporte para datos simulados, hardcodeados o cargados desde una base de datos/CSV.

## Estructura del Proyecto:
sales_dashboard/
├── .venv/                   # Entorno virtual
├── data/                    # Directorio para archivos de datos (ej. sales_data.csv)
│   └── sales_data.csv
├── src/                     # Código fuente del dashboard
│   ├── init.py
│   ├── app.py               # Archivo principal de la aplicación Streamlit
│   ├── data_handler.py      # Módulo para el manejo y carga de datos
│   ├── plots.py             # Módulo para funciones de gráficos
│   └── utils.py             # Módulo para funciones de utilidad (ej. simulación de datos)
├── requirements.txt         # Dependencias del proyecto
├── README.md                # Este archivo
## Configuración y Ejecución:

1.  **Clonar el repositorio (si aplica) o crear la estructura de archivos.**
2.  **Navegar al directorio del proyecto:**
    ```bash
    cd sales_dashboard
    ```
3.  **Crear y activar el entorno virtual:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```
4.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **Ejecutar el dashboard:**
    ```bash
    streamlit run src/app.py
    ```

El dashboard se abrirá automáticamente en tu navegador web.#   s a l e s - d a s h b o a r d  
 