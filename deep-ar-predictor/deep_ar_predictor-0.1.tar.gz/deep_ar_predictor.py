#!/usr/bin/env python
# coding: utf-8

# In[6]:


import sagemaker


# In[7]:


class DeepARPredictor(sagemaker.predictor.RealTimePredictor):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, content_type=sagemaker.content_types.CONTENT_TYPE_JSON, **kwargs
        )

    def predict(
        self,
        ts,
        cat=None,
        dynamic_feat=None,
        num_samples=100,
        return_samples=False,
        quantiles=["0.1", "0.5", "0.9"],
    ):
        prediction_time = ts.index[-1] + 1
        quantiles = [str(q) for q in quantiles]
        req = self.__encode_request(
            ts, cat, dynamic_feat, num_samples, return_samples, quantiles
        )
        res = super(DeepARPredictor, self).predict(req)
        return self.__decode_response(
            res, ts.index.freq, prediction_time, return_samples
        )

    def __encode_request(
        self, ts, cat, dynamic_feat, num_samples, return_samples, quantiles
    ):
        instance = series_to_dict(
            ts, cat if cat is not None else None, dynamic_feat if dynamic_feat else None
        )
        configuration = {
            "num_samples": num_samples,
            "output_types": ["quantiles", "samples"]
            if return_samples
            else ["quantiles"],
            "quantiles": quantiles,
        }
        http_request_data = {"instances": [instance], "configuration": configuration}
        return json.dumps(http_request_data).encode("utf-8")

    def __decode_response(self, response, freq, prediction_time, return_samples):
        predictions = json.loads(response.decode("utf-8"))["predictions"][0]
        prediction_length = len(next(iter(predictions["quantiles"].values())))
        prediction_index = pd.DatetimeIndex(
            start=prediction_time, freq=freq, periods=prediction_length
        )
        if return_samples:
            dict_of_samples = {
                "sample_" + str(i): s for i, s in enumerate(predictions["samples"])
            }
        else:
            dict_of_samples = {}
        return pd.DataFrame(
            data={**predictions["quantiles"], **dict_of_samples}, index=prediction_index
        )

    def set_frequency(self, freq):
        self.freq = freq


def encode_target(ts):
    return [x if np.isfinite(x) else "NaN" for x in ts]


def series_to_dict(ts, cat=None, dynamic_feat=None):
    # Given a pandas.Series object, returns a dictionary encoding the time series.
    obj = {"start": str(ts.index[0]), "target": encode_target(ts)}
    if cat is not None:
        obj["cat"] = cat
    if dynamic_feat is not None:
        obj["dynamic_feat"] = dynamic_feat
    return obj


# In[ ]:
