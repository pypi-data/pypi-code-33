
class Results:
    """
    Class to contains full set of results for a given experiment.

    Attributes
    ----------
        pipeline_set : list of sklearn pipelines
            sklearn pipelines allows a sequence of preprocessing, feature selection and
                estimators to realize the full power of ML techniques for your problem.
            Currently only one pipeline is supported.
            The need for and utility of implementing multiple pipelines is being contemplated.

        metric_set : dict
            Contains the set of the metrics evaluating the predictive performance of the model.
            The most common metric is classification accuracy, and other metrics available are:
                balanced_accuracy : most generically applicable,
                    with experiments with class imbalance and in multi-class experiments.
                AUC (when the classification task is binary),

        probabilities : dict
            Contains predictive probabilities (predicted by the estimator)
                from which the metrics (above) were derived from.
            Note this may not always be available, and often is slower than otherwise.


    """

    def __init__(self,
                 pipeline_set=None,
                 metric_set=None,
                 feature_names=None,
                 ):
        "Constructor."

        self.pipeline_set = pipeline_set
        self.metric_set = metric_set
        self.feature_names = feature_names


    def add_result(self,
                 metric_data=None,
                 probabilities=None,
                 test_labels_predicted=None,
                 test_labels_true=None,
                 confusion_matrices=None,
                 best_params=None,
                 feature_importance=None,
                 num_times_misclassified=None,
                 num_times_tested=None
                 ):
        """
        Method to populate the Results class with predictions/accuracies,
         coming from different repetitions of CV.

        """

        self.metric_data = metric_data
        self.probabilities = probabilities
        self.test_labels_predicted = test_labels_predicted
        self.test_labels_true = test_labels_true
        self.confusion_matrices = confusion_matrices
        self.best_params = best_params
        self.feature_importance = feature_importance
        self.num_times_misclassified = num_times_misclassified
        self.num_times_tested = num_times_tested

    def save(self):
        "Method to persist the results to disk."

    def export(self):
        "Method to export the results to different formats (e.g. CSV)"

    def load(self):
        "Method to load previously saved results e.g. to redo visualizations"


