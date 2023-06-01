#%%
import sys
import os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, "..")
from utile import *

main_path = "/home/lucky/Documents/CNRS/Justice-Luc/FinalWP3Results draft/"

paths = ["GenericStrasbourgFin.csv",
         "NoBusStrasbourg.csv",
         "NoTramStrasbourg.csv",
         "NoTransferStrasbourg.csv",
         "SlowWalkerStrasbourg.csv",
         "WalkReluctantStrasbourg.csv"]

for p in paths:
    print(p)
    GenericClean(main_path + p)

