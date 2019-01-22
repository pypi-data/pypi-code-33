# Primitive Python paths (Python paths under which primitives registers themselves) have to adhere to namespace rules.
# Those rules describe that the Python path consists of multiple segments, one of them being "primitive name". Those
# names should be a general name to describe the logic of a primitive with the idea that multiple implementations
# of the same logic share the same name. This file contains a list of known and allowed primitive names.
# Names should be descriptive and something which can help people understand what the primitive is about.
# You can assume general understanding of data science concepts and names.
#
# Everyone is encouraged to help currate this list and suggest improvements (merging, removals, additions)
# of values in that list by submitting a merge request. We are not strict about names here, the main purpose of
# this list is to encourage collaboration and primitive name reuse when that is reasonable. Please check the list
# first when deciding on a Python path of your primitive and see if it can fit well under an existing name.
#
# See: https://gitlab.com/datadrivendiscovery/d3m/issues/3

PRIMITIVE_NAMES = [
    'adaptive_simultaneous_markov_blanket',
    'add_semantic_types',
    'adjacency_spectral_embedding',
    'ape',
    'ard',
    'arima',
    'audio_featurization',
    'audio_reader',
    'audio_slicer',
    'bagging',
    'bayesian_logistic_regression',
    'bernoulli_naive_bayes',
    'binarizer',
    'cast_to_type',
    'channel_averager',
    'cleaning_featurizer',
    'cluster',
    'cluster_curve_fitting_kmeans',
    'collaborative_filtering_link_prediction',
    'collaborative_filtering_parser',
    'column_parser',
    'community_detection',
    'community_detection_parser',
    'computes_cores',
    'conditioner',
    'construct_predictions',
    'convolutional_neural_net',
    'corex_continuous',
    'corex_supervised',
    'corex_text',
    'count_vectorizer',
    'cover_tree',
    'croc',
    'csv_reader',
    'cut_audio',
    'data_cleaning',
    'dataframe_to_list',
    'dataframe_to_ndarray',
    'dataframe_to_tensor',
    'dataset_text_reader',
    'dataset_to_dataframe',
    'decision_tree',
    'deep_markov_bernoulli_forecaster',
    'deep_markov_categorical_forecaster',
    'deep_markov_gaussian_forecaster',
    'denormalize',
    'diagonal_mvn',
    'dict_vectorizer',
    'dimension_selection',
    'doc_2_vec',
    'dummy',
    'edge_list_to_graph',
    'ekss',
    'encoder',
    'extra_trees',
    'extract_columns',
    'extract_columns_by_semantic_types',
    'extract_columns_by_structural_types',
    'fast_ica',
    'fast_lad',
    'feature_agglomeration',
    'feed_forward_neural_net',
    'forward',
    'gaussian_classification',
    'gaussian_clustering',
    'gaussian_naive_bayes',
    'gaussian_process',
    'general_relational_dataset',
    'generic_univariate_select',
    'glda',
    'glis',
    'gmm',
    'go_dec',
    'goturn',
    'gradient_boosting',
    'graph_matching_link_prediction',
    'graph_matching_parser',
    'graph_node_splitter',
    'graph_to_edge_list',
    'graph_transformer',
    'grasta',
    'grasta_masked',
    'greedy_imputation',
    'grouse',
    'hdp',
    'horizontal_concat',
    'i3d',
    'i_vector_extractor',
    'ibex',
    'identity_parentchildren_markov_blanket',
    'image_reader',
    'image_transfer_learning_transformer',
    'imputer',
    'increment',
    'iqr_scaler',
    'iterative_regression_imputation',
    'joint_mutual_information',
    'k_neighbors',
    'kernel_pca',
    'kernel_ridge',
    'kfold_dataset_split',
    'kmeans',
    'kss',
    'l1_low_rank',
    'labler',
    'laplacian_spectral_embedding',
    'largest_connected_component',
    'lars',
    'lasso',
    'lasso_cv',
    'lda',
    'learner',
    'linear_discriminant_analysis',
    'linear_regression',
    'linear_svc',
    'linear_svr',
    'link_prediction',
    'list_to_ndarray',
    'list_to_dataframe',
    'log_mel_spectrogram',
    'logistic_regression',
    'loss',
    'lupi_svm',
    'max_abs_scaler',
    'mean_baseline',
    'mean_imputation',
    'meta_feature_extractor',
    'min_max_scaler',
    'monomial',
    'multinomial_naive_bayes',
    'multitable_featurization',
    'mutual_info_classif',
    'naive_bayes',
    'ndarray_to_dataframe',
    'ndarray_to_list',
    'nk_sent2vec',
    'non_parametric_clustering',
    'normalizer',
    'null',
    'number_of_clusters',
    'nystroem',
    'one_hot_encoder',
    'one_hot_maker',
    'out_of_core_adjacency_spectral_embedding',
    'owl_regression',
    'pass_to_ranks',
    'passive_aggressive',
    'pca',
    'pca_features',
    'pcp_ialm',
    'polynomial_features',
    'primitive_sum',
    'profiler',
    'pyglrm_d3huber_pca',
    'pyglrm_d3low_rank_imputer',
    'quadratic_discriminant_analysis',
    'random',
    'random_forest',
    'random_projection_timeseries_featurization',
    'random_sampling_imputer',
    'random_trees_embedding',
    'rbf_sampler',
    'redact_targets',
    'relationalt_imeseries',
    'remove_columns',
    'remove_duplicate_columns',
    'remove_semantic_types',
    'replace_semantic_types',
    'resnet50_image_feature',
    'reverse',
    'rfd',
    'rfe',
    'rffeatures',
    'rfm_precondition_ed_gaussian_krr',
    'rfm_precondition_ed_polynomial_krr',
    'ridge',
    'robust_scaler',
    'rpca_lbd',
    'score_based_markov_blanket',
    'search',
    'search_hybrid',
    'search_hybrid_numeric',
    'search_numeric',
    'seeded_graph_matching',
    'segment_curve_fitter',
    'select_fwe',
    'select_percentile',
    'sequence_to_bag_of_tokens',
    'sgd',
    'signal_dither',
    'signal_framer',
    'signal_mfcc',
    'simon',
    'simultaneous_markov_blanket',
    'spectral_graph_clustering',
    'ssc_admm',
    'ssc_cvx',
    'ssc_omp',
    'stack_ndarray_column',
    'stacking_operator',
    'standard_scaler',
    'sum',
    'svc',
    'svr',
    'targets_reader',
    'tensor_machines_binary_classification',
    'tensor_machines_regularized_least_squares',
    'text_reader',
    'tfidf_vectorizer',
    'time_series_to_list',
    'train_score_dataset_split',
    'trecs',
    'tree_augmented_naive_bayes',
    'truncated_svd',
    'unary_encoder',
    'unicorn',
    'uniform_segmentation',
    'unseen_label_decoder',
    'unseen_label_encoder',
    'update_semantictypes',
    'variance_threshold',
    'vertex_nomination',
    'vertex_nomination_parser',
    'vertex_nomination_seeded_graph_matching',
    'vertical_concatenate',
    'vgg16',
    'vgg16_image_feature',
    'video_reader',
    'voting',
    'word_2_vec',
    'zero_count'
]
