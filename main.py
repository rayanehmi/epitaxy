# import lambda_extractor
from joblib import dump
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

import slope_curv_extractor
import temp_extractor


def train_and_test(shuffle=True):
    # curv
    curv_file = open("labelled_data/curv.txt", "r")
    curv_slopes_set = curv_file.readlines()
    for i in range(len(curv_slopes_set)):
        curv_slopes_set[i] = float(curv_slopes_set[i].rstrip("\n"))

    # temperature
    temp_set = [700 for i in range(len(curv_slopes_set))]

    # periods
    periods_file = open("labelled_data/periods.txt", "r")
    period_set = periods_file.readlines()
    for i in range(len(period_set)):
        period_set[i] = float(period_set[i].rstrip("\n"))

    # labels
    labels_file = open("labelled_data/labels.txt", "r")
    label_set = labels_file.readlines()
    for i in range(len(label_set)):
        label_set[i] = float(label_set[i].rstrip("\n"))

    # Prep the inputs
    X = []
    for i in range(len(label_set)):
        X.append([curv_slopes_set[i], temp_set[i], period_set[i]])
    y = label_set

    score_list = []
    error_list = []

    # Train and test (multiple times)
    for i in range(25):

        # split dataset
        if shuffle:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
        else:
            X_train = X[:-12]
            X_test = X[-12:]
            y_train = y[:-12]
            y_test = y[-12:]

        # Train
        model = RandomForestRegressor()
        model.fit(X_train,y_train)

        # Predictions
        predicts = model.predict(X_test)
        error = []
        for i in range(len(X_test)):
            error.append(abs(predicts[i] - y_test[i]))
            print("real :", y_test[i], ", predicted :", predicts[i], ", diff :", abs(predicts[i] - y_test[i]))
        score_list.append(model.score(X_test, y_test))
        error_list.append(sum(error) / len(error))
        print("model score :",model.score(X_test,y_test))
        print("mean error :", sum(error)/len(error))

    # Results
    print("\n")
    print("Mean score :",sum(score_list) / len(score_list))
    print("Mean error :",sum(error_list) / len(error_list))
    return


def dump_temp_features():
    code_list = ["A1418,""A1419", "A1420", "A1421", "A1422"]
    temp_features = temp_extractor.start_all(code_list, doPrint=False, doPlot=False)
    print(temp_features)
    dump(temp_features, "./dumps/temperature_features.joblib")
    return


def dump_slope_features():
    code_list = ["A1418", "A1419", "A1420", "A1421", "A1422"]
    slope_features = slope_curv_extractor.start_all_slope(code_list, doPrint=True, doPlot=False)
    print(slope_features)
    dump(slope_features, "./dumps/slope_features.joblib")
    return


def main():
    train_and_test(shuffle=True)
    return


if __name__ == "__main__":
    main()
