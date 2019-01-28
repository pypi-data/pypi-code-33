import numpy as np
from datetime import datetime, timedelta

class regularize(object):

    @staticmethod
    def mask_pixels_with_more_than(mask, more_than):
        t_mask = np.sum(mask, axis=0)
        mask = t_mask > more_than
        return mask

    @staticmethod
    def time(stack, timestamps,
             start_date,
             end_date,
             interval_days,
             masks = None,
             ts_format = "%Y-%m-%d"):
        ts = [datetime.strptime(t, ts_format) for t in timestamps]
        start_date = datetime.strptime(start_date, ts_format)
        end_date = datetime.strptime(end_date, ts_format)
        delta = timedelta(days=interval_days)

        wanted = [start_date]
        while wanted[-1] + delta < end_date:
            wanted.append(wanted[-1] + delta)
        if end_date not in wanted: wanted.append(end_date)

        ts = np.array([(t - start_date).total_seconds() for t in ts])
        wanted = np.array([(t - start_date).total_seconds() for t in wanted])

        if masks is None:
            pass
        interpolated = np.array([[[np.interp(wanted,
                                 ts[masks[:,x_i,y_i] == 0],
                                 stack[masks[:,x_i,y_i] == 0, x_i, y_i, b_i])
                        for b_i in range(stack.shape[3])]
                        for y_i in range(stack.shape[2])]
                        for x_i in range(stack.shape[1])])
        interpolated = np.transpose(np.array(interpolated), axes=[3,0,1,2])
        return interpolated, wanted