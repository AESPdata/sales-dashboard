import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def plot_running_totals(df_running_totals, selected_quarters_labels):
    """
    Crea el gráfico de índice de ventas acumuladas por semana utilizando Plotly Express,
    mostrando solo los periodos seleccionados.

    Args:
        df_running_totals (pd.DataFrame): DataFrame con ventas acumuladas por semana y trimestre,
                                          debe contener 'Week_Number', 'Running_Total', 'Quarter_Label'.
        selected_quarters_labels (list): Lista de etiquetas de trimestre seleccionadas.
    """
    if df_running_totals.empty:
        st.warning("No hay datos disponibles para el gráfico de totales acumulados con los periodos seleccionados.")
        return

    # Usar una paleta de colores cualitativa para diferenciar los trimestres seleccionados
    fig = px.line(
        df_running_totals,
        x='Week_Number',       # Eje X: Número de semana
        y='Running_Total',     # Eje Y: Total acumulado
        color='Quarter_Label', # Dibuja una línea por cada trimestre seleccionado
        title='Totales Acumulados (Trimestres Seleccionados)', # Título traducido
        labels={               # Etiquetas de ejes y leyenda traducidas
            'Week_Number': 'Número de Semana',
            'Running_Total': 'Totales Acumulados',
            'Quarter_Label': 'Trimestre'
        },
        hover_data={           # Datos adicionales a mostrar en el tooltip
            'Week_Number': True,
            'Running_Total': ':.2s', # Formato de número (ej. 726K)
            'Quarter_Label': True
        }
    )

    # Ajustes generales de layout para mejorar la interactividad y estética
    fig.update_layout(
        xaxis_title="Número de Semana", # Etiqueta del eje X traducida
        yaxis_title="Totales Acumulados", # Etiqueta del eje Y traducida
        hovermode="x unified",
        legend_title="Trimestre", # Título de la leyenda traducido
        yaxis=dict(tickformat=".2s"), # Formato de los ticks del eje Y
        yaxis_range=[0, df_running_totals['Running_Total'].max() * 1.1] if not df_running_totals.empty else [0, 1000000]
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_quarterly_metrics(df_quarterly_metrics, selected_quarters_labels):
    """
    Crea el gráfico de barras detallado de métricas trimestrales utilizando Plotly Express,
    mostrando solo los periodos seleccionados.

    Args:
        df_quarterly_metrics (pd.DataFrame): DataFrame con métricas agregadas por trimestre.
        selected_quarters_labels (list): Lista de etiquetas de trimestre seleccionadas.
    """
    if df_quarterly_metrics.empty or not selected_quarters_labels:
        st.warning("No hay datos disponibles para el gráfico de métricas trimestrales con los periodos seleccionados.")
        return

    metrics_to_plot = [
        'Amount', 'Transactions', 'Active_Clients', 'SAMs',
        'Admins', 'Designers', 'Servers'
    ]
    
    # Filtrar el DataFrame de métricas trimestrales para mostrar solo los seleccionados
    df_filtered_for_plot = df_quarterly_metrics[df_quarterly_metrics['Quarter'].isin(selected_quarters_labels)].copy()

    if df_filtered_for_plot.empty:
        st.warning("No hay datos para los trimestres seleccionados en las métricas trimestrales.")
        return

    # Usar una paleta de colores para las barras
    # Se genera un color diferente para cada trimestre seleccionado
    color_map = {q: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, q in enumerate(sorted(selected_quarters_labels))}

    # Diccionario para traducir los nombres de las métricas para los títulos de los gráficos
    metric_translation = {
        'Amount': 'Monto',
        'Transactions': 'Transacciones',
        'Active_Clients': 'Clientes Activos',
        'SAMs': 'Gerentes de Venta Únicos',
        'Admins': 'Licencias de Administradores',
        'Designers': 'Licencias de Diseñadores',
        'Servers': 'Licencias de Servidores'
    }

    figs = []
    for metric in metrics_to_plot:
        fig = px.bar(
            df_filtered_for_plot, # Usar el DataFrame ya filtrado
            x='Quarter',
            y=metric,
            color='Quarter', # Color por trimestre para distinguirlos
            color_discrete_map=color_map, # Asigna colores predefinidos
            title=f'{metric_translation.get(metric, metric)} a lo Largo del Tiempo', # Título traducido
            labels={ # Etiquetas traducidas
                'Quarter': 'Trimestre',
                metric: metric_translation.get(metric, metric)
            },
            hover_data={ # Datos adicionales en el tooltip
                'Quarter': True,
                metric: ':.2s' if metric == 'Amount' else True # Formato para 'Amount', otros como están
            },
            text_auto=True # Muestra automáticamente el valor de la barra
        )
        
        if metric == 'Amount':
            fig.update_yaxes(range=[0, df_filtered_for_plot[metric].max() * 1.2], tickformat=".2s", title='Monto (£)') # Formato de ticks y título del eje Y
        else:
            fig.update_yaxes(title=metric_translation.get(metric, metric), tickformat=".0f") # Título y formato para otras métricas

        fig.update_layout(
            xaxis_title="Trimestre", # Etiqueta del eje X traducida
            showlegend=False # No mostrar leyenda en cada subplot individual
        )
        # Quitar el texto en las barras para las métricas que no son de dinero si se superponen mucho
        if metric != 'Amount':
            fig.update_traces(texttemplate='%{y}', textposition='outside')
            fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

        figs.append(fig)

    for fig in figs:
        st.plotly_chart(fig, use_container_width=True)

def plot_country_performance(df_country_performance):
    """
    Crea el gráfico de barras de rendimiento por país utilizando Plotly Express.
    Proporciona interactividad y muestra los montos de forma clara.

    Args:
        df_country_performance (pd.DataFrame): DataFrame con el total de ventas por país.
                                               Debe contener 'Region', 'Amount', 'Formatted_Amount'.
    """
    if df_country_performance.empty:
        st.warning("No hay datos disponibles para el gráfico de rendimiento por país.")
        return

    # Ordenar los datos para que las barras se muestren de mayor a menor venta
    df_country_performance_sorted = df_country_performance.sort_values(by='Amount', ascending=True)

    fig = px.bar(
        df_country_performance_sorted,
        x='Amount', # Eje X: Monto de ventas
        y='Region', # Eje Y: Región
        orientation='h', # Barras horizontales
        title='Rendimiento por País', # Título traducido
        color_discrete_sequence=px.colors.sequential.Blues_r, # Colores azules degradados
        labels={'Amount': 'Monto de Venta', 'Region': 'País'}, # Etiquetas traducidas
        hover_data={ # Datos a mostrar en el tooltip
            'Region': True,
            'Amount': ':.2s', # Formato de monto (ej. 451K)
            'Formatted_Amount': False # No mostrar esta columna si ya se muestra Amount formateado
        }
    )

    # Añadir las etiquetas de monto directamente en las barras (similar a la imagen)
    for index, row in df_country_performance_sorted.iterrows():
        fig.add_annotation(
            x=row['Amount'] + (row['Amount'] * 0.05), # Posición X un poco después de la barra
            y=row['Region'], # Posición Y en el centro de la barra
            text=row['Formatted_Amount'], # El texto a mostrar
            showarrow=False, # No mostrar flecha
            font=dict(color="black", size=10), # Estilo de fuente
            xanchor="left", # Alineación del texto a la izquierda
            yanchor="middle" # Alineación vertical al medio
        )
    
    fig.update_layout(
        xaxis_title="", # Eliminar título del eje X
        yaxis_title="", # Eliminar título del eje Y
        xaxis_range=[0, df_country_performance_sorted['Amount'].max() * 1.3] # Ajustar el rango del eje X para que quepan las etiquetas
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_city_performance(df_city_performance):
    """
    Crea el gráfico de barras de rendimiento por ciudad utilizando Plotly Express.
    Proporciona interactividad y muestra los montos de forma clara.

    Args:
        df_city_performance (pd.DataFrame): DataFrame con el total de ventas por ciudad.
                                               Debe contener 'City', 'Amount', 'Formatted_Amount'.
    """
    if df_city_performance.empty:
        st.warning("No hay datos disponibles para el gráfico de rendimiento por ciudad.")
        return

    # Ordenar los datos para que las barras se muestren de mayor a menor venta
    df_city_performance_sorted = df_city_performance.sort_values(by='Amount', ascending=True)

    fig = px.bar(
        df_city_performance_sorted,
        x='Amount', # Eje X: Monto de ventas
        y='City', # Eje Y: Ciudad
        orientation='h', # Barras horizontales
        title='Rendimiento por Ciudad', # Título traducido
        color_discrete_sequence=px.colors.sequential.Viridis_r, # Otra paleta de colores
        labels={'Amount': 'Monto de Venta', 'City': 'Ciudad'}, # Etiquetas traducidas
        hover_data={ # Datos a mostrar en el tooltip
            'City': True,
            'Amount': ':.2s',
            'Formatted_Amount': False
        }
    )

    # Añadir las etiquetas de monto directamente en las barras
    for index, row in df_city_performance_sorted.iterrows():
        fig.add_annotation(
            x=row['Amount'] + (row['Amount'] * 0.05),
            y=row['City'],
            text=row['Formatted_Amount'],
            showarrow=False,
            font=dict(color="black", size=10),
            xanchor="left",
            yanchor="middle"
        )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        xaxis_range=[0, df_city_performance_sorted['Amount'].max() * 1.3]
    )

    st.plotly_chart(fig, use_container_width=True)


def plot_seller_performance(df_seller_performance):
    """
    Crea un gráfico de barras interactivo para mostrar el desempeño de los vendedores
    por país, producto y tipo de venta. Utiliza facetas para la región y color/patrón para
    producto y tipo de venta.

    Args:
        df_seller_performance (pd.DataFrame): DataFrame agregado con las ventas totales por Sales_Manager,
                                               Region, Product y License_Type.
    """
    if df_seller_performance.empty:
        st.warning("No hay datos disponibles para el gráfico de desempeño de vendedores con los filtros seleccionados.")
        return

    # Crear el gráfico de barras
    fig = px.bar(
        df_seller_performance,
        x='Sales_Manager',      # Eje X: Vendedor
        y='Amount',             # Eje Y: Monto de Venta
        color='Product',        # Color de las barras por Producto
        pattern_shape='License_Type', # Patrón de las barras por Tipo de Venta
        facet_col='Region',     # Crea subgráficos por Región (columna de faceta)
        facet_col_wrap=3,       # Envuelve las facetas en 3 columnas
        title='Desempeño de Ventas por Gerente de Ventas, Región, Producto y Tipo de Venta', # Título traducido
        labels={                # Etiquetas personalizadas para los ejes y leyendas
            'Sales_Manager': 'Vendedor',
            'Amount': 'Monto de Venta',
            'Product': 'Producto',
            'License_Type': 'Tipo de Venta',
            'Region': 'Región'
        },
        hover_data={            # Datos adicionales a mostrar en el tooltip
            'Amount': ':.2s',   # Formato de monto
            'Sales_Manager': True,
            'Region': True,
            'Product': True,
            'License_Type': True
        },
        height=600 # Altura del gráfico para acomodar múltiples facetas
    )

    # Ajustes del layout para mejorar la legibilidad
    fig.update_layout(
        showlegend=True, # Asegura que la leyenda de color y patrón sea visible
        xaxis_title="Vendedor", # Asegura el título del eje X
        yaxis_title="Monto de Venta", # Asegura el título del eje Y
        hovermode="x unified" # Unifica el tooltip al pasar el ratón por el eje X
    )

    # Ajustar las etiquetas de los ejes X en cada faceta (rotar si es necesario)
    fig.for_each_xaxis(lambda xaxis: xaxis.update(showticklabels=True, tickangle=45))

    # Ajustar títulos de las facetas (los títulos de cada subgráfico)
    fig.update_annotations(patch=dict(font_size=12))

    st.plotly_chart(fig, use_container_width=True)

def plot_seller_performance_over_time(df_seller_time_performance, time_granularity='quarter'):
    """
    Crea un gráfico de líneas para mostrar el desempeño de los vendedores a lo largo del tiempo.

    Args:
        df_seller_time_performance (pd.DataFrame): DataFrame agregado con las ventas totales por Sales_Manager y periodo.
        time_granularity (str): 'month' o 'quarter' para la granularidad temporal en el título y etiquetas.
    """
    if df_seller_time_performance.empty:
        st.warning("No hay datos disponibles para el gráfico de desempeño de vendedores en el tiempo.")
        return

    # Título dinámico basado en la granularidad temporal
    time_unit = "Trimestre" if time_granularity == 'quarter' else "Mes"
    title_text = f'Desempeño de Ventas por Vendedor a lo Largo del {time_unit}'

    fig = px.line(
        df_seller_time_performance,
        x='Period',             # Eje X: Periodo de tiempo
        y='Amount',             # Eje Y: Monto de Venta
        color='Sales_Manager',  # Color de la línea por Vendedor
        title=title_text,       # Título traducido y dinámico
        labels={                # Etiquetas traducidas
            'Period': time_unit,
            'Amount': 'Monto de Venta',
            'Sales_Manager': 'Vendedor'
        },
        hover_data={            # Datos adicionales en el tooltip
            'Period': True,
            'Amount': ':.2s',
            'Sales_Manager': True
        }
    )

    # Ajustes del layout
    fig.update_layout(
        xaxis_title=time_unit,
        yaxis_title="Monto de Venta",
        hovermode="x unified",
        legend_title="Vendedor"
    )
    # Rotar etiquetas del eje X si son trimestres/meses para evitar superposición
    fig.update_xaxes(tickangle=45)

    st.plotly_chart(fig, use_container_width=True)