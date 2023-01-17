import mbe_get_steps
import tdms_converter
import tdms_extraction
import pickle
import numpy as np
import matplotlib.pyplot as plt
from dataset_env import dataset_env, DatasetEnv
from pickle_results import pickle_results_main
from database import Layer, Step


def main():
    #mbe_get_steps.get_mbe_steps_main()

    # dataset_env.print_experiment_list()
    # DatasetEnv.clean_folder(dataset_env.tdms_output_folder)

    # # NE FONCTIONNE QUE SI ON MODIFIE LE CODE SOURCE venv/lib/python3.9/site-packages/nptdms/tdms_segment.py/
    # # if self.data_type isfft types.ExtendedFloat:
    # #     self.data_type.size = 8
    # #     self.data_type = types.DoubleFloat
    # tdms_converter.convert_tdms_files()

    #tdms_extraction.tdms_extraction_main()

    # dataset_env.print_experiment_list()
    with open('database.pkl', 'rb') as db:
        data = pickle.load(db)
        print(data)
        # for i in range(len(data)):
        #     exp = data[i]
        #     step = exp.step_list[7]
            #print("Experience : "+ str(i) +", pente de la step 7 :",step.curvature_slope) 
    #exp = data[0] #A1417

    #step0 = exp.step_list[0]
    #wavelength = 0
    # Reflectivity for first step and first wavelength
    # reflectivity0 = list(step0.reflectivity.values())[wavelength]
    # print(reflectivity0)
    # pickle_results_main(dataset_env.experiments)

    def mean_temp(step: Step,doPlot=False):
        x = []
        y = []
        if isinstance(step,Layer):
            if len(step.wafer_temperature) != 0:
                temp_t = step.wafer_temperature
                for tuple in temp_t:
                    x.append(tuple[0])
                    y.append(tuple[1])

                coeff = np.polyfit(x,y,1)
                if doPlot:
                    print(y)
                    plt.plot(x,y)
                    print("Temp moyenne de la step : ",np.mean(x))
                    plt.title("Temp step "+str(step.step_number))
                    plt.show()
    
    exp = data[0]
    for step in exp.step_list:
        mean_temp(step,doPlot=True)

    # Extracts the slope of a step if it is a Layer with non-null curvature data
    def extract_slope_step(step, doUpdate=True, doPlot=False):
         
        x = []
        y = []
        
        if isinstance(step,Layer):
            if len(step.curvature) != 0:
                curv_t = step.curvature
                for tuple in curv_t:
                    x.append(tuple[0])
                    y.append(tuple[1])

                coeff = np.polyfit(x,y,1)
                if doPlot:
                    plt.plot(x,y)
                    plt.plot(x,(coeff[0]*np.array(x)+coeff[1]),'-r')
                    plt.title("Curv step "+str(step.step_number))
                    plt.show()
                if doUpdate == True:
                    step.curvature_slope = coeff[0]
   
        return coeff[0]


    def extract_slope_all(data,numexp,doUpdate, doPlot):
        exp = data[numexp]
        for step in exp.step_list:
            x = []
            y = []
            
            if isinstance(step,Layer):
                if len(step.curvature) != 0:
                    curv_t = step.curvature
                    for tuple in curv_t:
                        x.append(tuple[0])
                        y.append(tuple[1])

                    coeff = np.polyfit(x,y,1)
                    if doPlot:
                        plt.plot(x,y)
                        plt.plot(x,(coeff[0]*np.array(x)+coeff[1]),'-r')
                        plt.title("Curv step "+str(step.step_number))
                        plt.show()
                    if doUpdate == True:
                        step.curvature_slope = coeff[0]
        if doUpdate == True:
            with open("database.pkl", "wb") as f:
                pickle.dump(data,f)
                print("Donnees exportees avec succes (exp numero "+str(numexp)+")")
        return

    # for i in range(3,len(data)):
    #     extract_slope_all(data,i, False, False)


    def extract_lambda(data,numexp,step_n,wavelength_n):
        exp = data[numexp]
        step = exp.step_list[step_n]
        reflectivity_t = list(step.reflectivity.values())[wavelength_n]
        ref = []
        for tuple in reflectivity_t:
        # On ajoute le deuxième élément du tuple à la liste
            ref.append(tuple[1])
        
        
        fft = np.fft.fft(ref)
        periodicity = np.argmax(np.abs(fft))
        plt.plot(ref)
        plt.show()
        return periodicity
    

    def extract_lambda_all(data,numexp,wavelength_n):
        exp = data[numexp]
        ref = []
        
        for step in exp.step_list:
            step_ref = []
            print(step.step_number)
            if isinstance(step, Layer):
                if len(step.reflectivity.values()) != 0:
                    reflectivity_t = list(step.reflectivity.values())[wavelength_n]
        
                for tuple in reflectivity_t:
        # On ajoute le deuxième élément du tuple à la liste
                    ref.append(tuple[1])
                    step_ref.append(tuple[1])
            if not len(step_ref) == 0:
                plt.plot(step_ref)
                plt.title("Step "+str(step.step_number))
                plt.show()
                fft = np.fft.fft(step_ref)
                plt.scatter(np.arange(len(fft)),fft)
                plt.title("FFT Step "+str(step.step_number))
                plt.show()
        
        
        fft = np.fft.fft(ref)


        periodicity = np.argmax(np.abs(fft))
        plt.plot(ref)

        
        plt.title("Total steps")
        plt.show()
        plt.scatter(np.linspace(0,985,985),fft)
        plt.title("Total FFT")
        plt.show()

        return periodicity


    #period = extract_lambda_all(data,0,850)
    #print(period)



if __name__ == '__main__':
    main()
