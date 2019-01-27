import random
import numpy as np
from collections import OrderedDict
from sklearn import metrics
from dautil import collect
from dautil import log_api
from sklearn.tree import DecisionTreeClassifier
import ast
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import ExtraTreesClassifier
import time


class Evolver():
    def __init__(self, X_train, X_test, y_train, y_test, n_jobs=1,
                 candidates=None, ngen=10, pop_size=200, to_beat=0):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.candidates = candidates
        self.ngen = ngen
        self.pop_size = pop_size
        self.to_beat = to_beat
        self.log = log_api.conf_logger(__name__)
        self.nevals = 0
        self.cxpb = 0.6
        self.pop = []
        self.score_lookup = {}
        self.start_time = time.time()
        self.toppers = pd.DataFrame(columns=['score', 'params'])
        self.n_jobs = n_jobs
        self.parallel = False
        self.base_estimator = None
        self.pred_dict = {}

    def done_ratio(self):
        return self.nevals/(self.ngen * self.pop_size)

    def mutate_all(self, apop):
        mutpb = np.random.random_sample(size=len(apop))

        for i in range(len(apop)):
            if mutpb[i] < 1 - self.done_ratio():
                apop[i] = self.mutate(apop[i])

        return apop

    def evolve(self):
        for i in range(self.pop_size):
            self.pop.append(self.create_individual())

        for i in range(self.ngen):
            new_pop = []
            new_pop.extend(self.select())
            offspring = self.mate()

            for child in offspring:
                new_pop.append(child)

            self.pop = self.mutate_all(new_pop)
            self.log.info('Generation {0} of {1}'.format(i, self.ngen))
            self.toppers.to_csv('evolved_toppers.csv')

        hof = pd.DataFrame(columns=['score', 'pop'])
        hof['score'] = [self.evaluate(ind) for ind in self.pop]
        hof['pop'] = self.pop

        return hof.sort(['score'], ascending=False)

    def mate(self):
        offspring = []
        pairs = np.random.choice(range(len(self.pop)),
                                 size=(self.cxpb/2 * len(self.pop), 2),
                                 p=self.hypo_prob)

        for pair in pairs:
            offspring.extend(self.xover(self.pop[pair[0]],
                                        self.pop[pair[1]]))

        return offspring

    def xover(self, parent1, parent2):
        half = int(len(parent1)/2)
        xpoints = (random.randint(0, half),
                   random.randint(half, len(parent1)))

        p2 = parent2

        if str(parent1) == str(parent2):
            p2 = self.create_individual()
            self.log.debug('Parents similar')
        else:
            preds1 = self.pred_dict.get(str(parent1), None)
            preds2 = self.pred_dict.get(str(parent2), None)

            if preds1 is not None and preds2 is not None:
                if np.corrcoef(preds1, preds2)[0][1] > 0.9:
                    p2 = self.create_individual()
                    self.log.debug('Parents similar 0.9')

        child1 = parent1[:xpoints[0]]
        child2 = p2[:xpoints[0]]

        child1.extend(p2[xpoints[0]: xpoints[1]])
        child2.extend(parent1[xpoints[0]: xpoints[1]])

        child1.extend(parent1[xpoints[1]:])
        child2.extend(p2[xpoints[1]:])

        return [child1, child2]

    def select(self):
        scores = np.array([self.evaluate(ind) for ind in self.pop])
        fitness = scores ** 2
        self.hypo_prob = fitness/fitness.sum()

        '''
        sel = np.random.choice(range(len(self.pop)),
                               size=(1 - self.cxpb) * len(self.pop),
                               p=self.hypo_prob)

        return [self.pop[i] for i in sel]
                               '''

        sel = []

        for i in range(int((1 - self.cxpb) * len(self.pop))):
            first = random.randint(0, len(scores) - 1)
            second = random.randint(0, len(scores) - 1)

            if scores[first] > scores[second]:
                sel.append(self.pop[first])
            else:
                sel.append(self.pop[second])

        return sel

    def evaluate(self, ind):
        self.nevals += 1
        prev = self.score_lookup.get(str(ind))

        if prev:
            self.log.debug('Returning old value for {0}'.format(str(ind)))

            return prev

        clf = self.clazz()
        ind_params = {item[0]: item[1] for item in ind}

        if self.parallel:
            ind_params['n_jobs'] = self.n_jobs

        if self.base_estimator:
            ind_params['base_estimator'] = self.base_estimator

        clf.set_params(**ind_params)
        clf.fit(self.X_train, self.y_train)
        preds = clf.predict(self.X_test)
        self.pred_dict[str(ind)] = preds
        accuracy = metrics.accuracy_score(self.y_test, preds)

        if prev is None:
            self.score_lookup[str(ind)] = accuracy

        if accuracy > self.to_beat or self.nevals % 2 == 0:
            msg = 'Elapsed {3} s, eval={2}, accuracy={0} ind={1}'
            self.log.debug(msg.format(accuracy,
                                      ind, self.nevals,
                                      round(time.time() - self.start_time)))
            if accuracy > self.to_beat:
                collect.add_df_row(self.toppers,  [accuracy, str(ind)])

        return accuracy

    def pick_criterion(self):
        return random.choice(['gini', 'entropy'])

    def pick_max_features(self):
        return random.choice(['auto', 'sqrt', 'log2', None])

    def pick_max_depth(self):
        return random.randint(2, 7)

    def pick_min_weight_fraction_leaf(self):
        return 0.5 * random.random()

    def pick_min_samples_leaf(self):
        return random.randint(1, 17)

    def pick_min_samples_split(self):
        return random.randint(1, 7)

    def dict2tuple_list(self, ind):
        ordered = OrderedDict(sorted(ind.items(), key=lambda t: t[0]))

        return [(k, v) for k, v in ordered.items()]


