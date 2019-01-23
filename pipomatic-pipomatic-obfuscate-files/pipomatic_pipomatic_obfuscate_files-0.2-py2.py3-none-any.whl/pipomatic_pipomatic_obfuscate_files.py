"Obfuscate files package"

__version__ = "0.2"

#!/usr/bin/env python
# coding: utf-8

# To do:
#
# Replace each unique value with the same random text

# In[2]:


from pathlib import Path
import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_integer_dtype,
    is_object_dtype,
    is_string_dtype,
)


# In[3]:


def delete_files(folder):
    file_generator = folder.glob("**/*")
    file_list = list(file_generator)
    for file in file_list:
        file.unlink()
    return list(file_list)


def move_files(samples_folder, file_to_copy, destination_folder):
    (destination_folder / file_to_copy).write_bytes(
        (samples_folder / file_to_copy).read_bytes()
    )
    return file_to_copy


def convert_to_numeric_and_date(df, dayfirst=True):
    for column in df.columns:
        if is_object_dtype(df[column]) or is_string_dtype(df[column]):
            try:
                df[column] = pd.to_numeric(df[column], downcast="integer")
            except:
                try:
                    df[column] = df[column].str.replace("$", "")
                    df[column] = df[column].str.replace(",", "")
                    df[column] = pd.to_numeric(df[column])
                except:
                    try:
                        df[column] = pd.to_datetime(df[column], dayfirst=dayfirst)
                    except:
                        pass
    return df


def random_dates(start, end, seed=1, replace=True, number_of_rows=100):
    dates = pd.date_range(start, end).to_series()
    return dates.sample(number_of_rows, replace=replace, random_state=seed).index


def dataframe_obfuscator(df, number_of_rows=100):
    for column in df.columns:
        if is_datetime64_any_dtype(df[column]):
            df[column] = random_dates(min(df[column]), max(df[column]), seed=1)
        elif is_integer_dtype(df[column]):
            df[column] = df[column].fillna(0)
            if min(df[column]) < max(df[column]):
                df[column] = np.random.randint(
                    min(df[column]), max(df[column]), size=(number_of_rows)
                )
            else:
                df[column] = min(df[column])
        elif is_numeric_dtype(df[column]):
            df[column] = df[column].fillna(0)
            df[column] = np.random.uniform(
                min(df[column]), max(df[column]), size=(number_of_rows)
            )
        else:
            df[column] = "random text"
    return df


def obfuscate_csv(data_file, dayfirst=True, number_of_rows=100):
    df = pd.read_csv(data_file, nrows=number_of_rows)
    df = convert_to_numeric_and_date(df)
    df = dataframe_obfuscator(df)
    df.to_csv(data_file, header=True, index=False)
    return df


def obfuscate_excel(data_file, dayfirst=True, number_of_rows=100):
    df = pd.read_excel(data_file, nrows=number_of_rows)
    display(df.head())
    df = convert_to_numeric_and_date(df)
    df = dataframe_obfuscator(df)
    df.to_excel(data_file, header=True, index=False)
    return df


# In[ ]:
