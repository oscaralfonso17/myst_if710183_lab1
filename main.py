"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: main.py : python script with the main functionality                                         -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""
import functions as fn
import visualizations as vs
import data as dt
import pandas as pd
from os import path
import fire

# Path a los archivos
abspath = path.abspath('files/NAFTRAC_holdings')

# PASO 1. data.py: Obtener la lista de archivos a leer
files = dt.read_files(abspath)

# PASO 2. data.py: Leer todos los archivos y guardarlos en un diccionario
datos_dict = dt.data_dict(files)

# PASO 3. functions.py: Construir el vector de fechas a partir del vector de nombres de archivos
dates = fn.t_dates(files)
days = pd.date_range(start=fn.t_dates(files)[0], end=fn.t_dates(files)[-1])  # Vector de dias
days = days.strftime('%Y-%m-%d')

# PASO 4. functions.py: Construir el vector de tickers utilizables en yahoo finance
tickers = fn.glob_tickers(files)

# PASO 5. functions.py: Descargar y acomodar todos los precios históricos
prices = fn.yahoo_prices(files)
close_prices = prices[0]
open_prices = prices[1]
m_prices = fn.monthly_prices(close_prices, files)
d_prices = fn.daily_prices(close_prices, files)
d_open_prices = fn.daily_prices(open_prices, files)

# PASO 6. main.py: Posicion inicial: Inversion pasiva
k = 1000000.00  # capital
c = 0.00125  # comisiones
inv_pasiva_dict = {'timestamp': ['2018-01-30'], 'capital': [k]}
fn.pasiveinvestment(files, m_prices, dates, k, c, inv_pasiva_dict)

# PASO 7. main.py: df_pasiva: DataFrame de resumen de inversión pasiva
df_pasiva = vs.DFpasiva(inv_pasiva_dict)

# PASO 8. visualizations.py: grafica de evolucion del capital
pasiva_graph = vs.graph(x=df_pasiva['timestamp'], y=df_pasiva['capital'],
                        title="Inversión Pasiva: " +
                        str(inv_pasiva_dict['timestamp'][1]) + " a " + str(inv_pasiva_dict['timestamp'][-1]),
                        x_title='Dates', y_title="Capital")

# PASO 9. INVERSION ACTIVA
x_per = 0.01
kc = 0.1
inv_activa_dict = {'timestamp': ['2018-01-30'], 'capital': [k]}
ops_inv_activa_dict = {'timestamp': [], 'titulos_t': [], 'titulos_c': [], 'precio': [], 'comision': [], 'cash': []}
fn.activeinvestment(files, d_prices, d_open_prices, k, c, kc, x_per, inv_activa_dict, ops_inv_activa_dict)

# PASO 10. main.py: df_activa: DataFrame de resumen de inversión activa
df_activa = vs.DFActiva(inv_activa_dict, dates)

# PASO 11. main.py: df_activa: DataFrame de historico de operaciones
df_operaciones = vs.operaciones(ops_inv_activa_dict)

# PASO 12. visualizations.py: grafica de evolucion del capital
activa_graph = vs.graph(x=df_activa['timestamp'], y=df_activa['capital'],
                        title="Inversión Activa: " +
                        str(inv_activa_dict['timestamp'][1]) + " a " + str(inv_activa_dict['timestamp'][-1]),
                        x_title='Dates', y_title="Capital")

# PASO 13. main.py: Medidas de Atribución al Desempeño
df_medidas = fn.desempeno(df_pasiva, df_activa, 0.0770)

# CONCLUSIONES main.py: comparativo de inversiones
comparative = pd.DataFrame()
comparative["timestamp"] = df_pasiva['timestamp']
comparative["Inversión Pasiva"] = df_pasiva['capital']
comparative["Inversión Activa"] = df_activa['capital']

# CONCLUSIONES visualizations.py: grafica de evolucion del capital (dos graficas)
inver_graphs = vs.two_graph(x=df_pasiva['timestamp'], y=df_pasiva['capital'], name1="Inversión Pasiva",
                            x2=df_activa['timestamp'], y2=df_activa['capital'], name2="Inversión Activa",
                            title="Inversión Pasiva vs Activa: ",
                            x_title='Dates', y_title="Capital")

# What if (#1)
k = 1000000
inv_activa_dict_2 = {'timestamp': ['2018-01-30'], 'capital': [k]}
ops_inv_activa_dict_2 = {'timestamp': [], 'titulos_t': [], 'titulos_c': [], 'precio': [], 'comision': [], 'cash': []}
x_per_2 = 0.025
kc = 0.1
fn.activeinvestment(files, d_prices, d_open_prices, k, c, kc, x_per_2, inv_activa_dict_2, ops_inv_activa_dict_2)
df_activa_2 = vs.DFActiva(inv_activa_dict_2, dates)
df_operaciones_2 = vs.operaciones(ops_inv_activa_dict_2)

# What if (#2)
inv_activa_dict_3 = {'timestamp': ['2018-01-30'], 'capital': [k]}
ops_inv_activa_dict_3 = {'timestamp': [], 'titulos_t': [], 'titulos_c': [], 'precio': [], 'comision': [], 'cash': []}
x_per_3 = 0.005
kc_3 = 0.05
fn.activeinvestment(files, d_prices, d_open_prices, k, c, kc_3, x_per_3, inv_activa_dict_3, ops_inv_activa_dict_3)
df_activa_3 = vs.DFActiva(inv_activa_dict_3, dates)
df_operaciones_3 = vs.operaciones(ops_inv_activa_dict_3)


class Main(object):
    @staticmethod
    def pasive(show=False):
        print(df_pasiva)
        if show:
            pasiva_graph.show()

    @staticmethod
    def active(show=False):
        print(df_activa)
        if show:
            activa_graph.show()

    @staticmethod
    def active_movs():
        print(df_operaciones)

    @staticmethod
    def measures():
        print(df_medidas)

    @staticmethod
    def compare(show=False):
        print(comparative)
        if show:
            inver_graphs.show()


if __name__ == '__main__':
    fire.Fire(Main)
