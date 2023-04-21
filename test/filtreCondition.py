#%%
import sys
import os
sys.path.insert(0, os.getcwd())
from utile import *

path = "/home/lucky/Documents/CNRS/Justice-Luc/data/Base_arrêts_CTS.xlsx"

filtreCondition(path,["Accessible en fauteuil roulant", "Assistance sonore disponible"])


# %%
