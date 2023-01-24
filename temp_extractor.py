import csv
import pickle
from database import Layer, Step
import matplotlib.pyplot as plt

path = "/home/rhachemi/GitHub/Epitaxie/epitaxy/wafer/"

# Extracts temporal data for an experiment code from csv files
# Get the csv files with Excel tdms addon -> save as CSV (";" separated)
# Returns two lists, time data and PCST temperature data
def extract_csv_exp(exp_code, preclean_data=True, doPrint=False, doPlot=False):

    # Load time data
    t_wafer = open(path+"time_"+exp_code+".csv")
    time = csv.reader(t_wafer, delimiter=";")
    next(time) # Skip header
    time_list = []
    for t in time:
        time_list.append(float(t[0].replace(",",".")))

    # Load wafer data
    w_wafer = open(path+"wafer_"+exp_code+".csv")
    wafer = csv.reader(w_wafer, delimiter=";")
    next(wafer) # Skip header
    wtemp_list = []
    for wt in wafer:
        wtemp_list.append(float(wt[0].replace(",",".")))

    if preclean_data:
        if doPrint:
            print("Old length :",len(time_list))
        # Delete duplicate lines
        i = 0
        while True:
            if time_list[i] == time_list[i+1]:
                del time_list[i+1]
                del wtemp_list[i+1]
            else:
                i+=1
            if i>=len(time_list)-1:
                break
        if doPrint:
            print("New length :",len(time_list))

    if doPlot:
        plt.plot(time_list,wtemp_list)
        plt.title("Wafer temperature for experiment "+exp_code)
        plt.show()

    return time_list,wtemp_list


# Returns the average value of 
def get_mean_temp_step(time_data, temp_data, start_time, end_time):
    temp_data_in_range = [temp_data[i] for i in range(len(time_data)) if start_time <= time_data[i] <= end_time]
    average = sum(temp_data_in_range) / len(temp_data_in_range) if temp_data_in_range else None
    return average


# Call with doPrint = True for debugging
# Do not forget to update path to Time and Temperature data
def start_all(code_list, doPrint=False, doPlot=False):

    features_list = []

    # Load the data
    if doPrint:
        print("Loading database (may take some time)...")
    file =  open("database.pkl", "rb")
    data = pickle.load(file)
    if doPrint:
        print("Database loaded successfully !")

    for exp in data: # Iterate on each experiment in the dataset
        features_of_exp = []
        code = exp.code # Get exp number (code) as a string. example : "A1417"
        if code not in code_list:
            continue
        if doPrint:
            print("Starting temperature extraction on experience number",exp.code,"...")
        time_data, temp_data = extract_csv_exp(code, doPrint=doPrint,doPlot=doPlot)

        for step in exp.step_list: # We iterate on each step...
            if isinstance(step, Layer): # ... but only if they are meaningful (Layer)
                if doPrint:
                    print("Analyzing step number",step.step_number)
                average_temp = get_mean_temp_step(time_data, temp_data, step.rel_start, step.rel_end)
                features_of_exp.append(average_temp)   
        features_list.append(features_of_exp)
    return features_list



