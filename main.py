
# import lambda_extractor
import temp_extractor
import slope_curv_extractor
import csv
import pickle
from joblib import dump,load
import matplotlib.pyplot as plt
import numpy as np
from database import Layer, Step

def main():
    #temp_features = load("./dumps/temperature_features.joblib")
    slope_curv_features = load("./dumps/slope_features.joblib")
    for elem in slope_curv_features[-1]:
        print(str(elem))
    
    return

def dump_temp_features():
    code_list = ["A1418,""A1419","A1420","A1421","A1422"]
    temp_features = temp_extractor.start_all(code_list, doPrint=False, doPlot=False)
    print(temp_features)
    dump(temp_features,"./dumps/temperature_features.joblib")
    return

def dump_slope_features():
    code_list = ["A1418","A1419","A1420","A1421","A1422"]
    slope_features = slope_curv_extractor.start_all_slope(code_list,doPrint=True,doPlot=False)
    print(slope_features)
    dump(slope_features,"./dumps/slope_features.joblib")
    return

if __name__ == "__main__":
    main()
