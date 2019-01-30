class PersonaliseResult:
    def __init__(self, target, fscore, components, ruuid, recency_factor, **kwargs):

        self.target = target
        self.fscore = fscore
        self.components = components
        self.ruuid = ruuid
        self.recency_factor = recency_factor

        for key, value in kwargs.items():
            setattr(self, key, value)


class PersonaliseResultWrapper:
    def __init__(
        self, experiment, guuid, campaign, query_latency_ms, results=[], **kwargs
    ):

        self.experiment = experiment
        self.guuid = guuid
        self.campaign = campaign

        self._results = []
        self._query_latency_ms = query_latency_ms

        for key, value in kwargs.items():
            setattr(self, key, value)

        for result in results:
            self._results.append(PersonaliseResult(**result))

    @property
    def first(self):
        return self._results[0]

    @property
    def latency(self):
        return self._query_latency_ms

    def __getitem__(self, i):
        return self._results[i]

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __len__(self):
        return len(self._results)
