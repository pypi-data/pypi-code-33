import numpy as np
import pandas as pd

def PrintPdColumns(df):
	cols = [col for col in df.columns]
	print cols

def FlattenList(notflat_list):
	flat_list = [item for sublist in notflat_list for item in sublist]
	return flat_list