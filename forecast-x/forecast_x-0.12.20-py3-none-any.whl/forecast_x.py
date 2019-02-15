class forecast: 
    """ Class to forecast time series using multiple naive models.

    Parameters
    ----------
    time series: a Python list containing exclusively numbers.
        frequency: a Python integer. Used to specify time series
			pattern: 
			 - 12 for monthly.
			 - 7 for weekly.
			 - 365 for daily.
        ahed: A Python integer. Used to specify number of periods
			 towards the future.


    """

    TRAINING_SET = [0.6, 0.65, 0.7, 0.75, 0.8]
    TEST_SET = [0.4, 0.35, 0.3, 0.25, 0.2]

    fcst = None
    fitted = None
    test = None
    err = 0
    po = 0
	
    def __init__(self, time_series, f, h):
        if not isinstance(time_series, list):
            raise ValueError("Time Series must be a list type value")
        if len(time_series)  < 3:
            raise TypeError("Time Series must be longer than 3 observations")  
            
        self.time_series = time_series
        self.f = f
        self.h = h
        self.series_len = len(self.time_series)
        n = self.__class__.__name__
        self.method_list = [func for func in dir(eval(n)) if callable(getattr(eval(n), func)) and func[0]!='__' and func[:5] == 'model']
        
    def __len__(self):
        return self.series_len

    def err_predict(self, obs, est):
        """ Returns the RMSE of observed vs predicted """
        error_pred = [a - b for a, b in zip(obs, est)]
        total_error = [(number)** 2 for number in error_pred]
        try:
            result = (sum(total_error) / len(total_error)) ** (1/2)
        except ZeroDivisionError as err:
            print('run-time error:', err)
            result = 'NA'
        return result
    
    def model_naive(self):
        """ Returns time series' last observation value """ 
        allow = 1
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
		
        x = self.time_series[:y_hat]
        self.fitted = [x[-1] for i in range(x_hat)]
        result.append(self.fitted)
        
        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        self.fcst = [self.time_series[-1] for i in range(self.h)]
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_seas_naive(self):
        """ Returns time series' previous seasonal period """
        allow = self.f
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            x.append(x[-self.f])
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            y.append(y[-self.f])
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
		
        result.append(self.series_len >= allow)
        return result

    def model_mean_two_periods(self):
        """ Returns mean from last two periods """
        allow = 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            re = sum(x[-2:])/2
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = sum(y[-2:])/2
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_mean_three_periods(self):
        """ Returns mean from last three periods """
        allow = 3
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
         
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            re = sum(x[-3:])/3
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = sum(y[-3:])/3
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_half_seas_mean(self):
        """ Returns mean from last mid seasonal period """
        allow = self.f / 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        half_freq = int(self.f / 2)
        while i < x_hat:
            re = sum(x[-half_freq:])/half_freq
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = sum(y[-half_freq:])/half_freq
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_seas_period_mean(self):
        """ Returns the mean of the total observations in the first
            seasonal period
        """
        allow = self.f
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            re = sum(x[-self.f:])/self.f
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = sum(y[-self.f:])/self.f
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_double_seas_mean(self):
        """ Returns the mean of the total observations in the two
            seasonal periods
        """
        allow = self.f * 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        doub_freq = self.f * 2
        while i < x_hat:
            re = sum(x[-doub_freq:])/doub_freq
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = sum(y[-doub_freq:])/doub_freq
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_seas_growth(self):
        """ Returns the mean between previous seasonal periods """
        allow = self.f * 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        doub_freq = self.f * 2
        while i < x_hat:
            re = (x[-doub_freq] + x[-self.f]) / 2
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            re = (y[-doub_freq] + y[-self.f]) / 2
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_expo_weighted(self):
        allow = self.f * 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            xx = x[-self.f] * 0.4
            yy = (sum(x[-3:]) / 3 )  * 0.6
            x.append(xx + yy)
            i += 1
            
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = y[-self.f] * 0.4
            yy = (sum(y[-3:]) / 3 )  * 0.6
            y.append(xx + yy)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_threefith_mean(self):
        """ Returns mean between the mean from the last three
        observations and the mean from the last five observations """
        allow = 5
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            xx = sum(x[-3:]) / 3
            yy = sum(x[-5:]) / 5
            re = (xx + yy) / 2
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-3:]) / 3
            yy = sum(y[-5:]) / 5
            re = (xx + yy) / 2
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_multi_seas_mean(self):
        allow = self.f / 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        half_seas = int(self.f / 2)
        while i < x_hat:
            xx = sum(x[-self.f:]) / self.f
            yy = sum(x[-half_seas:]) / half_seas
            re = (xx + yy) / 2
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)
 
        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-self.f:]) / self.f
            yy = sum(y[-half_seas:]) / half_seas
            re = (xx + yy) / 2
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_seas_double_mean_growth(self):
        allow = self.f + 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        half_seas = int(self.f / 2)
        while i < x_hat:
            xx = sum(x[-self.f:]) / self.f
            yy = sum(x[-half_seas:]) / half_seas
            re = x[-self.f] * (yy / xx)
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-self.f:]) / self.f
            yy = sum(y[-half_seas:]) / half_seas
            re = y[-self.f] * (yy / xx)
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_grand_mean(self):
        """ Returns grand mean between multiple seasonal periods """
        allow = self.f * 3
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        half_seas = int(self.f / 2)
        double_seas = self.f * 2
        while i < x_hat:
            xx = sum(x[-self.f:]) / self.f
            yy = sum(x[-half_seas:]) / half_seas
            zz = sum(x[-double_seas:]) / double_seas
            re = (xx + yy + zz)/ 3
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-self.f:]) / self.f
            yy = sum(y[-half_seas:]) / half_seas
            zz = sum(y[-double_seas:]) / double_seas
            re = (xx + yy + zz)/ 3
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_smooth_grand_mean(self):
        allow = self.f * 3
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        half_seas = int(self.f / 2)
        double_seas = self.f * 2
        while i < x_hat:
            xx = sum(x[-self.f:]) / self.f
            yy = sum(x[-half_seas:]) / half_seas
            zz = sum(x[-double_seas:]) / double_seas
            re = x[-self.f] * 0.6 + ((xx + yy + zz)/ 3) * 0.4
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-self.f:]) / self.f
            yy = sum(y[-half_seas:]) / half_seas
            zz = sum(y[-double_seas:]) / double_seas
            re = y[-self.f] * 0.6 + ((xx + yy + zz)/ 3) * 0.4
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_smooth_double_seas_naive(self):
        """ Returns weighted seasonal mean of given time series """
        allow = self.f * 3
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        double_seas = self.f * 2
        while i < x_hat:
            xx = x[-double_seas]
            yy = x[-self.f]
            re = (yy * 0.6) + (xx * 0.4)
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = y[-double_seas]
            yy = y[-self.f]
            re = (yy * 0.6) + (xx * 0.4)
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_truncated_mean(self):
        """ Returns truncated mean of given time series """
        allow = self.f + 2
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            xx =  sum(x[-self.f:]) / self.f
            _min = min(x[-self.f])
            _max = max(x[-self.f])
            re = (xx - _min - _max) / (self.f - 2) 
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx =  sum(y[-self.f:]) / self.f
            _min = min(y[-self.f])
            _max = max(y[-self.f])
            re = (xx - _min - _max) / (self.f - 2) 
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_harmonic_mean(self):
        """ Returns harmonic mean of given time series """
        allow = 4
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            xx = 1 / x[-1]
            yy = 1 / x[-2]
            zz = 1 / x[-3]
            re = ((xx + yy + zz) ** -1 ) / (len([xx,yy,zz]) ** -1)
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = 1 / y[-1]
            yy = 1 / y[-2]
            zz = 1 / y[-3]
            re = ((xx + yy + zz) ** -1 ) / (len([xx,yy,zz]) ** -1)
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def model_heronian_mean(self):
        """ Returns heronian mean of given time series """
        allow = self.f + 1
        result = []
        y_hat = int(round(self.series_len * self.TRAINING_SET[self.po],0))
        x_hat = int(self.series_len - y_hat)
        
        x = self.time_series[:y_hat]
        i = 0
        while i < x_hat:
            xx = sum(x[-self.f:]) / self.f
            yy = x[-self.f]
            re = (1/3) * (xx + ((xx * yy) ** 1/2) + yy )
            x.append(re)
            i += 1
        del x[:y_hat]
        self.fitted = x   
        result.append(self.fitted)

        self.test = self.time_series[x_hat * -1:]
        
        self.err = self.err_predict(self.test, self.fitted)
        result.append(self.err)
        
        i = 0
        y = self.time_series[:]
        while i < self.h:
            xx = sum(y[-self.f:]) / self.f
            yy = y[-self.f]
            re = (1/3) * (xx + ((xx * yy) ** 1/2) + yy )
            y.append(re)
            i += 1
        del y[:self.series_len]
        self.fcst = y   
        result.append(self.fcst)
        
        result.append(self.series_len >= allow)
        return result

    def get_forecast(self, model):
        """ Returns forecast based on given  model name """
        elem = 2
        x = eval('self.' + model + '()')
        return x[elem]

    def eval_model(self, method):
        accuracy = 1
        valid_model = 3
        try:
            if eval('self.' + method + '()[' + str(valid_model) +']') == True:
                return eval('self.' + method + '()[' + str(accuracy) + ']')   
        except:
            pass
    
    def optimizer(self):
        """ Returns dictionary with all prediction model errors """
        models = {}

        for m in self.method_list:
            x = len(self.TRAINING_SET)
            y =[]
            i = 0
			
            while i < x:
                self.po = i
                y.append(self.eval_model(m))
                i += 1
            models[m] = y
        del y
        return models

    def best_model(self):
        """ Returns best fitting model (Model Name) for given time series """
        def_model = 'model_naive'
        best = {}
        model = self.optimizer()
		
        for k, v in model.items():
            try:
                best[k] = sum(v) / len(v)
            except:
                pass

        min_v = min(best.values())
        x = ''.join([k for k, v in best.items() if v == min_v])
        if len(x) > max([len(z) for z in self.method_list]):
            del min_v
            return def_model
        else:
            del min_v  
            return x