class GBCEvolver(Evolver):
    def __init__(self, *args, **kwargs):
        super(GBCEvolver, self).__init__(*args, **kwargs)
        self.clazz = GradientBoostingClassifier

    def pick_nestimators(self):
        return random.randint(2, 100)

    def pick_loss(self):
        return random.choice(['deviance', 'exponential'])

    def create_individual(self):
        ind = {}

        if self.candidates is None:
            ind['n_estimators'] = self.pick_nestimators()
            ind['loss'] = self.pick_loss()
            ind['max_depth'] = self.pick_max_depth()
            ind['min_samples_split'] = self.pick_min_samples_split()
            ind['min_samples_leaf'] = self.pick_min_samples_leaf()
            ind['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()
            ind['max_features'] = self.pick_max_features()
        else:
            ind = ast.literal_eval(random.choice(self.candidates))

        return self.dict2tuple_list(ind)

    def mutate(self, ind):
        akey = random.choice([k for k in ind])

        if akey == 'loss':
            ind['loss'] = self.pick_loss()
        elif akey == 'n_estimators':
            ind['n_estimators'] = self.pick_nestimators()
        elif akey == 'max_depth':
            ind['max_depth'] = self.pick_max_depth()
        elif akey == 'min_samples_split':
            ind['min_samples_split'] = self.pick_min_samples_split()
        elif akey == 'min_samples_leaf':
            ind['min_samples_leaf'] = self.pick_min_samples_leaf()
        elif akey == 'min_weight_fraction_leaf':
            ind['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()

        return ind


class AdaEvolver(Evolver):
    def __init__(self, *args, **kwargs):
        super(AdaEvolver, self).__init__(*args, **kwargs)
        self.clazz = AdaBoostClassifier

    def pick_nestimators(self):
        return random.randint(2, 100)

    def pick_algorithm(self):
        return random.choice(['SAMME', 'SAMME.R'])

    def create_individual(self):
        ind = {}

        if self.candidates is None:
            ind['n_estimators'] = self.pick_nestimators()
            ind['algorithm'] = self.pick_algorithm()
        else:
            ind = ast.literal_eval(random.choice(self.candidates))

        return self.dict2tuple_list(ind)

    def mutate(self, ind):
        akey = random.choice([k for k in ind])

        if akey == 'algorithm':
            ind['algorithm'] = self.pick_algorithm()
        elif akey == 'n_estimators':
            ind['n_estimators'] = self.pick_nestimators()

        return ind


class RFCEvolver(Evolver):
    def __init__(self, *args, **kwargs):
        super(RFCEvolver, self).__init__(*args, **kwargs)
        self.clazz = RandomForestClassifier
        self.parallel = True

    def pick_class_weight(self):
        return random.choice(['balanced', 'balanced_subsample', None])

    def pick_nestimators(self):
        return random.randint(2, 100)

    def create_individual(self):
        ind = {}

        if self.candidates is None:
            ind['n_estimators'] = self.pick_nestimators()
            ind['class_weight'] = self.pick_class_weight()
            ind['criterion'] = self.pick_criterion()
            ind['max_features'] = self.pick_max_features()
            ind['max_depth'] = self.pick_max_depth()
            ind['min_samples_split'] = self.pick_min_samples_split()
            ind['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()
            ind['min_samples_leaf'] = self.pick_min_samples_leaf()
        else:
            ind = ast.literal_eval(random.choice(self.candidates))

        return self.dict2tuple_list(ind)

    def mutate(self, ind):
        akey = random.choice([k for k in ind])[0]

        ind_dict = {k: v for k, v in ind}

        if akey == 'class_weight':
            ind_dict['class_weight'] = self.pick_class_weight()
        elif akey == 'criterion':
            ind_dict['criterion'] = self.pick_criterion()
        elif akey == 'max_depth':
            ind_dict['max_depth'] = self.pick_max_depth()
        elif akey == 'min_samples_split':
            ind_dict['min_samples_split'] = self.pick_min_samples_split()
        elif akey == 'min_weight_fraction_leaf':
            ind_dict['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()
        elif akey == 'min_samples_leaf':
            ind_dict['min_samples_leaf'] = self.pick_min_samples_leaf()
        elif akey == 'n_estimators':
            ind_dict['n_estimators'] = self.pick_nestimators()
        elif akey == 'max_features':
            ind_dict['max_features'] = self.pick_max_features()
        else:
            raise ValueError('Unknown key {}'.format(akey))

        return self.dict2tuple_list(ind_dict)


class ETCEvolver(RFCEvolver):
    def __init__(self, *args, **kwargs):
        super(ETCEvolver, self).__init__(*args, **kwargs)
        self.clazz = ExtraTreesClassifier


class DTCEvolver(Evolver):
    def __init__(self, *args, **kwargs):
        super(DTCEvolver, self).__init__(*args, **kwargs)
        self.clazz = DecisionTreeClassifier

    def pick_class_weight(self):
        return random.choice(['balanced', None])

    def pick_splitter(self):
        return random.choice(['best', 'random'])

    def create_individual(self):
        ind = {}

        if self.candidates is None:
            ind['class_weight'] = self.pick_class_weight()
            ind['criterion'] = self.pick_criterion()
            ind['max_features'] = self.pick_max_features()
            ind['max_depth'] = self.pick_max_depth()
            ind['splitter'] = self.pick_splitter()
            ind['min_samples_split'] = self.pick_min_samples_split()
            ind['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()
            ind['min_samples_leaf'] = self.pick_min_samples_leaf()
        else:
            ind = ast.literal_eval(random.choice(self.candidates))

        return self.dict2tuple_list(ind)

    def mutate(self, ind):
        akey = random.choice([k for k in ind])[0]
        ind_dict = {k: v for k, v in ind}

        if akey == 'class_weight':
            ind_dict['class_weight'] = self.pick_class_weight()
        elif akey == 'criterion':
            ind_dict['criterion'] = self.pick_criterion()
        elif akey == 'splitter':
            ind_dict['splitter'] = self.pick_splitter()
        elif akey == 'max_depth':
            ind_dict['max_depth'] = self.pick_max_depth()
        elif akey == 'max_features':
            ind_dict['max_features'] = self.pick_max_features()
        elif akey == 'min_samples_split':
            ind_dict['min_samples_split'] = self.pick_min_samples_split()
        elif akey == 'min_weight_fraction_leaf':
            ind_dict['min_weight_fraction_leaf'] = \
                self.pick_min_weight_fraction_leaf()
        elif akey == 'min_samples_leaf':
            ind_dict['min_samples_leaf'] = self.pick_min_samples_leaf()
        else:
            raise ValueError('Unknown key {}'.format(akey))

        return self.dict2tuple_list(ind_dict)
