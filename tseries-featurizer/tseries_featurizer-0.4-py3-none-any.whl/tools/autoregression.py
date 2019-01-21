from statsmodels.tsa.arima_model import ARIMA
import numpy as np
from .helpers import get_possible_orders
import pandas as pd
import warnings


def get_orders_aic(order, data):
	"""

	:param order:
	:param data:
	:return:
	"""
	aic = float('inf')
	data.name = str(data.name)
	p, q, c = None, None, None
	try:
		with warnings.catch_warnings():
			warnings.filterwarnings("ignore")
			arima_mod = ARIMA(data, order).fit(disp=0)
			aic = arima_mod.aic
			p, q, c = arima_mod.arparams, arima_mod.maparams, arima_mod.params.const
	except (ValueError, np.linalg.LinAlgError) as e:

		pass

	return aic, (p, q, [c])


def get_best_order(data, max_coeffs):
	"""

	:param data:
	:param max_coeffs:
	:return:
	"""
	best_score, best_cfg = float("inf"), None
	orders = get_possible_orders([max_coeffs, max_coeffs], max_coeffs)
	orders = np.concatenate((np.insert(orders, 1, 1, axis=1), np.insert(orders, 1, 0, axis=1)), )

	for order in orders:
		aic, _ = get_orders_aic(order, data)
		if aic < best_score:
			best_score, best_cfg = aic, order
	return best_cfg


def get_AR_model(data, max_coeffs):
	from random import shuffle
	col_list = list(data.columns)
	shuffle(col_list)
	for col in col_list:
		fit_model = get_best_order(data[col].dropna(), max_coeffs)
		if fit_model is not None:
			break
	return fit_model


def format_ar_column(params, title, max):
	if params is None:
		params = [None] * max

	ret = {f'{title}_{index}': params[index] for index in range(max)}
	return ret


def get_AR_params(data, fit_model, test=False):
	clean_data = data.dropna()
	_, params = get_orders_aic(fit_model, clean_data)
	ret = {'best_order': fit_model, 'constant': params[2][0]}

	ar_params = format_ar_column(params[0], 'ar_params', fit_model[0])

	ma_params = format_ar_column(params[1], 'ma_params', fit_model[2])
	ret.update({**ar_params, **ma_params})
	return ret
