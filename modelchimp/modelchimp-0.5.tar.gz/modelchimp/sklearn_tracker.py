import sys

from modelchimp import settings

from .event_queue import event_queue
from .enums import ClientEvent
from .module_loader import Finder


SKLEARN_OBJECT_LIST = [
('sklearn.linear_model.theil_sen', ['TheilSenRegressor.fit']),
('sklearn.svm.classes', ['SVR.fit',
                        'NuSVR.fit',
                        'LinearSVR.fit',
                        'SVC.fit', 'NuSVC.fit',
                        'LinearSVC.fit']),
('sklearn.linear_model.stochastic_gradient', ['SGDRegressor.fit',
                                                'SGDClassifier.fit']),
('sklearn.linear_model.ridge', ['RidgeCV.fit',
                                'Ridge.fit',
                                'RidgeClassifierCV.fit',
                                'RidgeClassifier.fit']),
('sklearn.neighbors.regression', ['RadiusNeighborsRegressor.fit',
                                    'KNeighborsRegressor.fit']),
('sklearn.linear_model.ransac', ['RANSACRegressor.fit']),
('sklearn.linear_model.passive_aggressive', ['PassiveAggressiveRegressor.fit',
                                            'PassiveAggressiveClassifier.fit']),
('sklearn.cross_decomposition.pls_',['PLSRegression.fit',
                                    'PLSCanonical.fit']),
('sklearn.linear_model.omp', ['OrthogonalMatchingPursuitCV.fit',
                                'OrthogonalMatchingPursuit.fit']),
('sklearn.linear_model.coordinate_descent', ['MultiTaskLassoCV.fit',
                                            'MultiTaskLasso.fit',
                                            'MultiTaskElasticNetCV.fit',
                                            'MultiTaskElasticNet.fit',
                                            'LassoCV.fit',
                                            'Lasso.fit',
                                            'ElasticNetCV.fit',
                                            'ElasticNet.fit']),
('sklearn.neural_network.multilayer_perceptron', ['MLPRegressor.fit',
                                                    'MLPClassifier.fit']),
('sklearn.linear_model.base', ['LinearRegression.fit']),
('sklearn.linear_model.least_angle', ['LassoLarsIC.fit',
                                        'LassoLarsCV.fit',
                                        'LassoLars.fit',
                                        'LarsCV.fit',
                                        'Lars.fit']),
('sklearn.kernel_ridge', ['KernelRidge.fit']),
('sklearn.linear_model.huber', ['HuberRegressor.fit']),
('sklearn.ensemble.gradient_boosting', ['GradientBoostingRegressor.fit',
                                        'GradientBoostingClassifier.fit']),
('sklearn.gaussian_process.gpr', ['GaussianProcessRegressor.fit']),
('sklearn.gaussian_process.gaussian_process', ['GaussianProcess.fit']),
("sklearn.ensemble.forest", ['RandomForestClassifier.fit',
                            'RandomForestRegressor.fit',
                            'ExtraTreesRegressor.fit',
                            'ExtraTreesClassifier.fit']),
('sklearn.tree.tree', ['ExtraTreeRegressor.fit',
                        'DecisionTreeRegressor.fit',
                        'ExtraTreeClassifier.fit',
                        'DecisionTreeClassifier.fit'
                        ]),
('sklearn.cross_decomposition.cca_', ['CCA.fit']),
('sklearn.linear_model.bayes', ['BayesianRidge.fit',
                                'ARDRegression.fit']),
('sklearn.ensemble.bagging', ['BaggingRegressor.fit',
                                'BaggingClassifier.fit']),
('sklearn.ensemble.weight_boosting', ['AdaBoostRegressor.fit',
                                        'AdaBoostClassifier.fit']),
('sklearn.neighbors.classification', ['RadiusNeighborsClassifier.fit',
                                        'KNeighborsClassifier.fit']),
('sklearn.discriminant_analysis', ['QuadraticDiscriminantAnalysis.fit',
                                    'LinearDiscriminantAnalysis.fit']),
('sklearn.linear_model.perceptron', ['Perceptron.fit']),
('sklearn.neighbors.nearest_centroid', ['NearestCentroid.fit']),
('sklearn.naive_bayes', ['MultinomialNB.fit',
                        'GaussianNB.fit',
                        'BernoulliNB.fit']),
('sklearn.linear_model.logistic', ['LogisticRegression.fit']),
('sklearn.semi_supervised.label_propagation', ['LabelSpreading.fit',
                                                'LabelPropagation.fit']),
('sklearn.gaussian_process.gpc', ['GaussianProcessClassifier.fit']),
('sklearn.calibration', ['CalibratedClassifierCV.fit']),
("sklearn.linear_model.logistic", ['LogisticRegressionCV.fit',
                                    'LogisticRegression.fit']),
("sklearn.pipeline", ["Pipeline.fit"])]

class SklearnState:
    FIT_STARTED = False

def sklearn_patcher(function):
    def wrapper(*args, **kwargs):
        execute_flag = False
        fit_event = {}
        fit_event['type'] = ClientEvent.MODEL_PARAM

        # Stop the execution of child fit methods( Basically, for ensembles)
        if SklearnState.FIT_STARTED is False:
            SklearnState.FIT_STARTED = True
            execute_flag = True
        return_value = function(*args, **kwargs)
        try:
            if execute_flag:
                params = return_value.get_params()
                settings.current_tracker.add_multiple_params(params)
        except Exception as e:
            pass

        return return_value
    return wrapper

def sklearn_loader():
    for fit in SKLEARN_OBJECT_LIST:
        sys.meta_path.insert(0, Finder(fit[0], sklearn_patcher,fit[1]))
