# from skmultiflow.evaluation.evaluate_prequential import EvaluatePrequential
# from skmultiflow.data.hyper_plane_generator import HyperplaneGenerator
# from skmultiflow.trees.hoeffding_adaptive_tree import HAT, HoeffdingTree
# from skmultiflow.bayes import NaiveBayes
#
# """1. Create stream"""
# stream = HyperplaneGenerator(mag_change=0.001, noise_percentage=0.1, random_state=2)
# stream.prepare_for_use()
#
# """2. Create classifier"""
# hat = HAT()
# ht = HoeffdingTree()
# nb = NaiveBayes()
#
# """3. Setup evaluator"""
# evaluator = EvaluatePrequential(show_plot=True,
#                                 pretrain_size=1,
#                                 max_samples=10000,
#                                 metrics=['accuracy', 'kappa', 'kappa_t'])
# # evaluator = EvaluatePrequential(show_plot=True,
# #                                 pretrain_size=1,
# #                                 max_samples=100,
# #                                 n_wait=1,
# #                                 metrics=['accuracy', 'true_vs_predicted'],
# #                                 output_file='test_tp.csv')
# #
# """4. Run evaluator"""
# evaluator.evaluate(stream=stream, model=[hat, nb], model_names=['HAT', 'NB'])

######
# Regression
######
# from skmultiflow.data import RegressionGenerator
# from skmultiflow.trees import RegressionHoeffdingTree, RegressionHAT
# stream = RegressionGenerator(n_samples=4000)
# stream.prepare_for_use()
# hatr = RegressionHAT()
# htr = RegressionHoeffdingTree()
#
# evaluator = EvaluatePrequential(show_plot=True,
#                                 pretrain_size=1,
#                                 max_samples=100,
#                                 n_wait=1,
#                                 # metrics=['mean_square_error', 'true_vs_predicted'],
#                                 metrics=['mean_square_error', 'mean_absolute_error'],
#                                 output_file='test_tp.csv')
#
# evaluator.evaluate(stream=stream, model=[hatr, htr], model_names=['HATr', 'HTr'])

# ######
# # Multi-label
# ######
# from skmultiflow.data import MultilabelGenerator
# from skmultiflow.meta import MultiOutputLearner
# from sklearn.linear_model.stochastic_gradient import SGDClassifier
#
# stream = MultilabelGenerator(n_samples=1000, random_state=1)
# stream.prepare_for_use()
#
# mol = MultiOutputLearner(SGDClassifier(n_iter=100))
# evaluator = EvaluatePrequential(show_plot=True,
#                                 pretrain_size=1,
#                                 max_samples=500,
#                                 n_wait=100,
#                                 metrics=['hamming_score', 'hamming_loss', 'exact_match', 'j_index'],
#                                 output_file='test.csv')
#
# evaluator.evaluate(stream=stream, model=[mol], model_names=['MOL'])

# ######
# # Multi-target
# ######
# from skmultiflow.data import RegressionGenerator
# from skmultiflow.trees import MultiTargetRegressionHoeffdingTree
#
# stream = RegressionGenerator(n_samples=1000, n_features=20,
#                              n_informative=15, random_state=1,
#                              n_targets=7)
# stream.prepare_for_use()
#
# mtrht = MultiTargetRegressionHoeffdingTree(leaf_prediction='adaptive')
#
# evaluator = EvaluatePrequential(show_plot=True,
#                                 pretrain_size=1,
#                                 max_samples=5000,
#                                 n_wait=100,
#                                 metrics=['average_mean_square_error',
#                                          'average_mean_absolute_error',
#                                          'average_root_mean_square_error'],
#                                 output_file='test.csv')
#
# evaluator.evaluate(stream=stream, model=[mtrht], model_names=['MTRHT'])


###
# Data points
###

# # The first example demonstrates how to evaluate one model
# from skmultiflow.data import SEAGenerator
# from skmultiflow.trees import HoeffdingTree
# from skmultiflow.evaluation import EvaluatePrequential
# # Set the stream
# stream = SEAGenerator(random_state=1)
# stream.prepare_for_use()
# # Set the model
# ht = HoeffdingTree()
# # Set the evaluator
# evaluator = EvaluatePrequential(max_samples=200,
#                                 n_wait=1,
#                                 pretrain_size=1,
#                                 max_time=1000,
#                                 show_plot=True,
#                                 metrics=['accuracy'],
#                                 data_points_for_classification=True)
# evaluator.evaluate(stream=stream, model=ht, model_names=['HT'])
# # Run evaluation
# evaluator.evaluate(stream=stream, model=ht, model_names=['HT'])

# ###
# # Example drift detection
# ###
# from skmultiflow.data import FileStream
# from skmultiflow.bayes import NaiveBayes
# from skmultiflow.drift_detection import ADWIN
#
# stream = FileStream('../data/datasets/elec.csv')
# stream.prepare_for_use()
#
# model = NaiveBayes()
# drift_detector = ADWIN()
#
# cnt = 0
# max_samples = 5000
#
# while cnt < max_samples:
#     X, y = stream.next_sample()
#     drift_detector.add_element(model.predict(X)[0] == y[0])
#     if drift_detector.detected_change():
#         print('Change detected at {}, resetting model'.format(cnt))
#         model.reset()
#     model.partial_fit(X, y, classes=stream.target_values)
#     cnt += 1

from skmultiflow.data.multilabel_generator import MultilabelGenerator
from skmultiflow.trees.lc_hoeffding_tree import LCHT
from skmultiflow.evaluation.evaluate_prequential import EvaluatePrequential
from skmultiflow.meta import MultiOutputLearner

stream = MultilabelGenerator(n_samples=2000, n_features=10, n_targets=3, n_labels=2, random_state=0)
stream.prepare_for_use()

lcht = LCHT(n_labels=3)
mol = MultiOutputLearner()

evaluator = EvaluatePrequential(show_plot=True,
                                pretrain_size=200,
                                max_samples=1000,
                                metrics = ['exact_match'])

evaluator.evaluate(stream=stream, model=[lcht, mol], model_names=['LCHT', 'MOL'])
