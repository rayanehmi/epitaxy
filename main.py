import tdms_reader
import lambda_extractor
import temp_extractor
import pickle
import matplotlib.pyplot as plt
import numpy as np
from database import Layer, Step

def main():


def main():
    # Load the data
    with open("database.pkl", "rb") as file:
        data = pickle.load(file)

    for exp in data:
        print("Experience number",exp.code,"...")
        for step in exp.step_list:
            if isinstance(step, Layer):
                print("Step",step.step_number)
                print(step.rel_start)
                print(step.rel_end)
                input()

    return


if __name__ == "__main__":
    main()
