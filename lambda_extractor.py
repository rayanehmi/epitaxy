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
    delta = time_data[1] - time_data[0] / len(all_wavelengths["0"][:])

    while i < len(all_wavelengths):
        reflectivities.append(all_wavelengths[str(i)][:])

        # Debug
        if plot_graphs:
            x_axis = np.linspace(0, time_data[1] - time_data[0], len(all_wavelengths[str(i)][:]))
            plt.plot(x_axis, all_wavelengths[str(i)][:], label = "Wavelength number " + str(i))

        i += step


    periodicity_list = []
    for reflectivity in reflectivities:
        for method in ["fft", "autocorr"]:
            periodicity = find_periodicity_methods(reflectivity, method)
            periodicity_list.append(periodicity)

    periodicity_list = [i for i in periodicity_list if i != 0]  # Remove failures
    periodicity_list = sorted(periodicity_list)

    # Convert to frequency
    time_per_wavelength = time_data[1] - time_data[0]
    number_of_points = len(all_wavelengths["0"][:])
    delta_t = time_per_wavelength / number_of_points
    for i in range(len(periodicity_list)):
        periodicity_list[i] = periodicity_list[i] / time_per_wavelength
    median_periodicity = periodicity_list[len(periodicity_list) // 2]
    print("Periodicity list:")
    print(periodicity_list)

    if plot_graphs:
        plt.title("Amplitude for different wavelengths. Period found : "+str(round(median_periodicity)))
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
