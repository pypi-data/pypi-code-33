import timeit
import typing as typ

from crimjustsimpy import Trial, PleaBargainingStrategy, ExperimentData, Docket


class Experiment:

    def __init__(self, *, docket_factory:typ.Iterator[Docket], trial:Trial,
                 plea_bargaining:PleaBargainingStrategy):
        self.docket_factory = docket_factory
        self.trial = trial
        self.plea_bargaining = plea_bargaining

        self.dockets = []

    def run(self,iterations:int) -> ExperimentData:
        start = timeit.default_timer()
        self._simulate(iterations)
        end = timeit.default_timer()

        data = ExperimentData()
        data.run_time = end - start
        data.dockets = self.dockets

        return data

    def _simulate(self, iterations):
        for i in range(iterations):
            self._simulate_docket()

    def _simulate_docket(self):

        # Create the docket.
        docket = next(self.docket_factory)
        self.dockets.append(docket)

        # Plea bargaining phase.
        self.plea_bargaining.bargain(docket)

        # Trials for remaining cases.
        for case in docket.cases:
            if not (case.plead):
                self.trial.try_case(case)
