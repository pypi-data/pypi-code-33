# -*- coding: utf-8 -*-
"""
Machine learning steps for processed data.

@author: Alan Xu
"""

import os
import sys
import time
import numpy as np
import pandas as pd
import xgboost as xgb
from osgeo import gdal
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LassoCV, BayesianRidge, RidgeCV
from sklearn.feature_selection import SelectFromModel
from sklearn.utils import resample
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble.base import _partition_estimators
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import gaussian_kde, binned_statistic
import matplotlib.pyplot as plt
import threading
from sklearn.decomposition import PCA
from sklearn.externals.joblib import Parallel, delayed
from sklearn.utils.validation import check_is_fitted
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import forestci as fci
import learn2map.raster_tools as rt
from sklearn.neighbors import KNeighborsRegressor
# from sklearn.linear_model import lasso_path, enet_path, OrthogonalMatchingPursuitCV
# from sklearn.gaussian_process.kernels import WhiteKernel, ExpSineSquared
# from sklearn.kernel_ridge import KernelRidge
# from sklearn.model_selection import StratifiedShuffleSplit
# from sklearn import svm
# from sklearn.ensemble.forest import _generate_unsampled_indices
# import statsmodels.api as sm


# # from keras.models import Sequential
# # from keras.layers import Dense
# # from keras.wrappers.scikit_learn import KerasRegressor
# from fancyimpute import (
#     SimpleFill,
#     IterativeSVD,
#     SoftImpute,
#     BiScaler,
#     KNN,
#     MICE,
#     BayesianRidgeRegression,
# )


def density_scatter_plot(x0, y0, x_label='W', y_label='W_hat', x_limit=None, y_limit=None, file_name='fig_00.png'):
    # Calculate the point density
    xy = np.vstack([x0, y0])
    z0 = gaussian_kde(xy)(xy)
    idx = z0.argsort()
    x0, y0, z0 = x0[idx], y0[idx], z0[idx]

    fig0 = plt.figure(figsize=(5, 4))
    plt.scatter(x0, y0, c=z0, s=5, edgecolor='')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    x1 = plt.xlim(x_limit)
    y1 = plt.ylim(y_limit)
    plt.plot(x1, y1, 'k-')
    # plt.plot(x1, np.array(y1) * 0.8, '--', color='0.6')
    # plt.plot(x1, np.array(y1) * 1.2, '--', color='0.6')
    print('{}% of the data within the range of ±20%.'.format(
        np.sum((x0 * 0.8 < y0) & (y0 < x0 * 1.2) & (x0 < 100)) / x0[x0 < 100].size * 100))
    print('{}% of the data within the range of ±10%.'.format(
        np.sum((x0 * 0.9 < y0) & (y0 < x0 * 1.1) & (x0 < 100)) / x0[x0 < 100].size * 100))
    print('{}% of the data within the range of 20 Mg/ha.'.format(
        np.sum((x0 - 20 < y0) & (y0 < x0 + 20) & (x0 < 100)) / x0[x0 < 100].size * 100))
    print('{}% of the data within the range of 10 Mg/ha.'.format(
        np.sum((x0 - 10 < y0) & (y0 < x0 + 10) & (x0 < 100)) / x0[x0 < 100].size * 100))

    r2 = r2_score(x0[:, None], y0[:, None])
    # r2 = r_squared(x0, y0)
    print("Variance score 1: {:.2f}".format(r2))
    rmse = np.sqrt(mean_squared_error(x0[:, None], y0[:, None]))
    print("RMSE: {:.5f}".format(rmse))
    plt.text(max(x_limit) * 0.04, max(y_limit) * 0.85,
             r'$R^2 = {:1.3f}$'.format(r2) + '\n' + '$RMSE = {:1.3f}$'.format(rmse))
    plt.savefig(file_name, dpi=300)
    plt.close(fig0)

    return r2, rmse


def noise_filter(X, y, min_thres=4.0):
    print('Avg of y: {}'.format(np.mean(y)))
    # preliminary filter
    mdl1 = RandomForestRegressor(
        n_estimators=10,
        # max_features="sqrt",
        max_depth=10, random_state=444,
    )
    mdl2 = KNeighborsRegressor(n_neighbors=10)
    mdl3 = MLPRegressor(learning_rate_init=0.01, hidden_layer_sizes=(100, 100), random_state=444)

    noise_threshold = min_thres + 0.2 * y  # change as needed
    mdl_list = [mdl1, mdl2, mdl3]
    # mdl_list = [mdl3]
    noise_list = []
    for mdl in mdl_list:
        start_time = time.time()
        estimators = [('scale', StandardScaler()), ('learn', mdl)]
        ppl = Pipeline(estimators)
        y_hat = ppl.fit(X, y).predict(X)
        # print(ppl.score(X, y))
        # print(np.sqrt(mean_squared_error(y, y_hat)))
        # print("--- %s seconds ---" % (time.time() - start_time))
        y_c = np.int8(np.abs(y - y_hat) > noise_threshold)
        # print('Fraction of noise: {:.3f}%'.format(np.sum(y_c) / y.size * 100))
        noise_list.append(y_c)
    noise0 = np.sum(np.stack(noise_list), axis=0)
    # print('Fraction of valid noise: {:.3f}%'.format(np.sum(noise0 > 1) / y.size * 100))

    # post-preliminary, iteration
    noise = noise0
    noise_pool = []
    iteration = 5
    print(X.shape)
    print(y.shape)
    for i in range(iteration):
        Xtr = X[noise < 2, :]
        ytr = y[noise < 2]
        noise_list = []
        for mdl in mdl_list:
            start_time = time.time()
            estimators = [('scale', StandardScaler()), ('learn', mdl)]
            ppl = Pipeline(estimators)
            y_hat = ppl.fit(Xtr, ytr).predict(X)
            # print(ppl.score(Xtr, ytr))
            # print(np.sqrt(mean_squared_error(y, y_hat)))
            # print("--- %s seconds ---" % (time.time() - start_time))
            y_c = np.int8(np.abs(y - y_hat) > noise_threshold)
            # print('Fraction of noise: {:.3f}%'.format(np.sum(y_c) / y.size * 100))
            noise_list.append(y_c)
            noise_pool.append(y_c)
        noise = np.sum(np.stack(noise_list), axis=0)
        # print('Fraction of valid noise: {:.3f}%'.format(np.sum(noise > 1) / y.size * 100))

    noise = np.sum(np.stack(noise_pool), axis=0)
    # print(np.histogram(noise))
    X_clean = X[noise < 2 * iteration, :]
    y_clean = y[noise < 2 * iteration]
    X_noise = X[noise >= 2 * iteration, :]
    y_noise = y[noise >= 2 * iteration]
    print('Fraction of valid noise: {:.3f}%'.format(np.sum(noise > 2 * iteration - 1) / y.size * 100))
    plt.figure()
    plt.hist(y, 20, range=(0, np.max(y)), alpha=0.5, edgecolor='gray')
    plt.hist(y_clean, 20, range=(0, np.max(y)), alpha=0.5, edgecolor='gray')
    plt.show()
    # return X_clean, y_clean, X_noise, y_noise
    return X_clean, y_clean


