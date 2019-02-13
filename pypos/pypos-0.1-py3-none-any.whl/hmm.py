import numpy as np
from typing import Optional


class HMM:
    def __init__(self, n_states: int, n_emissions: int):
        self.n_states = n_states
        self.n_emissions = n_emissions

        self.transition_prob_: Optional[np.ndarray] = None
        self.start_prob_: Optional[np.ndarray] = None
        self.emission_prob_: Optional[np.ndarray] = None


    def fit(self, x: np.ndarray, y: np.ndarray, l: np.ndarray):
        """
        Fits the HMM to the emission sequences with given target sequences
        :param x: Emission sequences (seqlen)
        :param y: Target sequences (seqlen)
        :param l: Lengths of sequences in X and y
        :return: Fitted HMM
        """
        self.start_prob_ = np.zeros((self.n_states,))
        self.emission_prob_ = np.zeros((self.n_states, self.n_emissions))
        self.transition_prob_ = np.zeros((self.n_states, self.n_states))

        ptrs = [0, *np.cumsum(l)]
        for s in y[ptrs[:-1]]:
            self.start_prob_[s] += 1

        for ss, se in zip(ptrs[:-1], ptrs[1:]):
            obs = x[ss:se]  # observation sequence
            hss = y[ss:se]  # hidden state sequence

            for ob, hs in zip(obs, hss):
                self.emission_prob_[hs, ob] += 1

            for hs1, hs2 in zip(hss[:-1], hss[1:]):
                self.transition_prob_[hs1, hs2] += 1

        self.start_prob_ /= np.sum(self.start_prob_)
        self.emission_prob_ = self.emission_prob_ / np.sum(self.emission_prob_, axis=1)[:, None]
        self.transition_prob_ = self.transition_prob_  / np.sum(self.transition_prob_, axis=1)[:, None]

        return self


    def predict(self, x: np.ndarray):
        paths = np.zeros((x.shape[0], self.n_states), dtype='int')
        probs = np.zeros((x.shape[0], self.n_states))
        probs[0] = self.start_prob_ * self.emission_prob_[:, x[0]]

        for i, ob in enumerate(x[1:]):
            p_em = self.emission_prob_[:, ob]

            for s in range(self.n_states):
                in_p = probs[i] * self.transition_prob_[:, s]
                max_in = np.argmax(in_p)
                out_p = in_p[max_in] * p_em[s]
                probs[i+1, s] = out_p
                paths[i+1, s] = max_in

            # in_p = probs[i] * self.transition_prob_.T
            # max_in = np.argmax(in_p, axis=1)
            # out_p = in_p[max_in, np.arange(0, self.n_states)]
            # out_p *= p_em
            # probs[i+1] = out_p
            # paths[i+1] = max_in

        max_out = np.argmax(probs[-1])
        path = [max_out]
        for i in reversed(range(1, x.shape[0])):
            path.append(paths[i, path[-1]])

        return np.array(list(reversed(path)))






    def score(self, x: np.ndarray):
        probs = np.zeros((x.shape[0], self.n_states))
        probs[0] = self.start_prob_ * self.emission_prob_[:, x[0]]
        for i, ob in enumerate(x[1:]):
            probs[i+1] = (probs[i] @ self.transition_prob_) * self.emission_prob_[:, ob]
        return probs
