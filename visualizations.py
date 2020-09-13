
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: visualizations.py : python script with data visualization functions                         -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import plotly.graph_objects as go


def graph(x, y, title, x_title, y_title):
    """,
    Función que crea una gráfica de linea con la librería plotly.

        Parameters
        ----------
        x: list:
            Valores para el eje x de la gráfica
        y: list:
            Valores para el eje y de la gráfica
        title: str:
            Título para la gráfica
        x_title: str:
            Título del eje x
        y_title: str:
            Título del eje y

        Returns
        -------
        fig: Figure:
            Figura con la gráfica

        Debugging
        ---------
        x:df_pasiva['timestamp']
        y:df_pasiva['capital']
        title:"Inversión Pasiva"
        x_title:'Dates'
        y_title:"Capital"
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=y_title, line=dict(color='#2325A8'),
                             marker=dict(symbol=2, color='black'),
                             hovertemplate='<extra></extra>'+'Capital: $%{y:2,.2f}'+'<br>Date: %{x}<br>'))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title,
                      plot_bgcolor='#FFFFFF')

    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    return fig


def two_graph(x, y, name1, x2, y2, name2, title, x_title, y_title):
    """,
    Función que crea una gráfica de linea con la librería plotly.

        Parameters
        ----------
        x: list:
            Valores para el eje x de la gráfica
        y: list:
            Valores para el eje y de la gráfica
        title: str:
            Título para la gráfica
        name1: str:
            Nombre de la serie 1 a graficar
        x: list:
            Segundos valores para el eje x de la gráfica
        y: list:
            Segundos valores para el eje y de la gráfica
        name2: str:
            Nombre de la serie 2 a graficar
        x_title: str:
            Título del eje x
        y_title: str:
            Título del eje y
        Returns
        -------
        fig: Figure:
            Figura con la gráfica

        Debugging
        ---------
        x:df_pasiva['timestamp']
        y:df_pasiva['capital']
        title:"Inversión Pasiva"
        x_title:'Dates'
        y_title:"Capital"
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=name1, line=dict(color='#2325A8'),
                             marker=dict(symbol=2, color='black'),
                             hovertemplate='<extra></extra>'+'Capital: $%{y:2,.2f}'+'<br>Date: %{x}<br>'))
    fig.add_trace(go.Scatter(x=x2, y=y2, mode='lines+markers', name=name2, line=dict(color='red'),
                             marker=dict(symbol=2, color='black'),
                             hovertemplate='<extra></extra>' + 'Capital: $%{y:2,.2f}' + '<br>Date: %{x}<br>'))
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title=y_title,
                      plot_bgcolor='#FFFFFF')

    fig.update_xaxes(showspikes=True)
    fig.update_yaxes(showspikes=True)
    return fig


def DFpasiva(inv_pasiva):
    """
    Función que realiza la inversión pasiva dependiendo principalmente de un DataFrame de precios

        Parameters
        ----------
        inv_pasiva: diccionario para guardar información de cada cierre de mes de la inversión pasiva

        Returns
        -------
        df_pasiva: DataFrame. DataFrame de rendimientos y rendimientos acumulados de una inversión pasiva

        Debugging
        ---------
        passive_dF(archivos, monthly_prices, i_fechas, 1000000, 0.00125, inv_pasiva)
    """
    import numpy as np
    import pandas as pd
    df_pasiva = pd.DataFrame()
    df_pasiva['timestamp'] = inv_pasiva['timestamp']
    df_pasiva['capital'] = np.round(inv_pasiva['capital'], 2)

    df_pasiva['rend'] = 0
    df_pasiva['rend_acum'] = 0
    for i in range(1, len(df_pasiva)):
        df_pasiva.loc[i, 'rend'] = np.round((df_pasiva.loc[i, 'capital'] / df_pasiva.loc[i - 1, 'capital'])-1, 4)
        df_pasiva.loc[i, 'rend_acum'] = np.round(df_pasiva.loc[i - 1, 'rend_acum'] + df_pasiva.loc[i, 'rend'], 4)
    return df_pasiva


def DFActiva(inv_activa, months):
    """
    Función que realiza la inversión activa dependiendo principalmente de un DataFrame de precios

        Parameters
        ----------
        inv_activa: diccionario para guardar información de cada día
        months: lista de fechas ( retorno de t_dates() )

        Returns
        -------
        df_activa: DataFrame. DataFrame de rendimientos y rendimientos acumulados de una inversión activa

        Debugging
        ---------
        activeinvestment(files, d_prices, k, c, kc, x_per, inv_activa, ops_inv_activa):
    """
    import numpy as np
    import pandas as pd
    d = ['2018-01-30']
    d = d + months
    df_activa = pd.DataFrame()
    df_activa['timestamp'] = inv_activa['timestamp']
    df_activa['capital'] = np.round(inv_activa['capital'], 2)
    df_activa['rend'] = 0
    df_activa['rend_acum'] = 0

    df_activa = df_activa[df_activa['timestamp'].isin(d)]
    df_activa = df_activa.reset_index(drop=True)

    for i in range(1, len(df_activa)):
        df_activa.loc[i, 'rend'] = np.round((df_activa.loc[i, 'capital'] / df_activa.loc[i - 1, 'capital'])-1, 4)
        df_activa.loc[i, 'rend_acum'] = np.round(df_activa.loc[i - 1, 'rend_acum'] + df_activa.loc[i, 'rend'], 4)
    return df_activa


def operaciones(dict):
    """
    Función que realiza la el DataFrame de histórico de operaciones

        Parameters
        ----------
        ops_inv_activa: dict:
            diccionario con resultados de la inversión activa.
            ejemplo: ( ops_inv_activa = {'timestamp': [], 'titulos_t': [],
             'titulos_c': [], 'precio': [], 'comision': []} )

        Returns
        -------
        df_operaciones: DataFrame:
            DataFrame de histórico de operaciones de compra de títulos nuevos

        Debugging
        ---------
        activeinvestment(files, d_prices, k, c, kc, x_per, inv_activa, ops_inv_activa)
    """
    import pandas as pd
    df_operaciones = pd.DataFrame()
    df_operaciones['timestamp'] = dict['timestamp']
    df_operaciones['titulos_t'] = dict['titulos_t']
    df_operaciones['titulos_c'] = dict['titulos_c']
    df_operaciones['precio'] = dict['precio']
    df_operaciones['comision'] = dict['comision']
    df_operaciones['Cash Disponible'] = dict['cash']
    return df_operaciones
