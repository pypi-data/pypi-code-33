import numpy as np
import pandas as pd


class ADFunctionalBase:
    def __init__(
        self,
        base_pipeline,
        train_window_size=None,
        growing_train_window=False,
        predict_window_size=None,
        num_lags=0,
        outlier_filtering="3sigma",
    ):

        self.base_pipeline = base_pipeline
        self.train_size = train_window_size
        self.predict_size = predict_window_size
        self.growing_train_window = growing_train_window
        self.filtering = outlier_filtering
        self.num_lags = 0

    def _fit_window(self, data):
        y = data[self.target_var]
        X = data.drop([self.target_var, "timestamp"], axis=1)

        self.base_pipeline.fit(X, y)

    def _predict_window(self, data):
        T = data.timestamp.values
        y_true = data[self.target_var].values
        X = data.drop([self.target_var, "timestamp"], axis=1)

        y_pred = self.base_pipeline.predict(X)

        self.residual.loc[T, "Predicted"] = y_pred
        self.residual.loc[T, "Residual"] = y_true - y_pred

        return 0

    def _calc_score(self):
        L2 = np.sum((1.0 / len(self.residual)) * np.abs(self.residual["Residual"].values) ** 2) ** 0.5

        self.score = {}
        self.score["L2"] = L2

        return 0

    def fit(self, data, target_var):
        self.target_var = target_var
        self.residual = pd.DataFrame(columns=["Predicted", "Residual"], index=data.timestamp)

        T = data.timestamp.values
        Tstart = T[0]
        Tstop = T[-1]
        DT_training = int(pd.Timedelta(self.train_size).total_seconds() * 1000)
        DT_predict = int(pd.Timedelta(self.predict_size).total_seconds() * 1000)

        Tcurrent = Tstart + DT_training
        while Tcurrent < Tstop:
            if self.growing_train_window:
                train_start = Tstart
            else:
                train_start = Tcurrent - DT_training
            train_end = Tcurrent
            predict_start = Tcurrent
            predict_end = Tcurrent + DT_predict

            print("Training period:", pd.to_datetime(train_start, unit="ms"), pd.to_datetime(predict_end, unit="ms"))

            training_window = (data.timestamp > train_start) & (data.timestamp < train_end)
            predict_window = (data.timestamp > predict_start) & (data.timestamp < predict_end)

            data_train = data[training_window]
            data_predict = data[predict_window]

            self._fit_window(data_train)
            self._predict_window(data_predict)

            Tcurrent = predict_end

        self.valid_to = Tstop + DT_predict

        self.residual["timestamp"] = self.residual.index
        self.residual = self.residual.reset_index(drop=True)
        self.residual = self.residual.fillna(value=0.0)
        self._calc_score()

        return self.score

    def predict(self, data):
        print("not implemented")
        return -1
