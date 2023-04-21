import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def filtreTime(path, max = 60*60*2, overwrite = False):
    """
    Filtre les sorties de l'algorithme des plus courts chemins
    On enlève les lignes avec duration == NaN et supèrieur à 'max' en seconde
    
    path      : le chemin du fichier xlsx ou csv
    overwrite : Si True alors ré-écrit le fichier d'origine. Sinon création
                d'un nouveau fichier avec l'extension _Conditionfiltred.csv
        
    """

    path_list = path.split("/")
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
        new = "/".join(path_list[:-1]) + "/" + name + ".csv"
    else:
        new = "/".join(path_list[:-1]) + "/"+ name + "_Timefiltred.csv"
    base.to_csv(new,sep=",", index=False)



def filtreCondition(path, conditions, overwrite = False):
    """
    path       : Le chemin du fichier xlsx ou csv
    conditions : Liste des conditions qui doivent être à Oui
    overwrite  : Si True alors ré-écrit le fichier d'origine. Sinon création
                 d'un nouveau fichier avec l'extension _Conditionfiltred.csv        
    """

    path_list = path.split("/")
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path)
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"

    conditions_possibles = base.keys()[(base == "Oui").any()]

    taken = []
    for condition in conditions:
        #Si jamais la condition ne se trouve pas dans les conditions possible -> Error
        if condition not in conditions_possibles:
            print("Error : Condition introuvable, veuillez vérifier que l'orthographe de la condition est le même que celui de la colonne")
        else:
            taken += [np.array(base[condition]) == "Oui"]

    base = base[np.sum(taken, axis = 0) == 2]

    if overwrite:
        new = "/".join(path_list[:-1]) + "/" + name + ".csv"
    else:
        new = "/".join(path_list[:-1]) + "/" + name + "_Conditionfiltred.csv"
    
    base.to_csv(new,sep=",", index=False)




def GenericClean(path, path_POI = None, path_Mailles = None, overwrite= False):
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

    path_list = path.split("/")
    name, format = tuple(path_list[-1].split("."))

    if format == "csv":
        base = pd.read_csv(path, delimiter=",")
    elif format =="xlsx":
        base = pd.read_excel(path, delimiter=",")
    else : 
        raise "Error : Format de fichier non reconnut (csv ou xlsx)"

    if path_POI is not None:
        destination = pd.read_csv(path_POI)
    else:
        destination = pd.read_csv("/".join(path_list[:-1])+"/POIStras.csv")

    if path_Mailles is not None: 
        origine = pd.read_csv(path_Mailles)
    else:
        origine = pd.read_csv("/".join(path_list[:-1])+"/Mailles_Stras.csv")

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
    from_stop_id = []; to_stop_id = []
    for _, i in base.iterrows():
        to_stop_id += [destination[(destination.stop_lat == i.to_lat) &(destination.stop_lon == i.to_lon)].stop_id.iloc[0]]
        from_stop_id   += [origine[(origine.stop_lat == i.from_lat)&(origine.stop_lon == i.from_lon)].stop_id.iloc[0]]

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
        new = "/".join(path_list[:-1]) + "/" + name + ".csv"
    else:
        new = "/".join(path_list[:-1]) + "/" + name + "_Clean.csv"
    
    base.to_csv(new,sep=",", index=False)