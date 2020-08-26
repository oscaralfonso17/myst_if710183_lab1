
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import pandas as pd
import glob
import datetime
from functions import last_day_of_month
import numpy as np

dates = []  # timestamp part of df_pasiva
for month in range(1, 13):
    dates.append(last_day_of_month(datetime.date(2018, month, 1)))
    dates.append(last_day_of_month(datetime.date(2019, month, 1)))

for month in range(1, 9):
    dates.append(last_day_of_month(datetime.date(2020, month, 1)))

dates.columns = ['timestamp']
dates = pd.DataFrame(dates)

# DF de precio inicial y ponderaciones
path = 'files/NAFTRAC_holdings'
all_files = sorted(glob.glob(path + "/*.csv"))

# Pesos iniciales (2018)
precios_frame = pd.read_csv('files/NAFTRAC_holdings/01NAFTRAC_310118.csv', skiprows=2)
precios_frame = precios_frame.loc[:, ['Ticker', 'Peso (%)']]
precios_frame = precios_frame.set_index('Ticker')
precios_frame = precios_frame/100

# Precios variables (2018-2020)
i = 0
for filename in all_files:
    df = pd.read_csv(filename, skiprows=2)
    df = df.set_index('Ticker')
    precios_frame[i] = df.loc[:, 'Precio']
    i = i + 1
precios_frame = precios_frame.fillna(0)

# Comisiones
capital = 1000000
comision = 0.0125 / 100
prices = precios_frame
final = []

day1 = pd.DataFrame()
day1['Precio'] = prices.loc[:, 0].values  # Comision incial
day1['Invertido'] = capital * prices['Peso (%)'].values
day1['titulos'] = round(day1['Invertido'] / day1['Precio'])
day1['Comisiones'] = comision * day1['titulos'] * day1['Precio']
day1['Total'] = day1['Precio'] * day1['titulos'] - day1['Comisiones']
day1 = day1.fillna(0)
day1 = day1.replace([np.inf, -np.inf], 0)

final.append(sum(day1['Total']))

for i in range(1, 32):
    price_per_day = pd.DataFrame()
    price_per_day['Precio'] = prices.loc[:, i].values
    price_per_day['Invertido'] = prices['Peso (%)'].values * capital
    price_per_day['titulos'] = round(price_per_day['Invertido'] / price_per_day['Precio'])
    price_per_day['Comisiones'] = 0  # no hay comisiones posteriores
    price_per_day['Total'] = price_per_day['titulos'] * price_per_day['Precio']
    price_per_day = price_per_day.fillna(0)
    price_per_day = price_per_day.replace([np.inf, -np.inf], 0)

    final.append(sum(price_per_day['Total']))

final = pd.DataFrame(final) # Capital final dia por dia
final = final / capital - 1
final

# Creacion DF pasivo
df_pasiva = dates
df_pasiva['Capital'] = capital
df_pasiva['rendcum'] = final.values
