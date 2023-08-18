#%%
import sys
import os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, "..")
from utile import *



bus_info = "/home/lucky/Documents/CNRS/Justice-Luc/data/fluo 22-05-2021 au 31-08-2023/stops.txt"
path_base = "/home/lucky/Documents/CNRS/Justice-Luc/data/Base_arrêts_CTS.xlsx"

fixe_Base_arrêts_Bus(path_base, bus_info)
