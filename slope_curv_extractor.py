import pickle
from database import Layer, Step
import matplotlib.pyplot as plt
import numpy as np

def start_all_slope(code_list,doPrint=False, doPlot=False):
    features_list = []
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
            print("Starting slope curvature extraction on experience number",exp.code,"...")
        for step in exp.step_list: # We iterate on each step...
            if isinstance(step,Layer):
                slop_step = extract_slope_step(step,doPlot)
                features_of_exp.append(slop_step)
        features_list.append(features_of_exp)
    return features_list


def extract_slope_step(step, doPlot=False):
    x = []
    y = []
    
    if len(step.curvature) != 0:
        curv_t = step.curvature
        for tuple in curv_t:
            x.append(tuple[0])
            y.append(tuple[1])

        coeff = np.polyfit(x,y,1)
        print("----La Pente vaut----")
        print(coeff[0])
        if doPlot:
            plt.plot(x,y)
            plt.plot(x,(coeff[0]*np.array(x)+coeff[1]),'-r')
            plt.title("Curv step "+str(step.step_number))
            plt.show()


    return coeff[0]