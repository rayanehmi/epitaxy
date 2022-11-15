from nptdms import TdmsFile
import matplotlib.pyplot as plt

# Modifier le path : mettre le dossier dans lequel se trouvent les données TDMS
path = "C:/Users/Rayane/Documents/GitHub/epitaxy/Données/Série A1417 - A1425 TDMS/"

# Renvoie une colonne de données
def readTDMS(fileName, groupName, channelName='Y'):
    tdms_file = TdmsFile.read(fileName)
    group = tdms_file[groupName]
    channel = group[channelName]
    channel_data = channel[:]
    # channel_properties = channel.properties
    return channel_data

# Plot un fichier TDMS
def plotTDMS(fileName):
    data = readTDMS(path+fileName,'Curvature (km-1)')
    time = readTDMS(path + fileName, 'Time (s)', 'Time (s)')

    plt.plot(time,data)
    plt.title("Courbature en fonction du temps")
    plt.show()
    return

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    plotTDMS('A1418/A1418 Curvature.tdms')