class GridLearn(object):
    """
    Build machine learning object that can find the best parameters for final run.

    """

    def __init__(self, in_file='', y_column=None, mask_column=None):
        """
        :param in_file: input h5 file that contains the training data
        :param y_column: column index for response variable y
        :param mask_column: column index for mask (if exist, and should be after popping y_column)
        :param: best_params: param set that can be used in further learning
        """
        self.in_file = in_file
        if type(y_column) is list:
            self.y_column = y_column
        else:
            self.y_column = [y_column]
        if type(mask_column) is list:
            self.mask_column = mask_column
        else:
            self.mask_column = [mask_column]
        self.best_params = {}
        self.mdl = Pipeline([('scale', StandardScaler())])

    def tune_param_xgboost(self, params, bins, k=5):
        """
        Find the best param set that used in learning.
        :param k: number of folds used in cv
        :param params: parameter set used in grid search
        :return: best_params: param set that can be used in further learning
        :return: mdl: updated model using best_params
        """
        # train = pd.read_csv(self.in_file, sep=',', header=None)
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # print('start grid_search; predictors - {}'.format(predictors))
        target = train[self.y_column[0]]

        bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
        bin_weights = max(bin_counts) / bin_counts
        target_weight = bin_weights[binnumber - 1]
        target = binnumber.astype(int) - 1
        # target_weight = gaussian_kde(target)(target)
        # target_weight = max(target_weight) / target_weight
        fit_params = {'learn__sample_weight': target_weight}

        # grid_search = GridSearchCV(self.mdl, params, fit_params=fit_params, n_jobs=-1, verbose=1, cv=k)
        grid_search = GridSearchCV(self.mdl, params, n_jobs=-1, verbose=1, cv=k)
        # grid_search.fit(train[predictors], target)
        grid_search.fit(train[predictors], target, learn__sample_weight=target_weight)

        print(grid_search.best_params_)
        print(grid_search.best_score_)
        self.best_params = grid_search.best_params_
        self.mdl.set_params(**self.best_params)
        return self.best_params, self.mdl

    def clean_and_tune(self, params, k=5, min_thres=30):
        """
        Find the best param set that used in learning.
        :param k: number of folds used in cv
        :param params: parameter set used in grid search
        :return: best_params: param set that can be used in further learning
        :return: mdl: updated model using best_params
        """
        # train = pd.read_csv(self.in_file, sep=',', header=None)
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # print('start grid_search; predictors - {}'.format(predictors))
        target = train[self.y_column[0]]

        X, y = noise_filter(train[predictors].values, target.values, min_thres=min_thres)
        print(X.shape)
        print(y.shape)

        grid_search = GridSearchCV(self.mdl, params, n_jobs=-1, verbose=1, cv=k)
        grid_search.fit(X, y)
        # grid_search.fit(train[predictors], target)

        print(grid_search.best_params_)
        print('best score: {}'.format(grid_search.best_score_))
        self.best_params = grid_search.best_params_
        self.mdl.set_params(**self.best_params)
        return self.best_params, self.mdl

    def tune_param_set(self, params, k=5):
        """
        Find the best param set that used in learning.
        :param k: number of folds used in cv
        :param params: parameter set used in grid search
        :return: best_params: param set that can be used in further learning
        :return: mdl: updated model using best_params
        """
        # train = pd.read_csv(self.in_file, sep=',', header=None)
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        grid_search = GridSearchCV(self.mdl, params, n_jobs=-1, verbose=1, cv=k)
        grid_search.fit(train[predictors], train[self.y_column[0]])
        # for p in grid_search.grid_scores_:
        #     print(p)
        print(grid_search.best_params_)
        # print(grid_search.best_score_)
        self.best_params = grid_search.best_params_
        self.mdl.set_params(**self.best_params)
        return self.best_params, self.mdl

    # def tune_param_mdl(self, params, bins, k=5):
    #     """
    #     Find the best param set that used in learning.
    #     :param k: number of folds used in cv
    #     :param params: parameter set used in grid search
    #     :return: best_params: param set that can be used in further learning
    #     :return: mdl: updated model using best_params
    #     """
    #     # train = pd.read_csv(self.in_file, sep=',', header=None)
    #     train = pd.read_hdf(self.in_file, 'df0')
    #     if self.y_column[0] is None:
    #         sys.exit('"y_column" must be defined in training process...')
    #     else:
    #         predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]
    #
    #     # print('start grid_search; predictors - {}'.format(predictors))
    #     target = train[self.y_column[0]]
    #
    #     bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
    #     bin_weights = max(bin_counts) / bin_counts
    #     target_weight = bin_weights[binnumber - 1]
    #     target = binnumber.astype(int) - 1
    #     # target_weight = gaussian_kde(target)(target)
    #     # target_weight = max(target_weight) / target_weight
    #     fit_params = {'learn__sample_weight': target_weight}
    #
    #     # grid_search = GridSearchCV(self.mdl, params, fit_params=fit_params, n_jobs=-1, verbose=1, cv=k)
    #     grid_search = GridSearchCV(self.mdl, params, n_jobs=-1, verbose=1, cv=k)
    #     # grid_search.fit(train[predictors], target)
    #     grid_search.fit(train[predictors], target, learn__sample_weight=target_weight)
    #
    #     print(grid_search.best_params_)
    #     print(grid_search.best_score_)
    #     self.best_params = grid_search.best_params_
    #     self.mdl.set_params(**self.best_params)
    #     return self.best_params, self.mdl

    def split_training(self, test_file, i=0, fraction=0.3, min_thres=4.0):
        """
        :param fraction:
        :return:
        """
        train = pd.read_hdf(test_file)
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # self.mdl.fit(train[predictors], train[self.y_column[0]])
        X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        # X, y = train[predictors].values, train[self.y_column[0]].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=fraction, random_state=444)
        # X_test = np.concatenate((X_test, X_noise))
        # y_test = np.concatenate((y_test, y_noise))
        print(X_train.shape)
        self.mdl.fit(X_train, y_train)
        y_hat = self.mdl.predict(X_test)
        y_hat0 = self.mdl.predict(X_train)
        # print(y_hat.shape)
        # print(y_test.shape)
        # plt.scatter(y_test, y_hat)
        # plt.show()
        density_scatter_plot(y_test, y_hat,
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_{}_indep_valid_scatterplot.png'.format(os.path.splitext(test_file)[0], i)))
        density_scatter_plot(y_train, y_hat0,
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_{}_indep_valid_scatterplot0.png'.format(os.path.splitext(test_file)[0], i)))

    def predict_bigdata(self, test_file, out_file_h5, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        self.mdl.fit(train[predictors], train[self.y_column[0]])
        # X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        # self.mdl.fit(X, y)

        # x1 = Pipeline(self.mdl.steps[:-1]).transform(X)
        # _, coef_path, _ = lasso_path(x1, y, alphas=[5., 3., 1., .8, .5, .3])
        # print(coef_path)

        # min_y = y.min()
        # max_y = y.max()
        # limit_y = [min_y - abs(max_y - min_y) * 0.05, max_y + abs(max_y - min_y) * 0.05]
        # importances = self.mdl.named_steps['learn'].feature_importances_
        # plt.figure()
        # plt.bar(np.arange(train[predictors].shape[1]), importances)
        # plt.show()
        # density_scatter_plot(y, self.mdl.predict(X),
        #                      x_label='Measured', y_label='Predicted',
        #                      x_limit=limit_y, y_limit=limit_y,
        #                      file_name=('{}_train_xy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        # density_scatter_plot(train[self.y_column[0]].values, self.mdl.predict(train[predictors].values),
        #                      x_label='Measured', y_label='Predicted',
        #                      x_limit=limit_y, y_limit=limit_y,
        #                      file_name=('{}_train_rawxy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        #
        # # density_scatter_plot(train[self.y_column[0]].values, self.mdl.named_steps['learn'].oob_prediction_,
        # density_scatter_plot(y, self.mdl.named_steps['learn'].oob_prediction_,
        #                      x_label='Measured', y_label='Predicted',
        #                      x_limit=limit_y, y_limit=limit_y,
        #                      file_name=('{}_train_rawxyoob_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        # df_plot = pd.DataFrame(np.stack([y, self.mdl.predict(X)]).T, columns=['measured', 'predicted'])
        # df_plot.to_csv('{}_train_xy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))
        # df_plot = pd.DataFrame(np.stack([train[self.y_column[0]].values, self.mdl.predict(train[predictors].values)]).T, columns=['measured', 'predicted'])
        # df_plot.to_csv('{}_train_rawxy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))

        with pd.HDFStore(out_file_h5, mode='w', complib='blosc:snappy', complevel=9) as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
                transX = self.mdl.named_steps['impute'].transform(df[predictors])
                transX2 = self.mdl.named_steps['scale'].transform(transX)
                y_hat = np.zeros([df[predictors].shape[0], self.mdl.named_steps['learn'].n_estimators])
                for i, pred in enumerate(self.mdl.named_steps['learn'].estimators_):
                    y_hat[:, i] = (pred.predict(transX2))
                preds = np.nanmean(y_hat, axis=1)
                yerr = np.nanstd(y_hat, axis=1)

                # preds = self.mdl.predict(df[predictors])
                # # calculate inbag and unbiased variance
                # y_inbag = fci.calc_inbag(train[predictors].shape[0], self.mdl.named_steps['learn'])
                # y_V_IJ_unbiased = fci.random_forest_error(
                #     self.mdl.named_steps['learn'], y_inbag, train[predictors], df[predictors])
                # yerr = np.sqrt(y_V_IJ_unbiased)

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

            # predictors = [x for x in df.columns if x not in self.y_column + self.mask_column]
            #     xpred_i = Pipeline(self.mdl.steps[:-1]).transform(df[predictors].values)
            #     preds, yerr = self.mdl.named_steps['learn'].predict_err(xpred_i)
            #
            #     # transX = self.mdl.named_steps['scale'].transform(df[predictors])
            #     # y_hat = np.zeros([df[predictors].shape[0], self.mdl.named_steps['learn'].n_estimators])
            #     # for i, pred in enumerate(self.mdl.named_steps['learn'].estimators_):
            #     #     y_hat[:, i] = (pred.predict(transX))
            #     # preds = np.nanmean(y_hat, axis=1)
            #     # yerr = np.nanstd(y_hat, axis=1)
            #
            #     # preds = self.mdl.predict(df[predictors])
            #     # # calculate inbag and unbiased variance
            #     # y_V_IJ_unbiased = fci.random_forest_error(self.mdl.named_steps['learn'],
            #     #                                           self.mdl.named_steps['scale'].transform(train[predictors]),
            #     #                                           self.mdl.named_steps['scale'].transform(df[predictors]))
            #     # # y_inbag = fci.calc_inbag(train[predictors].shape[0], self.mdl.named_steps['learn'])
            #     # # y_V_IJ_unbiased = fci.random_forest_error(
            #     # #     self.mdl.named_steps['learn'], y_inbag, train[predictors], df[predictors])
            #     # yerr = np.sqrt(y_V_IJ_unbiased)
            #
            #     df1 = pd.Series(preds, name='Est')
            #     df2 = pd.Series(yerr, name='Err')
            #     df3 = df[['x', 'y']].reset_index(drop=True)
            #     df0 = pd.concat([df3, df1, df2], axis=1)
            #     store.append('df0', df0, index=False, data_columns=['Est'])
            # store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def predict_rfbc_error(self, test_file, out_file_h5, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # self.mdl.fit(train[predictors], train[self.y_column[0]])
        X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        self.mdl.fit(X, y)

        with pd.HDFStore(out_file_h5, mode='w', complib='blosc:snappy', complevel=9) as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
                predictors = [x for x in df.columns if x not in self.y_column + self.mask_column]
                xpred_i = Pipeline(self.mdl.steps[:-1]).transform(df[predictors].values)
                preds = self.mdl.named_steps['learn'].predict_all(xpred_i)

                df1 = pd.DataFrame(preds, columns=[f'Est_{i}' for i in range(preds.shape[1])])
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1], axis=1)
                store.append('df0', df0, index=False)
            store.create_table_index('df0', columns=['x', 'y'], optlevel=9, kind='full')

    def predict_lasso(self, test_file, out_file_h5, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        self.mdl.fit(train[predictors], train[self.y_column[0]])
        # X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        X, y = train[predictors].values, train[self.y_column[0]].values

        x1 = Pipeline(self.mdl.steps[:-1]).transform(X)
        x0 = Pipeline(self.mdl.steps[:-1]).transform(train[predictors].values)
        # _, coef_path, _ = lasso_path(x1, y, alphas=[.25, .2, .15, .1])
        # print(coef_path)
        # clf = LassoCV(cv=10).fit(x1, y)
        # print(clf.alpha_)
        # clf = BayesianRidge()
        # clf.fit(x0, train[self.y_column[0]].values)
        # param_grid = {"alpha": [1e0, 1e-1, 1e-2, 1e-3],
        #               "kernel": [ExpSineSquared(l, p)
        #                          for l in np.logspace(-2, 2, 10)
        #                          for p in np.logspace(0, 2, 10)]}
        # clf = GridSearchCV(KernelRidge(), cv=5, param_grid=param_grid, verbose=1)
        # x1 = np.concatenate((x1, x1 ** 2), axis=1)
        # x0 = np.concatenate((x0, x0 ** 2), axis=1)
        clf = LassoCV(max_iter=2000)
        sfm = SelectFromModel(clf, threshold=0.25)
        # sfm = SelectFromModel(clf)
        sfm.fit(x1, y)
        n_features = sfm.transform(x1).shape[1]
        print(n_features)
        print(sfm.get_support())
        # C_range = np.logspace(-2, 10, 13)
        # gamma_range = np.logspace(-9, 3, 13)
        # param_grid = dict(gamma=gamma_range, C=C_range)
        # clf = GridSearchCV(svm.SVR(), param_grid=param_grid, cv=5)
        # clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1, verbose=1)
        # clf = KNeighborsRegressor(n_neighbors=3)
        clf = BayesianRidge()
        clf.fit(sfm.transform(x1), y)
        # clf.fit(x1, y)
        print(clf.coef_)

        density_scatter_plot(y, clf.predict(sfm.transform(x1)),
        # density_scatter_plot(y, clf.predict(x1),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_xy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        density_scatter_plot(train[self.y_column[0]].values, clf.predict(sfm.transform(x0)),
        # density_scatter_plot(train[self.y_column[0]].values, clf.predict(x0),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_rawxy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        df_plot = pd.DataFrame(np.stack([y, clf.predict(sfm.transform(x1))]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_xy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))
        df_plot = pd.DataFrame(np.stack([train[self.y_column[0]].values, clf.predict(sfm.transform(x0))]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_rawxy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))

        with pd.HDFStore(out_file_h5, mode='w', complib='blosc') as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
                predictors = [x for x in df.columns if x not in self.y_column + self.mask_column]
                xpred_i = Pipeline(self.mdl.steps[:-1]).transform(df[predictors].values)
                # xpred_i = np.concatenate((xpred_i, xpred_i ** 2), axis=1)
                preds, yerr = clf.predict(sfm.transform(xpred_i), return_std=True)
                # preds = clf.predict(xpred_i)
                # yerr = preds

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def predict_lassocv(self, test_file, out_file_h5, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # self.mdl.fit(train[predictors], train[self.y_column[0]])
        X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        # X, y = train[predictors].values, train[self.y_column[0]].values

        mdl1 = LassoCV(cv=10, verbose=1)
        estimators = [
            ('poly', PolynomialFeatures(2)),
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        ppl = Pipeline(estimators)
        ppl.fit(X, y)
        print(ppl.steps[-1][1].coef_)

        # clf = BayesianRidge()
        # clf.fit(sfm.transform(x1), y)

        density_scatter_plot(y, ppl.predict(X),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_xy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        density_scatter_plot(train[self.y_column[0]].values, ppl.predict(train[predictors].values),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_rawxy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        df_plot = pd.DataFrame(np.stack([y, ppl.predict(X)]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_xy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))
        df_plot = pd.DataFrame(np.stack([train[self.y_column[0]].values, ppl.predict(train[predictors].values)]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_rawxy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))

        with pd.HDFStore(out_file_h5, mode='w', complib='blosc') as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
                predictors = [x for x in df.columns if x not in self.y_column + self.mask_column]
                preds = ppl.predict(df[predictors].values)
                yerr = preds

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def predict_lassocv_boost(self, test_file, out_file_h5, mask_file, mask_valid_range=0, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]
        X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        mdl1 = LassoCV(cv=10, verbose=1)
        estimators = [
            ('poly', PolynomialFeatures(2)),
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        ppl = Pipeline(estimators)

        # X, y = resample(X, y)
        ppl.fit(X, y)
        print(ppl.steps[-1][1].coef_)

        in0 = gdal.Open(mask_file)
        z_mask = in0.GetRasterBand(1).ReadAsArray()
        xs = in0.RasterXSize
        ys = in0.RasterYSize
        driver = gdal.GetDriverByName("GTiff")
        for k in range(351, 450):
            X1, y1 = resample(X, y, random_state=(k * 444))
            ppl.fit(X1, y1)
            print(f'step {k}: coef - {ppl.steps[-1][1].coef_}')
            # out_csv = f'{out_file_h5}{k}.csv'
            out_hdf = f'{out_file_h5}{k}.h5'
            with pd.HDFStore(test_file, 'r') as store:
                # for df in store.select('df0', columns=['x', 'y', f'Est_{k}'], chunksize=500000):
                #     preds = ppl.predict(df[[f'Est_{k}']].values)
                #     df1 = pd.Series(preds, name='Est').reset_index(drop=True)
                #     df3 = df[['x', 'y']].reset_index(drop=True)
                #     df0 = pd.concat([df3, df1], axis=1)
                #     if not os.path.isfile(out_csv):
                #         df0.to_csv(out_csv, mode='a', index=False, header=True)
                #     else:
                #         df0.to_csv(out_csv, mode='a', index=False, header=False)
                with pd.HDFStore(out_hdf, mode='w', complib='blosc:snappy', complevel=9) as store2:
                # with pd.HDFStore(out_hdf, mode='w') as store2:
                #     for df in store.select('df0', columns=[f'Est_{k}'], chunksize=2500000):
                    for df in store.select('df0', chunksize=500000):
                        preds = ppl.predict(df[[f'Est_{k}']].values)
                        df1 = pd.DataFrame(preds[:, None], columns=['Est']).reset_index(drop=True)
                        store2.append('df0', df1, index=False)

                out_yhat = '{}_raster.tif'.format(os.path.splitext(out_hdf)[0])
                z_hat = np.full((ys, xs), np.nan, dtype=np.float32)
                df0 = pd.read_hdf(out_hdf)
                print(df0.shape)
                z_hat[z_mask > mask_valid_range] = df0.Est.values
                dst_ds = driver.CreateCopy(out_yhat, in0, strict=0)
                dst_ds.GetRasterBand(1).WriteArray(z_hat)
                dst_ds.FlushCache()
                dst_ds = None
                # rt.ogrvrt_to_grid(mask_file, out_csv, 'x', 'y', 'Est', out_yhat, a_interp='nearest')
                os.remove(out_hdf)
        in0 = None

    def predict_ridge(self, test_file, out_file_h5, min_thres=4.0):
        """
        sklearn prediction for big data
        :param min_thres:
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # self.mdl.fit(train[predictors], train[self.y_column[0]])
        X, y = noise_filter(train[predictors].values, train[self.y_column[0]].values, min_thres=min_thres)
        # X, y = train[predictors].values, train[self.y_column[0]].values

        bins = np.concatenate((np.arange(0, 400, 40), np.array([999, ])))
        bin_counts, bin_edges, binnumber = binned_statistic(y, y, statistic='count', bins=bins)
        bin_weights = max(bin_counts) / bin_counts
        y_weight = bin_weights[binnumber - 1]

        mdl1 = RidgeCV(cv=10)
        estimators = [
            ('poly', PolynomialFeatures(2)),
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        ppl = Pipeline(estimators)
        ppl.fit(X, y, learn__sample_weight=y_weight)
        print(ppl.steps[-1][1].coef_)

        # clf = BayesianRidge()
        # clf.fit(sfm.transform(x1), y)

        density_scatter_plot(y, ppl.predict(X),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_xy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        density_scatter_plot(train[self.y_column[0]].values, ppl.predict(train[predictors].values),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(-90, 900), y_limit=(-90, 900),
                             file_name=('{}_train_rawxy_scatterplot.png'.format(os.path.splitext(out_file_h5)[0])))
        df_plot = pd.DataFrame(np.stack([y, ppl.predict(X)]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_xy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))
        df_plot = pd.DataFrame(np.stack([train[self.y_column[0]].values, ppl.predict(train[predictors].values)]).T, columns=['measured', 'predicted'])
        df_plot.to_csv('{}_train_rawxy_scatterplot.csv'.format(os.path.splitext(out_file_h5)[0]))

        with pd.HDFStore(out_file_h5, mode='w', complib='blosc') as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
                predictors = [x for x in df.columns if x not in self.y_column + self.mask_column]
                preds = ppl.predict(df[predictors].values)
                yerr = preds

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def predict_xgbc(self, test_file, out_file_h5, bins=np.concatenate((np.arange(0, 300, 30), np.array([999, ])))):
        """
        sklearn prediction for big data
        :param out_file_h5:
        :param test_file:
        :return:
        """
        train = pd.read_hdf(self.in_file, 'df0')
        if self.y_column[0] is None:
            sys.exit('"y_column" must be defined in training process...')
        else:
            predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]

        # mdl_err = self.mdl
        # x_train, x_test, y_train, y_test = train_test_split(train, train[self.y_column[0]], test_size=0.5)
        #
        # target = x_train[self.y_column[0]]
        # bins = np.linspace(0, 300, 13)
        # bins = np.concatenate((bins, np.array([999, ])))
        # bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
        # bin_weights = max(bin_counts) / bin_counts
        # target_weight = bin_weights[binnumber - 1]
        # target = binnumber - 1
        #
        # self.mdl.fit(x_train[predictors], target, learn__sample_weight=target_weight)
        # self.mdl.fit(x_train[predictors], target)
        # p_test = self.mdl.predict(np.float32(x_test[predictors]))
        # err_test = (y_test - p_test) ** 2
        # mdl_err.fit(x_test[predictors], err_test)

        target = train[self.y_column[0]]
        bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
        bin_weights = max(bin_counts) / bin_counts
        target_weight = bin_weights[binnumber - 1]
        target = binnumber.astype(int) - 1
        self.mdl.fit(train[predictors], target, learn__sample_weight=target_weight)
        # self.mdl.fit(train[predictors], target)

        preds0 = self.mdl.predict(np.float32(train[predictors]))
        density_scatter_plot(train[self.y_column[0]].values.flatten(), preds0.flatten(),
                             x_label='Measured AGB', y_label='Predicted AGB',
                             x_limit=(0, 400), y_limit=(0, 12),
                             file_name=('xgbc_target' + '_scatterplot.png'))
        xgbr = []
        for i in range(max(binnumber)):
            print(i)
            # linear_glm = sm.GLM(train[self.y_column[0]][(target == i) & (preds0==i)], train[predictors][(target == i) & (preds0==i)])
            # xgbr_i = linear_glm.fit()
            xgbr_i = self.xgbc_regression(0.1)
            xgbr_i.fit(train[predictors][(target == i) & (preds0 == i)],
                       train[self.y_column[0]][(target == i) & (preds0 == i)])
            preds1a = xgbr_i.predict(np.float32(train[predictors][(preds0 == i)]))
            # [preds1, e] = xgbr_i.predict(np.float32(train[predictors][(preds0==i)]))
            density_scatter_plot(train[self.y_column[0]][(preds0 == i)].values.flatten(), preds1a.flatten(),
                                 x_label='Measured AGB', y_label='Predicted AGB',
                                 x_limit=(0, 400), y_limit=(0, 400),
                                 file_name='xgbc_target_{}_scatterplot.png'.format(i))
            xgbr.append(xgbr_i)
        with pd.HDFStore(out_file_h5, mode='w', complib='blosc') as store:
            for df in pd.read_hdf(test_file, 'df0', chunksize=500000):

                preds1 = self.mdl.predict(np.float32(df[predictors])).astype(int)
                preds = np.copy(preds1)
                yerr = np.copy(preds1)
                for i in range(max(binnumber)):
                    pred_i = xgbr[i].predict(df[predictors][preds1 == i])
                    # pred_i[(pred_i < bin_edges[i])] = bin_edges[i]
                    # pred_i[(pred_i > bin_edges[i+1])] = bin_edges[i+1]
                    preds[preds1 == i] = pred_i
                    # preds[preds0 == i] = i * 30 + 15
                    xtrain_i = Pipeline(xgbr[i].steps[:-1]).transform(train[predictors][(target == i) & (preds0 == i)])
                    xpred_i = Pipeline(xgbr[i].steps[:-1]).transform(df[predictors][preds1 == i])
                    yerr_i = fci.random_forest_error(
                        xgbr[i].named_steps['learn'], xtrain_i, xpred_i)
                    yerr[preds1 == i] = yerr_i

                df1 = pd.Series(preds, name='Est')
                df2 = pd.Series(yerr, name='Err')
                df3 = df[['x', 'y']].reset_index(drop=True)
                df0 = pd.concat([df3, df1, df2], axis=1)
                store.append('df0', df0, index=False, data_columns=['Est'])
            store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    # def predict_xgboost(self, test_file, out_file_h5):
    #     """
    #     sklearn prediction for big data
    #     :param out_file_h5:
    #     :param test_file:
    #     :return:
    #     """
    #     train = pd.read_hdf(self.in_file, 'df0')
    #     if self.y_column[0] is None:
    #         sys.exit('"y_column" must be defined in training process...')
    #     else:
    #         predictors = [x for x in train.columns if x not in self.y_column + self.mask_column]
    #
    #     # mdl_err = self.mdl
    #     # x_train, x_test, y_train, y_test = train_test_split(train, train[self.y_column[0]], test_size=0.5)
    #     #
    #     # target = x_train[self.y_column[0]]
    #     # bins = np.linspace(0, 300, 13)
    #     # bins = np.concatenate((bins, np.array([999, ])))
    #     # bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
    #     # bin_weights = max(bin_counts) / bin_counts
    #     # target_weight = bin_weights[binnumber - 1]
    #     # target = binnumber - 1
    #     #
    #     # self.mdl.fit(x_train[predictors], target, learn__sample_weight=target_weight)
    #     # self.mdl.fit(x_train[predictors], target)
    #     # p_test = self.mdl.predict(np.float32(x_test[predictors]))
    #     # err_test = (y_test - p_test) ** 2
    #     # mdl_err.fit(x_test[predictors], err_test)
    #
    #     target = train[self.y_column[0]]
    #     bins = np.linspace(0, 300, 13)
    #     bins = np.concatenate((bins, np.array([999, ])))
    #     bin_counts, bin_edges, binnumber = binned_statistic(target, target, statistic='count', bins=bins)
    #     bin_weights = max(bin_counts) / bin_counts
    #     target_weight = bin_weights[binnumber - 1]
    #     target = binnumber.astype(int) - 1
    #     self.mdl.fit(train[predictors], target, learn__sample_weight=target_weight)
    #     # self.mdl.fit(train[predictors], target)
    #     with pd.HDFStore(out_file_h5, mode='w', complib='blosc') as store:
    #         for df in pd.read_hdf(test_file, 'df0', chunksize=500000):
    #
    #             preds = self.mdl.predict(np.float32(df[predictors]))
    #             yerr = preds
    #             # yerr = np.sqrt(mdl_err.predict(np.float32(df[predictors])))
    #
    #             df1 = pd.Series(preds, name='Est')
    #             df2 = pd.Series(yerr, name='Err')
    #             df3 = df[['x', 'y']].reset_index(drop=True)
    #             df0 = pd.concat([df3, df1, df2], axis=1)
    #             store.append('df0', df0, index=False, data_columns=['Est'])
    #         store.create_table_index('df0', columns=['Est'], optlevel=9, kind='full')

    def setup_rf_model(self):
        """
        setup rf model
        :type rate: learning rate to specify
        :return: self.mdl
        """

        mdl1 = RandomForestRegressor(
            n_estimators=500,
            max_features="sqrt",
            min_samples_split=5,
            oob_score=True,
        )

        estimators = [
            ('impute', SimpleImputer())
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    def setup_xgb_model(self, rate):
        """
        setup xgboost model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        mdl = xgb.XGBRegressor(
            learning_rate=rate,
            n_estimators=50,
            objective='reg:linear',
            eval_metric='rmse',
            nthread=1)

        estimators = [
            ('scale', StandardScaler()),
            ('pca', PCA(n_components=3)),
            ('learn', mdl)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    def setup_xgbc_model(self, rate):
        """
        setup xgboost model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        mdl = xgb.XGBClassifier(
            learning_rate=rate,
            n_estimators=100,
            max_depth=5,
            min_child_weight=5,
            gamma=0,
            subsample=0.7,
            colsample_bytree=0.7,
            objective='multi:softmax',
            nthread=1)

        estimators = [
            ('scale', StandardScaler()),
            ('pca', PCA()),
            ('learn', mdl)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    def xgbc_regression(self, rate):
        """
        setup xgboost model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        # mdl = xgb.XGBRegressor(
        #     learning_rate=rate,
        #     n_estimators=10,
        #     objective='reg:linear',
        #     eval_metric='rmse',
        #     nthread=1)
        # mdl = KNeighborsRegressor(n_neighbors=2)
        mdl = RandomForestRegressor()
        # mdl = RFbcRegressor()

        estimators = [
            ('scale', StandardScaler()),
            ('pca', PCA(n_components=3)),
            ('learn', mdl)
        ]
        mdl = Pipeline(estimators)
        return mdl

    def setup_rfbc_model(self):
        """
        setup rf model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        mdl1 = RFbcRegressor(
            # n_estimators=450,
            # max_features="sqrt",
            # min_samples_leaf=5,
            n_estimators=450,
            max_features=1,
            max_depth=15,
            # n_estimators=350,
            # max_features=3,
            # max_depth=31,
            oob_score=True,
        )
        # mdl1 = RFbcRegressor(n_estimators=350)
        estimators = [
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    def setup_lassocv_model(self):
        """
        setup rf model
        :type rate: learning rate to specify
        :return: self.mdl
        """
        mdl1 = LassoCV(cv=10, verbose=1)
        estimators = [
            ('poly', PolynomialFeatures(2)),
            ('scale', StandardScaler()),
            ('learn', mdl1)
        ]
        self.mdl = Pipeline(estimators)
        return self.mdl

    # def setup_nn_model(self):
    #     """
    #     setup nn model
    #     :type rate: learning rate to specify
    #     :return: self.mdl
    #     """
    #     with pd.HDFStore(self.in_file, mode='r') as store:
    #         if self.y_column[0] is None:
    #             sys.exit('"y_column" must be defined in training process...')
    #         else:
    #             predictors = [x for x in store['df0'].columns if x not in self.y_column + self.mask_column]
    #     n_feature = len(predictors)
    #
    #     model = Sequential()
    #     model.add(Dense(n_feature, input_dim=n_feature, init='normal', activation='relu'))
    #     model.add(Dense(1, init='normal'))
    #     model.compile(loss='mean_squared_error', optimizer='adam')
    #     mdl1 = KerasRegressor(
    #         build_fn=model,
    #         nb_epoch=100,
    #         batch_size=6,
    #         verbose=0,
    #     )
    #     estimators = [
    #         ('scale', StandardScaler()),
    #         ('learn', mdl1)
    #     ]
    #     self.mdl = Pipeline(estimators)
    #     return self.mdl

    # def setup_nn_model(self):
    #     """
    #     setup nn model
    #     :type rate: learning rate to specify
    #     :return: self.mdl
    #     """
    #     with pd.HDFStore(self.in_file, mode='r') as store:
    #         if self.y_column[0] is None:
    #             sys.exit('"y_column" must be defined in training process...')
    #         else:
    #             predictors = [x for x in store['df0'].columns if x not in self.y_column + self.mask_column]
    #     n_feature = len(predictors)
    #
    #     model = Sequential()
    #     model.add(Dense(n_feature, input_dim=n_feature, init='normal', activation='relu'))
    #     model.add(Dense(1, init='normal'))
    #     model.compile(loss='mean_squared_error', optimizer='adam')
    #     mdl1 = KerasRegressor(
    #         build_fn=model,
    #         nb_epoch=100,
    #         batch_size=6,
    #         verbose=0,
    #     )
    #     estimators = [
    #         ('scale', StandardScaler()),
    #         ('learn', mdl1)
    #     ]
    #     self.mdl = Pipeline(estimators)
    #     return self.mdl


def rfbc_tune(learn_rfbc, n_feature, min_thres=30):
    """
    tuning parameters for the xgboost regression model
    :param n_feature: number of features
    :param learn_rfbc: GridLearn class object
    :return: learn_rfbc: GridLearn class object
    """
    learn_rfbc.setup_rfbc_model()
    params = {
        'learn__max_depth': list(range(3, 40, 4)),
        'learn__max_features': [int(0.2 * n_feature), int(0.4 * n_feature), int(0.6 * n_feature), int(0.8 * n_feature)],
        'learn__n_estimators': list(range(50, 501, 100)),
        # 'learn__n_estimators': list(range(30, 301, 30)),
    }
    learn_rfbc.clean_and_tune(params, k=5, min_thres=min_thres)

    return learn_rfbc


def xgb_tune(learn_xgb, n_feature, bins=np.concatenate((np.arange(0, 300, 30), np.array([999, ])))):
    """
    tuning parameters for the xgboost regression model
    :param n_feature: number of features
    :param bins: number of bins for floating to n_class
    :param learn_xgb: GridLearn class object
    :return: learn_xgb: GridLearn class object
    """
    learn_xgb.setup_xgbc_model(0.1)
    params = {
        'pca__n_components': [int(0.2 * n_feature), int(0.4 * n_feature), int(0.6 * n_feature), int(0.8 * n_feature)],
        # 'learn__n_estimators': list(range(50, 501, 100)),
    }
    learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__n_estimators': list(range(50, 501, 100)),
        'learn__learning_rate': [0.001, 0.01, 0.1],
    }
    learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__max_depth': list(range(3, 10, 2)),
        'learn__min_child_weight': list(range(1, 11, 3)),
    }
    learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__gamma': [i / 10.0 for i in range(0, 4)],
    }
    learn_xgb.tune_param_xgboost(params, bins)
    # params = {
    #     'learn__n_estimators': list(range(50, 501, 100)),
    #     'learn__learning_rate': [0.001, 0.01, 0.1],
    # }
    # learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__subsample': [i / 10.0 for i in range(1, 10, 2)],
        'learn__colsample_bytree': [i / 10.0 for i in range(5, 10, 2)],
    }
    learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__reg_alpha': [0, 1e-4, 1e-2, 1, 100],
        'learn__reg_lambda': [0, 1e-4, 1e-2, 1, 100],
    }
    learn_xgb.tune_param_xgboost(params, bins)
    params = {
        'learn__n_estimators': list(range(50, 501, 100)),
        'learn__learning_rate': [0.001, 0.01, 0.1],
    }
    learn_xgb.tune_param_xgboost(params, bins)

    return learn_xgb


def accumulate_prediction(predict1, predict2, X, out1, out2, lock):
    prediction1 = predict1(X, check_input=False)
    prediction2 = predict2(X, check_input=False)
    with lock:
        out1 += prediction1 * 2 - prediction2
        out2 += (prediction1 * 2 - prediction2) ** 2


class RFbcRegressor(RandomForestRegressor):
    def __init__(self,
                 n_estimators=300,
                 max_depth=15,
                 min_samples_split=2,
                 min_samples_leaf=5,
                 max_features="auto",
                 oob_score=True,
                 n_jobs=1,
                 random_state=None,
                 verbose=0):
        super().__init__(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            verbose=verbose,
            warm_start=False)
        self.estimators1_ = []
        self.estimators2_ = []

    def fit(self, X, y=None, sample_weight=None):
        """
        fit rfbc model
        :param X:
        :param y:
        :return:
        """
        super().fit(X, y, sample_weight=None)
        self.estimators1_ = self.estimators_
        # oob_y = super().predict(X)
        oob_y = self.oob_prediction_
        e1 = y - oob_y
        y2 = oob_y - e1
        super().fit(X, y2, sample_weight=None)
        self.estimators2_ = self.estimators_

    def predict(self, X):
        # Assign chunk of trees to jobs
        n_jobs, _, _ = _partition_estimators(self.n_estimators, self.n_jobs)

        # avoid storing the output of every estimator by summing them here
        y_hat1 = np.zeros((X.shape[0]), dtype=np.float64)
        y_hat2 = np.zeros((X.shape[0]), dtype=np.float64)

        # Parallel loop
        lock1 = threading.Lock()
        Parallel(n_jobs=n_jobs, verbose=self.verbose, backend="threading")(
            delayed(accumulate_prediction)(self.estimators1_[i].predict, self.estimators2_[i].predict,
                                           np.float32(X), y_hat1, y_hat2, lock1)
            for i in range(len(self.estimators1_)))

        y_hat = y_hat1 / len(self.estimators1_)
        # y_err = np.sqrt((y_hat2 - y_hat1 ** 2 / len(self.estimators1_)) / (len(self.estimators1_) - 1))

        return y_hat

    def predict_err(self, X):
        # Assign chunk of trees to jobs
        n_jobs, _, _ = _partition_estimators(self.n_estimators, self.n_jobs)

        # avoid storing the output of every estimator by summing them here
        y_hat1 = np.zeros((X.shape[0]), dtype=np.float64)
        y_hat2 = np.zeros((X.shape[0]), dtype=np.float64)

        # Parallel loop
        lock1 = threading.Lock()
        Parallel(n_jobs=n_jobs, verbose=self.verbose, backend="threading")(
            delayed(accumulate_prediction)(self.estimators1_[i].predict, self.estimators2_[i].predict,
                                           np.float32(X), y_hat1, y_hat2, lock1)
            for i in range(len(self.estimators1_)))

        y_hat = y_hat1 / len(self.estimators1_)
        y_err = np.sqrt((y_hat2 - y_hat1 ** 2 / len(self.estimators1_)) / (len(self.estimators1_) - 1))

        return y_hat, y_err

    def predict_all(self, X):
        # Assign chunk of trees to jobs
        n_jobs, _, _ = _partition_estimators(self.n_estimators, self.n_jobs)

        # avoid storing the output of every estimator by summing them here
        y_hat1 = np.zeros((X.shape[0], len(self.estimators1_)), dtype=np.float64)
        for i in range(len(self.estimators1_)):
            prediction1 = self.estimators1_[i].predict(X, check_input=False)
            prediction2 = self.estimators2_[i].predict(X, check_input=False)
            y_hat1[:, i] = prediction1 * 2 - prediction2

        return y_hat1

    # def _set_oob_score(self, X, y):
    #     """Compute out-of-bag scores"""
    #     n_samples = y.shape[0]
    #
    #     predictions = np.zeros((n_samples, self.n_outputs_))
    #     n_predictions = np.zeros((n_samples, self.n_outputs_))
    #
    #     for i in range(len(self.estimators1_)):
    #         unsampled_indices = _generate_unsampled_indices(
    #             self.estimators1_[i].random_state, n_samples)
    #         prediction1 = self.estimators1_[i].predict(X[unsampled_indices, :], check_input=False)
    #         prediction2 = self.estimators1_[i].predict(X[unsampled_indices, :], check_input=False)
    #         p_estimator = prediction1 * 2 - prediction2
    #
    #         if self.n_outputs_ == 1:
    #             p_estimator = p_estimator[:, np.newaxis]
    #
    #         predictions[unsampled_indices, :] += p_estimator
    #         n_predictions[unsampled_indices, :] += 1
    #
    #     predictions /= n_predictions
    #     self.oob_prediction_ = predictions
    #
    #     if self.n_outputs_ == 1:
    #         self.oob_prediction_ = \
    #             self.oob_prediction_.reshape((n_samples, ))
    #
    #     self.oob_score_ = 0.0
    #
        # for k in range(self.n_outputs_):
        #     self.oob_score_ += r2_score(y[:, k],
        #                                 predictions[:, k])
        #
        # self.oob_score_ /= self.n_outputs_

    @property
    def feature_importances_(self):
        check_is_fitted(self, 'estimators1_')

        all_importances = Parallel(n_jobs=self.n_jobs,
                                   backend="threading")(
            delayed(getattr)(tree, 'feature_importances_')
            for tree in self.estimators1_)

        return sum(all_importances) / len(self.estimators1_)
