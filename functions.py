"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import numpy as np
from data import *

pd.set_option('display.expand_frame_rep', True)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('colheader_justify', 'left')


def t_dates(archivos):
    """
    Función que crea una serie de fechas con formato '%Y-%m-%d'

        Parameters
        ----------
        archivos: list:
            lista con nombres de archivos

        Returns
        -------
        t_fechas: list:
            lista de fechas

        Debugging
        ---------
        archivos = read_files()
    """
    # fechas a partir de los archivos
    t_fechas = [i.strftime('%Y-%m-%d') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]
    return t_fechas


def glob_tickers(archivos):
    """
    Función para generar lista de activos compatibles con Yahoo Finance

        Parameters
        ----------
        archivos: list:
            lista con nombres de archivos

        Returns
        -------
        global_tickers: list:
            Lista con activos para descargar sus precios de Yahoo Finance

        Debugging
        ---------
        archivos = read_files()
    """
    tickers = []
    for i in archivos:
        # i = archivos[0]
        data_archivos = data_dict(archivos)
        l_tickers = list(data_archivos[i]['Ticker'])
        [tickers.append(i + '.MX') for i in l_tickers]
    global_tickers = np.unique(tickers).tolist()
    # Reemplazo de tickers por actualizaciones en Yahoo
    global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
    global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
    global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

    # eliminar MXN, USD
    [global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX', 'KOFUBL.MX', 'BSMXB.MX']]
    # KOFL pasar a Cash
    return global_tickers


def yahoo_prices(archivos):
    """
    Función que descarga precios de Yahoo Finance

        Parameters
        ----------
        archivos: list:
            list con nombres de archivos

        Returns
        -------
        data_close: DataFrame:
            Precios de cierre diario los activos

        Debugging
        ---------
        archivos = read_files()
    """
    # Bajar precios de Yahoo finance
    import yfinance as yf

    data_yf = yf.download(glob_tickers(archivos), start='2017-08-21', end='2020-08-22', actions=False,
                          group_by='close', interval='1d', auto_adjust=False, prepost=False, threads=True)
    # print('se tardo', time.time() - inicio, 'segundos')

    # Quedarnos con close data only
    data_close = pd.DataFrame({i: data_yf[i]['Close'] for i in glob_tickers(archivos)})
    data_open = pd.DataFrame({i: data_yf[i]['Open'] for i in glob_tickers(archivos)})
    return data_close, data_open


def monthly_prices(data_close, archivos):
    """
    Función que acomoda los precios unicos del primer periodo

        Parameters
        ----------
        data_close: DataFrame con precios de cierre diarios ( Utilizando yahoo_prices() )

        archivos: list:
            list con nombres de archivos
        Returns
        -------
        precios: DataFrame:
            Precios de los activos coincidentes al primer periodo.

        Debugging
        ---------
        archivos = read_files()
    """
    data_close = data_close
    # tomar solo las fechas de interés (utilizando teoria de conjuntos)
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(t_dates(archivos))))
    # localizar todos los precios (del primer NAFTRAC)
    precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]
    # ordernar columnas lexicograficamente
    precios = precios.reindex(sorted(precios.columns), axis=1)
    return precios


def daily_prices(data_close, archivos):
    """
    Función que acomoda los precios unicos diarios

        Parameters
        ----------
        data_close: DataFrame con precios de cierre diarios ( Utilizando yahoo_prices() )

        archivos: list:
            lista con nombres de archivos
        Returns
        -------
        precios: DataFrame:
            Precios de los activos coincidentes al primer periodo.

        Debugging
        ---------
        archivos = read_files()
    """
    data_close = data_close
    # tomar solo las fechas de interés (utilizando teoria de conjuntos)
    days = pd.date_range(start=t_dates(archivos)[0], end=t_dates(archivos)[-1])
    days = days.strftime('%Y-%m-%d')
    ic_fechas = sorted(list(set(data_close.index.astype(str).tolist()) & set(days)))
    # localizar todos los precios (del primer NAFTRAC)
    precios = data_close.iloc[[int(np.where(data_close.index.astype(str) == i)[0]) for i in ic_fechas]]
    # ordernar columnas lexicograficamente
    precios = precios.reindex(sorted(precios.columns), axis=1)
    return precios


