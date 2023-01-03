from nptdms import TdmsFile
import matplotlib.pyplot as plt

# Modifier le path : mettre le dossier dans lequel se trouvent les données TDMS
path = "C:/Users/Rayane/Desktop/Epitaxy/Données/Données/Série A1417 - A1425 TDMS/"


# Charge le fichier TDMS dans la mémoire de Python
def load_tdms(filename):
    return TdmsFile.read(path+filename)


# Lit le channel "channelName" du groupe "groupName" du fichier tdms_file chargé en mémoire.
# Renvoie une liste correspondant aux données
def read_channel(tdmsFile, groupName, channelName):
    group = tdmsFile[groupName]
    channel = group[channelName]
    channel_data = channel[:]
    return channel_data


# Plot un fichier TDMS à partir de son nom
def plot_tdms(fileName, xAxisGroup, xAxisName, yAxisGroup, yAxisName):
    file = load_tdms(path + fileName)
    data = read_channel(file, xAxisGroup, xAxisName)
    time = read_channel(file, yAxisGroup, yAxisName)

    plt.plot(time, data)
    plt.title(xAxisName, "vs", yAxisName)
    plt.show()
    return
