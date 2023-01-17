import tdms_reader
import numpy as np
from scipy.signal import fftconvolve
import numpy as np
import matplotlib.pyplot as plt


# Takes a reflectivity tdms file and extracts a period
# Uses autocorrelation and FFT to check num_wavelength different wavelengths
# Returns the median wavelength found
def find_periodicity(tdms_data, num_wavelengths=10, plot_graphs=False):
    if num_wavelengths < 1:
        raise ValueError(f'Not enough wavelengths to test')

    # Get the reflectivity values for each wavelength
    # all_wavelengths = tdms_data.groups()
    all_wavelengths = tdms_data["Normalized R"]
    # print(all_wavelengths["1"][:])
    if num_wavelengths > len(all_wavelengths):
        raise ValueError(f'Too many wavelengths to test')

    # Select n equally spaced wavelengths
    step = len(all_wavelengths) // num_wavelengths
    # print(len(all_wavelengths))
    i = step
    reflectivities = []

    # Find the time step
    time_data = tdms_reader.read_channel(tdms_data, "Reflectivity Data", "Time (s)")
    print(len(time_data))
    print(time_data[-1])
    print(time_data[0])
    sampling_rate = (time_data[-1]-time_data[0])/len(time_data)
    print("Sampling rate:",sampling_rate)

    while i < len(all_wavelengths):
        reflectivities.append(all_wavelengths[str(i)][:])

        # Debug
        if plot_graphs:
            plt.plot(time_data, all_wavelengths[str(i)][:], label="Wavelength number " + str(i))

        i += step

    periodicity_list = []
    for reflectivity in reflectivities:
        for method in ["fft", "autocorr"]:
            periodicity = find_periodicity_methods(reflectivity, method)
            periodicity_list.append(periodicity)

    periodicity_list = [i for i in periodicity_list if i != 0]  # Remove failures
    periodicity_list = sorted(periodicity_list)

    # Convert to frequency
    number_of_points = len(time_data)
    for i in range(len(periodicity_list)):
        periodicity_list[i] = periodicity_list[i]
    median_periodicity = periodicity_list[len(periodicity_list) // 2]
    print("Periodicity list:")
    print(periodicity_list)

    if plot_graphs:
        plt.title("Amplitude for different wavelengths. Period found : " + str(round(median_periodicity)))
        plt.legend()
        plt.show()

    return median_periodicity


def find_periodicity_methods(reflectivity_array, method):
    # Find the periodicity for the current wavelength using the specified method
    if method == 'fft':
        # Compute the FFT of the reflectivity values
        fft = np.fft.fft(reflectivity_array)
        # Find the periodicity by finding the index of the maximum magnitude in the FFT spectrum
        periodicity = np.argmax(np.abs(fft))

    elif method == 'autocorr':
        # Compute the autocorrelation of the reflectivity values
        autocorr = fftconvolve(reflectivity_array, reflectivity_array[::-1], mode='full')
        # Find the periodicity by finding the index of the maximum value in the autocorrelation function
        periodicity = np.argmax(autocorr)

    else:
        raise ValueError(f'Invalid method: {method}')
    return periodicity




def extract_lambda(data, numexp, step_n, wavelength_n):
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

def extract_lambda_all(data, numexp, wavelength_n):
    exp = data[numexp]
    ref = []

    for step in exp.step_list:
        step_ref = []
        print(step.step_number)
        if isinstance(step, Layer):
            print(step.step_number)
            if len(step.reflectivity.values()) != 0:
                reflectivity_t = list(step.reflectivity.values())[wavelength_n]

            for tuple in reflectivity_t:
                # On ajoute le deuxième élément du tuple à la liste
                ref.append(tuple[1])
                step_ref.append(tuple[1])
    # if not len(step_ref) == 0:
    # plt.plot(step_ref)
    # plt.title("Step "+str(step.step_number))
    # plt.show()

    fft = np.fft.fft(ref)
    print("fft :", fft)

    periodicity = np.argmax(np.abs(fft))
    plt.plot(ref)

    x = 0
    for step in exp.step_list:
        if isinstance(step, Layer):
            if len(step.reflectivity.values()) != 0:
                x += len(reflectivity_t)
        plt.vlines(x, ymin=1000, ymax=2000, colors='red', linestyles='dashed')

    plt.title("Total steps")
    plt.show()
    plt.scatter(np.linspace(0, 985, 985), fft)
    plt.title("Total FFT")
    plt.show()

    return periodicity

    period = extract_lambda_all(data, 0, 850)
    print(period)
