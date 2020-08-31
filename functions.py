
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- project: A SHORT DESCRIPTION OF THE PROJECT                                                         -- #
# -- script: functions.py : python script with general functions                                         -- #
# -- author: oscaralfonso17                                                                              -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- repository: https://github.com/oscaralfonso17/myst_if710183_lab1.git                                -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

import datetime
import glob

def datareader(path):  # Import all csv's
    all_files = sorted(glob.glob(path + "/*.csv"))  # path = 'files/NAFTRAC_holdings'
    return all_files