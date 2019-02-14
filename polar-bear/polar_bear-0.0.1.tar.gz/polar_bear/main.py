import numpy as np
import pandas as pd

int_dtype_list = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
float_dtype_list = ['float16', 'float32', 'float64', 'float128']


def clean(df, target_col='target', include_target=True, threshold_one_hot=0.1):
    return_df = pd.DataFrame()
    print(df)
    rows_count = df.shape[0]
    feature_column_index = 1

    for label, content in df.iteritems():
        print(label)

        if label == target_col:
            if include_target:
                return_df["y1:" + label] = content
            continue

        dtype = content.dtype
        print(dtype)
        if dtype in int_dtype_list:
            value_counts = content.value_counts().shape[0]
            if value_counts < (rows_count * threshold_one_hot):
                mode = content.value_counts().index[0]
                content[np.isnan(content)] = mode
                one_hot_df = pd.get_dummies(content, prefix=label)
                for one_hot_label, one_hot_content in one_hot_df.iteritems():
                    return_df["x" + str(feature_column_index) + ":" + one_hot_label] = one_hot_content
                    feature_column_index += 1
        elif dtype in float_dtype_list:
            value_counts = content.value_counts().shape[0]
            if value_counts < (rows_count * threshold_one_hot):
                mode = content.value_counts().index[0]
                content[np.isnan(content)] = mode
                one_hot_df = pd.get_dummies(content, prefix=label)
                for one_hot_label, one_hot_content in one_hot_df.iteritems():
                    return_df["x" + str(feature_column_index) + ":" + one_hot_label] = one_hot_content
                    feature_column_index += 1
            else:
                mean = content.mean()
                content[np.isnan(content)] = mean
                return_df["x" + str(feature_column_index) + ":" + label + "_float"] = content
                feature_column_index += 1
        elif (dtype == 'object') or (dtype == 'bool'):
            value_counts = content.value_counts().shape[0]
            if value_counts < (rows_count * threshold_one_hot):
                mode = content.value_counts().index[0]
                content[pd.isnull(content)] = mode
                one_hot_df = pd.get_dummies(content, prefix=label)
                for one_hot_label, one_hot_content in one_hot_df.iteritems():
                    return_df["x" + str(feature_column_index) + ":" + one_hot_label] = one_hot_content
                    feature_column_index += 1

    return return_df
