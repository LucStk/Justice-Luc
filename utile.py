import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


import platform




def filtreTime(path, max = 60*60*2, overwrite = False):
    """
    Filtre les sorties de l'algorithme des plus courts chemins
    On enlève les lignes avec duration == NaN et supèrieur à 'max' en seconde
    
    path      : le chemin du fichier xlsx ou csv
    overwrite : Si True alors ré-écrit le fichier d'origine. Sinon création
                d'un nouveau fichier avec l'extension _Conditionfiltred.csv
        
    """

    
    operating_system = platform.system()
    if operating_system == "Linux":
        sep = "/"
    else:
        sep = "\\"

    path_list = path.split(sep)
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path, delimiter=",")
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"


    #Renome le nom des colonnes (pb sur generic)
    base = base.rename(columns={ '\'unique_request\'': "unique_request", '\'from_stop_id\'':"from_stop_id", 
                         '\'from_lon\'': "from_lon", '\'from_lat\'' : "from_lat",
       '\'to_stop_id\'' : "to_stop_id", '\'to_lon\'' : "to_lon", '\'to_lat\'' : "to_lat", 
       '\'time\'' : "time", '\'duration\'' : "duration",
       '\'startTime\'' : "startTime", '\'endTime\'' : "endTime", '\'walkTime\'' : "walkTime", 
       '\'transitTime\'' : "transitTime",'\'waitingTime\'' : "waitingTime", 
       '\'walkDistance\'' : "walkDistance", '\'transfers\'' : "transfers"})
    
    a = len(base)
    #Enlève les lignes qui ont duration à NaN
    base = base[~pd.isna(base['duration'])]
    #Parse les lignes
    base = base.applymap(lambda x: str(x).replace("'",""), na_action='ignore')
    #On filtre les durées trop longues
    for i in ["duration", "walkTime", "waitingTime", "transfers", "walkDistance", "transitTime",]:
        base[i] = base[i].astype("float")

    for i in ["from_stop_id"]:
        base[i] = base[i].astype("int")

    base = base[base['duration'] < max]
    print("{} lignes filtrés".format(a - len(base)))

    if overwrite:
        new = sep.join(path_list[:-1]) + sep + name + ".csv"
    else:
        new = sep.join(path_list[:-1]) + sep+ name + "_Timefiltred.csv"
    base.to_csv(new,sep=",", index=False)



def filtreCondition(path, conditions, output  = "banned.txt", form = "feed:{}"):
    """
    path       : Le chemin du fichier xlsx ou csv
    conditions : Liste des conditions qui doivent être à Oui
    form : format pour chaque sortie
    
    retourne   : un fichier banned.txt contenant une liste de code arrêt CTS des station à bannir
    """

    
    operating_system = platform.system()
    if operating_system == "Linux":
        sep = "/"
    else:
        sep = "\\"


    path_list = path.split(sep)
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path)
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"

    conditions_possibles = base.keys()[(base == "Oui").any()]

    banned = []
    for condition in conditions:
        #Si jamais la condition ne se trouve pas dans les conditions possible -> Error
        if condition not in conditions_possibles:
            print("Error : Condition introuvable, veuillez vérifier que l'orthographe de la condition est le même que celui de la colonne")
        else:
            banned += [np.array(base[condition]) == "Non"]

    banned = base[np.sum(banned, axis = 0) != 0]
    banned = banned["Code arrÃªt CTS"]
    banned = banned[~banned.isnull()]

    l = [form.format(i) for i in list(banned)]
    l = '"' + ",".join(l) + '"'
    o = open(output, "w")
    o.write(str(l))
    o.close()




