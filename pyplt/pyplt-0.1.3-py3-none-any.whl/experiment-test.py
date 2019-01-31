from pyplt.experiment import Experiment
from pyplt.plalgorithms.ranksvm import RankSVM
from pyplt.util.enums import KernelType
from pyplt.evaluation.cross_validation import KFoldCrossValidation
import time

exp = Experiment()

# load ratings data
exp.load_single_data("..\\sample data sets\\single_synth.csv", has_ids=True, has_fnames=True)

# set up RankSVM algorithm
pl_algorithm = RankSVM(kernel=KernelType.RBF, gamma=1)
exp.set_pl_algorithm(pl_algorithm)

# set up K-Fold Cross Validation
pl_evaluator = KFoldCrossValidation(k=3)
exp.set_pl_evaluator(pl_evaluator)

# run the experiment
exp.run()

# save the results
t = time.time()
exp.save_exp_log(t, path="my_results.csv")
