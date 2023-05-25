import os
import sys
sys.path.insert(0, os.getcwd())
from utile import *

main_path = "/home/lucky/Documents/CNRS/Justice-Luc/FinalWP3Results draft/"

paths = ["GenericStrasbourgFin_Clean.csv",
         "NoBusStrasbourg_Clean.csv",
         "NoTramStrasbourg_Clean.csv",
         "NoTransferStrasbourg_Clean.csv",
         "SlowWalkerStrasbourg_Clean.csv",
         "WalkReluctantStrasbourg_Clean.csv"]

for p in paths:
    print(p)
    filtreTime(main_path + p)