
from neuropredict import config_neuropredict as cfg

class Experiment:
    """
    Class defining an neuropredict experiment to be run.

    Encapsulates all the details necessary for execution,
        hence easing the save/load/decide workflow.

    Attributes
    ----------



    """


    def __init__(self,
                 sample_ids=None,
                 classes=None,
                 train_perc=cfg.default_train_perc,
                 classifier_name=cfg.default_classifier,
                 feat_select_method=cfg.default_feat_select_method,
                 grid_search_level=cfg.GRIDSEARCH_LEVEL_DEFAULT,
                 feature_selection_size=cfg.default_num_features_to_select,
                 num_procs=cfg.DEFAULT_NUM_PROCS,
                 num_rep_cv=cfg.default_num_repetitions,
                 positive_class=None,
                 sub_groups=None,
                 fs_subject_dir=None,
                 user_feature_type=None,
                 user_feature_paths=None):


        pass
