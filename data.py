"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: data.py : python script for data collection                                                 -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

from os import listdir
from os.path import isfile, join
import pandas as pd
from datetime import datetime


def read_files(path):
    """
    Función que extrae los nombres de los archivos de un path SIN SU EXTENSIÓN, para posteriormente leerlos.

        Parameters
        ----------
        path: path.abspath:
            path a los archivos del NAFTRAC

        Returns
        -------
        archivos: list:
            archivos ordenados cronológicamente

        Debugging
        ---------
        path = path.abspath('files/NAFTRAC_holdings')
    """
    archivos = [f[:-4] for f in listdir(path) if isfile(join(path, f))]
    # Ordernar archivos por fecha
    archivos = sorted(archivos, key=lambda string: datetime.strptime(string[8:], '%d%m%y'))
    return archivos


def data_dict(archivos):
    """
    Función que lee los archivos de una lista, creando un diccionario con cada DataFramede cada archivo leido.

        Parameters
        ----------
        archivos: list:
            lista con nombres de archivos

        Returns
        -------
        data_archivos: dict:
            Diccionario con los archivos ya leídos.

        Debugging
        ---------
        archivos = read_files()
    """
    # Crear diccionario para almacenar todos los datos
    data_archivos = {}
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
        data['Peso (%)'] = data['Peso (%)'] / 100
        # guardar en diccionario
        data_archivos[i] = data
    return data_archivos
