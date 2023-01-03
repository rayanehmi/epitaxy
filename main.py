import tdms_reader
import lambda_extractor


def main():
    reflectivity = tdms_reader.load_tdms("A1417/A1417 Reflectivity.tdms")
    period = lambda_extractor.find_periodicity(reflectivity,5,True)
    print("Period found:", period)
    return


if __name__ == "__main__":
    main()
