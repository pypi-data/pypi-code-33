import pandas as pd
from .helpers import get_attr_from_module
import itertools


def item_list_from_tuple_list(data, item_index=0, unique=False, sort=True, output_type=int):
	item_list = data.apply(lambda x: list(list(zip(*x))[item_index])).apply(pd.Series).stack()
	if unique:
		item_list = item_list.unique()

	item_list = list(map(output_type, item_list))
	if sort:
		item_list = sorted(item_list)
	return item_list


def get_evaluated_function(data, evaluated_field, evaluator_fn, model_field):
	"""

	:param data:
	:param evaluated_field:
	:param evaluator_fn:
	:param model_field:
	:return:
	"""
	evaluator_fn = get_attr_from_module(evaluator_fn)

	evaluated_col = data.filter(regex=f'{evaluated_field}$')
	best_index = evaluator_fn(evaluated_col.iloc[:, 0].tolist())  # This function must always return an index
	selected_row = data.iloc[best_index]

	selected_frame = selected_row.to_frame().T

	return selected_frame.loc[:, selected_frame.columns.str.endswith(model_field)].iloc[0, 0]


def get_one_from_col(data, col):
	evaluated_col = data.filter(regex=f'{col}$')
	return evaluated_col.iloc[0, 0]


def get_list_from_columns(data):
	"""
	Takes the text after the underscore in each of the data columns and inserts them to a list.
	:param data: DataFrame with columns.
	:return: list of column parameters in str.
	"""
	columns = data.columns.tolist()
	data_list = list(map(lambda x: str(x.split('_')[-1]), columns))
	return data_list


def get_most_important_freqs(data):
	from .features import detect_peaks

	freqs = [list(detect_peaks(data[col]).keys()) for col in data]

	return set(itertools.chain(*freqs))
