
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

# timestamp part of df_pasiva
dates = []

[dates.append(last_day_of_month(datetime.date(2018, month, 1))) for month in range(1, 13)]
[dates.append(last_day_of_month(datetime.date(2019, month, 1))) for month in range(1, 13)]
[dates.append(last_day_of_month(datetime.date(2020, month, 1))) for month in range(1, 9)]

dates = pd.DataFrame(dates)
dates.columns = ['timestamp']

# DF de precio inicial y ponderaciones
path = 'files/NAFTRAC_holdings'
all_files = sorted(glob.glob(path + "/*.csv"))

# Pesos iniciales (2018): Tomar el primer archivo de all_files
pesos_in = pd.read_csv(all_files[0],
                       skiprows=2)
pesos_in = pesos_in.loc[:, ['Peso (%)', 'Ticker']]
pesos_in = pesos_in.set_index('Ticker')
pesos_in['Peso (%)'] = pesos_in['Peso (%)'] / 100

# Precios variables (2018-2020)
i = 0
for filename in all_files:
    df = pd.read_csv(filename, skiprows=2)
    df = df.set_index('Ticker')
    pesos_in[i] = df.loc[:, 'Precio']
    i = i + 1
pesos_in = pesos_in.fillna(0)
pesos_in = pesos_in.replace(',', '', regex=True)
pesos_in = pesos_in.astype('float64')

# Comisiones
capital = 1000000
comision = 0.0125 / 100
prices = pesos_in
final = []

price_per_day = pd.DataFrame()
price_per_day['Precio'] = prices.loc[:, 0].values  # Comision incial
price_per_day['Invertido'] = prices['Peso (%)'].values * capital
price_per_day['Invertido'] = price_per_day['Invertido']
price_per_day['titulos'] = round(price_per_day['Invertido'] / price_per_day['Precio'])
price_per_day['Comisiones'] = comision * price_per_day['titulos'] * price_per_day['Precio']
price_per_day['Total'] = price_per_day['titulos'] * price_per_day['Precio'] - price_per_day['Comisiones']
price_per_day = price_per_day.fillna(0)
price_per_day = price_per_day.replace([np.inf, -np.inf], 0)

final.append(sum(price_per_day['Total']))

for i in range(1, 32):
    price_per_day = pd.DataFrame()
    price_per_day['Precio'] = prices.loc[:, i].values
    price_per_day['Invertido'] = prices['Peso (%)'].values * capital
    price_per_day['Invertido'] = price_per_day['Invertido']
    price_per_day['titulos'] = round(price_per_day['Invertido'] / price_per_day['Precio'])
    price_per_day['Comisiones'] = 0  # no hay comisiones posteriores
    price_per_day['Total'] = price_per_day['titulos'] * price_per_day['Precio'] - price_per_day['Comisiones']
    price_per_day = price_per_day.fillna(0)
    price_per_day = price_per_day.replace([np.inf, -np.inf], 0)

    final.append(sum(price_per_day['Total']))

final = pd.DataFrame(final)
final = final / capital - 1

# Creacion DF pasivo
df_pasiva = dates
df_pasiva['Capital'] = capital
df_pasiva['rendcum'] = final.values