def GenericClean(path, path_DEPART = None, path_ARRIVE = None, overwrite= False):
    """
    Construit un nouveau fichier csv modifié à partir des fichiers Poi et Mailles
    Rajoute les id des destinations et des origines.
    Enlève les doublons de requête.

    path      : Nom du fichier à nettoyer et csv ou xlsx
    overwrite : Si True alors ré-écrit le fichier d'origine. Sinon création
                d'un nouveau fichier avec l'extension _Clean.csv

    ATTENTION : Les fichiers POIStras.csv et Mailles_Stras.csv comprennant les
    ID des stations origines et destinations sont supposés DANS LE MEME dossier
    que le fichier à nettoyer.
    Si ce n'est pas le cas. Indiquez le chemin de ces fichiers en arguments.
    """


    operating_system = platform.system()
    if operating_system == "Linux":
        sep = "/"
    else:
        sep = "\\"


    path_list = path.split(sep)
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path, delimiter=",")
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"

    if path_ARRIVE is not None:
        destination = pd.read_csv(path_ARRIVE)
    else:
        destination = pd.read_csv(sep.join(path_list[:-1])+ sep +"POIStras.csv")

    if path_DEPART is not None: 
        origine = pd.read_csv(path_DEPART)
    else:
        origine = pd.read_csv(sep.join(path_list[:-1])+ sep +"Mailles_Stras.csv")

    #Élimination des doublons
    to_drop = []
    already_seen = set()
    for o,i in enumerate(base.unique_request):
        if i in already_seen:
            to_drop.append(o)
        else:
            already_seen.add(i)

    base.drop(index=to_drop, inplace   = True)
    
    #Création de la ligne durationmin
    base = base.assign(durationmin = lambda x : round(x.duration / 60,2))
    #Récupère les id des destinations et des origines en faisant une jointure gps avec les fichier POIStras et Mailles_Stras
    
    dicto_destination = {}
    dicto_origine     = {}

    for _,i in destination.iterrows():
        dicto_destination["{}-{}".format(i.stop_lat, i.stop_lon)] = str(i.stop_id)

    for _,i in origine.iterrows():
        dicto_origine["{}-{}".format(i.stop_lat, i.stop_lon)] = str(i.stop_id)

    from_stop_id = []; to_stop_id = []
    for _, i in base.iterrows():
        dest = dicto_destination["{}-{}".format(i.to_lat, i.to_lon)]
        orig = dicto_origine["{}-{}".format(i.from_lat, i.from_lon)]

        to_stop_id   += [dest]
        from_stop_id += [orig]

    #Rajout de la colonne dans l'objet panda Série
    base["from_stop_id"] = from_stop_id
    base["to_stop_id"] = to_stop_id

    # Change l'ordre des colonnes
    base = base.loc[:, ["unique_request",
    "from_stop_id",
    "from_lon",
    "from_lat",
    "to_stop_id",
    "to_lon",
    "to_lat",
    "time",
    "duration",
    "durationmin",
    "startTime",
    "endTime",
    "walkTime",
    "transitTime",
    "waitingTime",
    "walkDistance",
    "transfers"]]

    # Réécriture du fichier csv
    if overwrite:
        new = sep.join(path_list[:-1]) + sep + name + ".csv"
    else:
        new = sep.join(path_list[:-1]) + sep + name + "_Clean.csv"
    
    base.to_csv(new,sep=",", index=False)



def fixe_Base_arrêts_Bus(path_base, path_bus):
    """
    path base : la path du fichier Base_arret_CTS
    path bus : la path du fichier stops.txt
    Trouve le maximum de numéro de station (dans path_bus) et créée un nouveau fichier de nom:
    anciennom_add_busID.xlsx avec une colonne busID les contenants.

    """

    operating_system = platform.system()
    if operating_system == "Linux":
        sep = "/"
    else:
        sep = "\\"

    path_list = path_base.split(sep)
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path_base, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path_base)
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"

    #On selèctionne les lignes qui ont un identifiant CTBR et pas d'identifiant CTS
    nona  =  base["Code arrÃªt CTBR"].notna()
    nacts = ~base["Code arrÃªt CTS"].notna()
    nona = np.sum((list(nona), list(nacts)), axis = 0) == 2
    base_arret = base[nona]

    f = open(path_bus).read()
    base_bus = np.array([i.split(",") for i in f.split("\n")][1:-1])
    #On enlève toute les sations enfants
    parent   = np.array(base_bus[:,5]) == ''
    base_bus = base_bus[parent]


    noms = [ i[1:-1].lower() for i in base_bus[:,1]]
    dict_nom = dict(zip(noms, base_bus[:,0]))
    base["Bus ID"] = np.nan

    lignes = []

    for i,nc in zip(list(base_arret["Nom"]), base_arret.index):
        nom = dict_nom.get(i.lower())
        if nom :
            base.at[nc,"Bus ID"] = nom
        else :
            lignes += [nc]

    print("Les lignes de la base suivantes n'ont pas d'ID d'arrêt de bus trouvé alors que elle devrait en avoir un : \n",lignes)
    #Changement de la place de la colonne

    a = base.columns.tolist()[:33] + [base.columns.tolist()[-1]] + base.columns.tolist()[33:-1]
    base = base[a]

    base.to_excel("/".join(path_list[:-1])+"/"+name + "_add_busID.xlsx", index=False)

    return
    
    #Partie vestigial pour les correspondances entre les stations par la lattitude et longitude.
    decimal=3
    # Correspondance entre les positions des stations entre base et base_bus
    def cut_dec(n,decimal = 2): #Pour éviter round qui change de le dernier chiffre du nombre
        n, d = str(n).split(".")
        return n + "." + d[:decimal]


    keys = ["{}-{}".format(cut_dec(i[1]),cut_dec(i[0])) for i in b[:,2:4]]
    values = b[:,0]
    dictio = dict(zip(keys, values))

    bus_keys = list(zip(list(base_bus["Longitude"]), list(base_bus["Latitude"])))
    bus_keys = ["{}-{}".format(cut_dec(i[0]), cut_dec(i[1])) for i in bus_keys]


    c, d = np.unique(keys, return_counts=True)

    print(d)
    print(d[0])
    c[0]

    t1 = np.where(np.array(keys) == '48.11-7.54')[0]
    print(values[t1])