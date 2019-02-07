import pandas as pd


class ExperimentData:
    def __init__(self):
        self.run_time = 0.0
        self.dockets = []

    def casesToDataFrame(self):
        frame = pd.DataFrame({
            'id': [c.id for c in self.cases],
            'docketId': [c.docket.id for c in self.cases],
            'pConvict': [c.prob_convict for c in self.cases],
            'maxSentence': [c.sentence_if_convicted for c in self.cases],
            'plead': [c.plead for c in self.cases],
            'tried': [c.tried for c in self.cases],
            'acquitted': [c.acquitted for c in self.cases],
            'convicted': [c.convicted for c in self.cases],
            'guilty': [c.guilty for c in self.cases],
            'sentence': [c.sentence for c in self.cases],
        },index=[[c.docket.id for c in self.cases],[c.id for c in self.cases]])
        frame.index.names = ['docket', 'case']
        return frame

    @property
    def cases(self):
        return [c for d in self.dockets for c in d.cases]

    @property
    def cases_plead(self):
        return [c for c in self.cases if c.plead]

    @property
    def cases_tried(self):
        return [c for c in self.cases if c.tried]

    @property
    def cases_decided(self):
        return [c for c in self.cases if c.tried or c.plead]

    @property
    def cases_acquitted(self):
        return [c for c in self.cases_tried if c.acquitted]

    @property
    def cases_convicted(self):
        return [c for c in self.cases_tried if c.convicted]

    @property
    def cases_guilty(self):
        return [c for c in self.cases if c.guilty]

    @property
    def cases_not_guilty(self):
        return [c for c in self.cases if not c.guilty]

    @property
    def sentences(self):
        return [c.sentence for c in self.cases_decided]
