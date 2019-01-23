from skmultiflow.data import FileStream, LEDGenerator
from skmultiflow.evaluation import EvaluatePrequential
from skmultiflow.trees import HoeffdingTree
from skmultiflow.trees import HAT
from skmultiflow.meta import AdaptiveRandomForest


def demo():
    """ _test_pipeline

    This demo demonstrates the Pipeline structure seemingly working as a
    learner, while being passed as parameter to an EvaluatePrequential
    object.

    """
    # # Setup the stream
    dataset = 'elecNormNew'
    stream = FileStream("~/Documents/workspace/datasets/" + dataset + ".csv")

    # # If used for Hoeffding Trees then need to pass indices for Nominal attributes

    # Test with RandomTreeGenerator
    # stream = RandomTreeGenerator(n_classes=2, n_numerical_attributes=5)
    # stream.prepare_for_use()

    # Test with WaveformGenerator
    # stream = WaveformGenerator()
    # stream.prepare_for_use()

    # Setup the classifier
    nominal_attr_idx = []
    if dataset == 'covtype_pp':
        for i in range(10, 54):
            nominal_attr_idx.append(i)
        print(nominal_attr_idx)
    # elif dataset == 'agr_a':
    #     nominal_attr_idx = [2,3,4,5,7]
    elif dataset == 'airlines':
        for i in range(5):
            nominal_attr_idx.append(i)
        print(nominal_attr_idx)
    elif dataset == 'elecNormNew':
        nominal_attr_idx.append(1)
        print(nominal_attr_idx)

    classifier = []
    classifier.append(HoeffdingTree(nominal_attributes=nominal_attr_idx, leaf_prediction='nba'))
    # classifier.append(HAT(nominal_attributes=nominal_attr_idx))
    classifier.append(AdaptiveRandomForest(n_estimators=5, random_state=1))

    # Prepare stream
    stream.prepare_for_use()
    print('Instances remaining: ', stream.n_remaining_samples())
    # if isinstance(cfr, HAT):
    #     alg = 'HAT'
    # elif isinstance(cfr, HoeffdingTree):
    #     alg = 'HT'
    # elif isinstance(cfr, AdaptiveRandomForest):
    #     alg = 'ARF'

    # Setup the evaluator
    # evaluate = EvaluatePrequential(pretrain_size=1000, max_samples=1000000,
    #                                output_file='results_' + dataset + '_' + alg + '.csv')
    # evaluator = EvaluatePrequential(show_plot=True, pretrain_size=1000, max_samples=1000000, max_time=10000,
    #                                 output_file='test.csv')
    evaluator = EvaluatePrequential(show_plot=True, max_samples=100000)

    # Evaluate
    evaluator.evaluate(stream=stream, model=classifier, model_names=['HT', 'ARF'])

    print('Instances remaining: ', stream.n_remaining_samples())
    print('Done: ', dataset)


if __name__ == '__main__':
    demo()