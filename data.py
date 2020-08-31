
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# --------------------------------------- CLASE --------------------------------------------------
from os import listdir, path
from os.path import isfile, join
import pandas as pd
import numpy as np
import time
import yfinance as yf
from datetime import datetime
import math

abspath = path.abspath('files/NAFTRAC_holdings')

# Crear diccionario para almacenar todos los datos
data_archivos = {}
archivos = [f[:-4] for f in listdir(abspath) if isfile(join(abspath, f))]
# Ordernar archivos por fecha
archivos = sorted(archivos, key=lambda t: datetime.strptime(t[8:], '%d%m%y'))

for i in archivos:
    # leer archivos ignorando los dos primeros renglones
    data = pd.read_csv('files/NAFTRAC_holdings/' + i + '.csv', skiprows=2, header=None)
    # renombrar las columnas
    data.columns = list(data.iloc[0, :])
    # Quitar columnas que no sean nan
    data = data.loc[:, pd.notnull(data.columns)]
    data = data.iloc[1:-1].reset_index(drop=True, inplace=False)
    # Quitar las comas en la columna de precios
    data['Precio'] = [i.replace(',', '') for i in data['Precio']]
    # Quitar el * de los Ticker
    data['Ticker'] = [i.replace('*', '') for i in data['Ticker']]
    # hacer conversiones de tipos de columnas
    convert_dict = {'Ticker': str, 'Nombre': str, 'Peso (%)': float, 'Precio': float}
    data = data.astype(convert_dict)
    # Convertir a decimal la columna de Peso
    data['Peso (%)'] = data['Peso (%)']/100
    # guardar en diccionario
    data_archivos[i] = data

# fechas a partir de los archivos
t_fechas = [i.strftime('%d-%m-%y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]
# fechas para indexadores
i_fechas = [i.strftime('%d%m%y') for i in sorted([pd.to_datetime(i[8:]).date() for i in archivos])]


tickers = []
for i in archivos:
    # i = archivos[0]
    l_tickers = list(data_archivos[i]['Ticker'])
    [tickers.append(i + '.MX') for i in l_tickers]
global_tickers = np.unique(tickers).tolist()

global_tickers = [i.replace('GFREGIOO.MX', 'RA.MX') for i in global_tickers]
global_tickers = [i.replace('MEXCHEM.MX', 'ORBIA.MX') for i in global_tickers]
global_tickers = [i.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX') for i in global_tickers]

# eliminar MXN, USD
[global_tickers.remove(i) for i in ['MXN.MX', 'USD.MX', 'KOFL.MX']]
# KOFL pasar a Cash

# Bajar precios de Yahoo finance
inicio = time.time()
data_yf = yf.download(global_tickers, start='2017-08-21', end='2020-08-22', actions=False,
                   group_by='close', interval='1d', auto_adjust=True, prepost=False, threads=True)
print('se tardo', time.time() - inicio, 'segundos')

# Initial commissions
k = 1000000
c = 0.00125

# Solo close data
data_close = pd.DataFrame()
for i in global_tickers:
    data_close[i] = data_yf[i]['Close']
# Cambiar el index al mismo formato
data_close.index = data_close.index.strftime('%d%m%y')
# Quedarnos con solo las fechas de mes (mismas que los archivos)
month_data_close = data_close.loc[i_fechas, :]

# Precios a inversion pasiva
df_precios = pd.DataFrame(data_archivos[archivos[0]][['Ticker', 'Peso (%)']])
df_precios['Ticker'] = df_precios['Ticker'] + '.MX'
df_precios = df_precios.replace('GFREGIOO.MX', 'RA.MX')
df_precios = df_precios.replace('MEXCHEM.MX', 'ORBIA.MX')
df_precios = df_precios.replace('LIVEPOLC.1.MX', 'LIVEPOLC-1.MX')
df_precios = df_precios.replace('KOFL.MX', 'CASH')
df_precios = df_precios.replace('BSMXB.MX', 'CASH')
df_precios = df_precios.replace('MXN.MX', 'CASH')
df_precios = df_precios.groupby(df_precios['Ticker']).aggregate({'Ticker': 'first', 'Peso (%)': 'sum'})
df_precios = df_precios.set_index('Ticker')

df_precios['Inversion'] = df_precios['Peso (%)'] * k  # Capital repartido entre pesos

# Llenar los precios correspondientes
for i in i_fechas:
    df_precios[i] = month_data_close.loc[i]
    df_precios[i] = df_precios[i].fillna(100)  # Rellenar nan's con 100.00 (CASH)
    df_precios[i] = df_precios['Inversion']/df_precios[i]  # Determinar cantidad de titulos por acción
    df_precios[i] = df_precios[i].apply(np.floor)  # Redondear hacía abajo la cantidad de titulos
    df_precios[i] = month_data_close.loc[i] * df_precios[i]  # Titulos * precio
    df_precios.loc['CASH', i] = df_precios.loc['CASH', 'Inversion']  # Arreglo de nan (CASH)
    if i == i_fechas[0]:
        df_precios[i] = df_precios[i] - df_precios[i]*c

sum_df_precios = []
for i in i_fechas:
    sum_df_precios.append(sum(df_precios[i]))

sum_df_precios = pd.DataFrame(sum_df_precios)
sum_df_precios = (sum_df_precios / k-1)*100

df_pasiva = pd.DataFrame()
df_pasiva['timestamp'] = t_fechas
df_pasiva['capital'] = k
df_pasiva['rend_acum'] = sum_df_precios