def pasiveinvestment(archivos, monthly_prices, i_fechas, k, c, inv_pasiva):
    """
    Función que realiza la inversión activa dependiendo principalmente de un DataFrame de precios

        Parameters
        ----------
        archivos: list:
            lista con nombres de archivos
        monthly_prices: DataFrame:
            Precios mensuales ( retorno de monthly_prices() )
        i_fechas: list:
            lista de fechas ( retorno de t_dates() )
        k: int:
            Capital inicial
        c: float:
            porcentaje de comisiones
        inv_pasiva: dict:
            diccionario para guardar información de cada cierre de mes de la inversión pasiva

        Returns
        -------

        Debugging
        ---------
        archivos = read_files()
        monthly_prices = monthly_prices(files)
        i_fechas = t_dates(files)
        k = 1000000
        c = 0.00125
        inv_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}
    """
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'MXN', 'USD']  # Los % de c_activos asignarlos a CASH
    comisiones = [0]  # Lista de comisiones
    pos_datos = data_dict(archivos)[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Peso (%)']]
    # extraer la lista de activos a eliminar
    i_activos = list(pos_datos[list(pos_datos['Ticker'].isin(c_activos))].index)
    # eliminar los activos del dataframe
    pos_datos.drop(i_activos, inplace=True)
    # resetear el index
    pos_datos.reset_index(inplace=True, drop=True)
    # agregar .MX a los Tickers
    pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'
    # correccion de datos
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')

    # PRIMERA POSICION
    pos_datos['Precio'] = (
        np.array([monthly_prices.iloc[0, monthly_prices.columns.to_list().index(i)] for i in pos_datos['Ticker']]))
    # capital destinado por accion = proporcion de capital - comisiones por la posicion
    pos_datos['Capital'] = np.round(pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c, 2)
    pos_datos['Titulos'] = pos_datos['Capital'] // pos_datos['Precio']
    pos_datos['Comision'] = pos_datos['Precio'] * pos_datos['Titulos'] * c
    pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']
    # Cash fijo
    cash = np.round(k - pos_datos['Postura'].sum() - pos_datos['Comision'].sum(), 2)
    # Listas con valores
    inv_pasiva['capital'].append(k - pos_datos['Comision'].sum())
    comisiones.append(sum(pos_datos['Comision']))
    inv_pasiva['timestamp'].append(i_fechas[0])

    # 2 A N POSICIONES
    for a in range(1, len(i_fechas)):
        pos_datos['Precio'] = np.round(np.array([monthly_prices.iloc[a, monthly_prices.columns.to_list().index(i)] for
                                                 i in pos_datos['Ticker']]), 2)
        pos_datos['Comision'] = 0  # ya no hay comisiones
        pos_datos['Postura'] = np.round(pos_datos['Titulos'] * pos_datos['Precio'], 2)

        inv_pasiva['capital'].append(np.round(sum(pos_datos['Postura']) + cash, 2))
        comisiones.append(sum(pos_datos['Comision']))
        inv_pasiva['timestamp'].append(i_fechas[a])


def activeinvestment(archivos, d_prices, d_open, k, c, kc, x_per, inv_activa, ops_inv_activa):
    """
    Función que realiza la inversión activa dependiendo principalmente de un DataFrame de precios

        Parameters

        ----------
        archivos: list:
            lista con nombres de archivos
        d_prices: DataFrame:
            Precios diarios de cierre ( retorno de yahoo_prices() )
        d_open: DataFrame:
            Precios diarios de apertura ( retorno de yahoo_prices() )
        i_fechas: list:
            lista de fechas ( retorno de t_dates() )
        k: int:
            Capital inicial
        c: float:
            porcentaje de comisiones
        x_per: float:
            decimal de cambio en el precio. Señal de compra
        kc: float:
            decimal de porcentaje a comprar cuando se active la señal de compra
        inv_pasiva: dict:
            diccionario para guardar información de cada cierre de día de la inversión activa
        ops_inv_activa: dict:
            diccionario para guardar informacion de compra de titulos del activo con mayor peso

        Returns
        -------

        Debugging
        ---------
        archivos = read_files()
        monthly_prices = monthly_prices(files)
        i_fechas = t_dates(files)
        k = 1000000
        c = 0.00125
        x_per = 0.01
        kc = 0.1
        inv_pasiva = {'timestamp': ['30-01-2018'], 'capital': [k]}
        ops_inv_activa = {'timestamp': [], 'titulos_t': [], 'titulos_c': [], 'precio': [], 'comision': []}
    """
    c_activos = ['KOFL', 'KOFUBL', 'BSMXB', 'USD', 'MXN']  # Los % de activos asignarlos a CASH
    comisiones = [0]  # Lista de comisiones
    pos_datos = data_dict(archivos)[archivos[0]].copy().sort_values('Ticker')[['Ticker', 'Peso (%)']]
    i_activos = list(pos_datos[list(pos_datos['Ticker'].isin(c_activos))].index)
    pos_datos.drop(i_activos, inplace=True)
    pos_datos.reset_index(inplace=True, drop=True)
    pos_datos['Ticker'] = pos_datos['Ticker'] + '.MX'
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('GFREGIOO.MX', 'RA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('MEXCHEM.MX', 'ORBIA.MX')
    pos_datos['Ticker'] = pos_datos['Ticker'].replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')

    # encontrar el activo con mayor ponderacion
    peso_max = pos_datos['Peso (%)'].idxmax()

    pos_datos['Precio'] = np.round(np.array([d_prices.iloc[0, d_prices.columns.to_list().index(i)] for
                                             i in pos_datos['Ticker']]), 2)
    pos_datos['Precio_open'] = np.round(np.array([d_prices.iloc[0, d_prices.columns.to_list().index(i)] for
                                                  i in pos_datos['Ticker']]), 2)
    pos_datos['Precio_c'] = 0

    pos_datos['Capital'] = np.round(pos_datos['Peso (%)'] * k - pos_datos['Peso (%)'] * k * c, 2)

    pos_datos.loc[peso_max, 'Capital'] = pos_datos.loc[peso_max, 'Capital'] / 2  # LIMITE AL 50%

    pos_datos['Titulos'] = pos_datos['Capital'] // pos_datos['Precio']
    pos_datos['Comision'] = np.round(pos_datos['Precio'] * pos_datos['Titulos'] * c, 2)
    pos_datos['Postura'] = pos_datos['Titulos'] * pos_datos['Precio']

    cash = np.round(k - pos_datos['Postura'].sum() - pos_datos['Comision'].sum(), 2)

    inv_activa['capital'].append(k - pos_datos['Comision'].sum())
    comisiones.append(sum(pos_datos['Comision']))

    inv_activa['timestamp'].append(str(d_prices.index[0].strftime('%Y-%m-%d')))

    ops_inv_activa['timestamp'].append(str(d_prices.index[0].strftime('%Y-%m-%d')))
    ops_inv_activa['titulos_t'].append(pos_datos.loc[peso_max, 'Titulos'])
    ops_inv_activa['titulos_c'].append(pos_datos.loc[peso_max, 'Titulos'])
    ops_inv_activa['precio'].append(pos_datos.loc[peso_max, 'Precio'])
    ops_inv_activa['comision'].append(pos_datos.loc[peso_max, 'Comision'])
    ops_inv_activa['cash'].append(cash)

    for a in range(1, len(d_prices)):
        # Precio nuevo
        pos_datos['Precio'] = np.round(np.array([d_prices.iloc[a, d_prices.columns.to_list().index(i)] for
                                                 i in pos_datos['Ticker']]), 2)
        pos_datos['Comision'] = 0

        pos_datos.loc[peso_max, 'Precio_open'] = \
            np.round(np.array(d_open.iloc[a, d_open.columns.to_list().index(pos_datos.loc[peso_max, 'Ticker'])]), 2)

        dif = (pos_datos.loc[peso_max, 'Precio'] / pos_datos.loc[peso_max, 'Precio_open']) - 1
        comprados = pos_datos.loc[peso_max, 'Titulos']

        if dif <= -x_per:
            if a < len(d_prices)-1:
                pos_datos.loc[peso_max, 'Precio_c'] = \
                    np.round(np.array(d_open.iloc[a + 1,
                                                  d_open.columns.to_list().index(pos_datos.loc[peso_max,
                                                                                               'Ticker'])]), 2)
            if (cash * kc - cash * kc * c) // pos_datos.loc[peso_max, 'Precio_c'] > 0:
                # Nuevo capital, sumando el 10% y restando comisiones
                pos_datos.loc[peso_max, 'Capital'] = pos_datos.loc[peso_max, 'Capital'] + (cash * kc - cash * kc * c)
                # titulos anteriores
                titulos = pos_datos.loc[peso_max, 'Titulos']
                # titulos comprados con el cash disponible
                comprados = ((cash * kc) - (cash * kc * c)) // pos_datos.loc[peso_max, 'Precio_c']

                # gastamos el 10% del cash en titulos
                cash = cash - (cash * kc - cash * kc * c)

                n_titulos = comprados + titulos
                # actualización de titulos
                pos_datos.loc[peso_max, 'Titulos'] = n_titulos

                # comision de titulos comprados
                pos_datos.loc[peso_max, 'Comision'] = np.round(pos_datos.loc[peso_max, 'Precio_c'] * comprados * c, 2)

                ops_inv_activa['timestamp'].append(str(d_prices.index[a + 1].strftime('%Y-%m-%d')))
                ops_inv_activa['titulos_t'].append(n_titulos)
                ops_inv_activa['titulos_c'].append(comprados)
                ops_inv_activa['precio'].append(pos_datos.loc[peso_max, 'Precio_c'])
                ops_inv_activa['comision'].append(pos_datos.loc[peso_max, 'Comision'])
                ops_inv_activa['cash'].append(cash)

                postura = [a * b - c for a, b, c in zip(ops_inv_activa['titulos_c'], ops_inv_activa['precio'],
                                                        ops_inv_activa['comision'])]
                pos_datos.loc[peso_max, 'Postura'] = np.sum(postura)

            for i in range(len(pos_datos['Ticker'])):
                if i == peso_max:
                    pass
                else:
                    pos_datos['Postura'] = np.round(pos_datos['Titulos'] * pos_datos['Precio'], 2)

        pos_datos['Precio_ant'] = pos_datos['Precio']
        pos_datos['Postura'] = np.round(pos_datos['Titulos'] * pos_datos['Precio'], 2)
        inv_activa['capital'].append(np.round(sum(pos_datos['Postura']) + cash, 2))
        comisiones.append(sum(pos_datos['Comision']))
        inv_activa['timestamp'].append(str(d_prices.index[a].strftime('%Y-%m-%d')))


def desempeno(pasiva, activa, tiie):
    """
    Función que realiza la inversión activa dependiendo principalmente de un DataFrame de precios

        Parameters

        ----------
        pasiva: DataFrame:
            DataFrame con rendimientos y rendimientos acumulados de la inversión pasiva
        activa: DataFrame:
            DataFrame con rendimientos y rendimientos acumulados de la inversión activa
        tiie: float:
            TIIE a 360 días en el comienzo de las inversiones
        Returns
        -------
        df_medidas: DataFrame:
            DataFrame con Medidas de Atribución al Desempeño básicas para comparar las estrategias.

        Debugging
        ---------
        pasiva: df_pasiva
        activa: df_activa
        tiie: 0.0770
    """
    df_medidas = pd.DataFrame()
    df_medidas['medida'] = ['rend_m', 'rend_c', 'sharpe']
    df_medidas['descripcion'] = ['Rendimiento Promedio Mensual', ' Rendimiento mensual Acumulado', 'Ratio de Sharpe']

    df_medidas.loc[0, 'inv_pasiva'] = np.round(np.average(pasiva['rend']), 4)
    df_medidas.loc[1, 'inv_pasiva'] = pasiva.loc[len(pasiva) - 1, 'rend_acum']
    df_medidas.loc[2, 'inv_pasiva'] = np.round((np.average(pasiva['rend']) - (tiie / 12)) / np.std(pasiva['rend']), 4)

    df_medidas.loc[0, 'inv_activa'] = np.round(np.average(activa['rend']), 4)
    df_medidas.loc[1, 'inv_activa'] = activa.loc[len(activa) - 1, 'rend_acum']
    df_medidas.loc[2, 'inv_activa'] = np.round((np.average(activa['rend']) - (tiie / 12)) / np.std(activa['rend']), 4)
    return df_medidas
