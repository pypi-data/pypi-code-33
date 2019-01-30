# -*- coding: utf-8 -*-
"""pyprimed constants.

[description]
:param __version__: pyprimed version
:type __version__: string
:param API_PATH: API path mapping
:type API_PATH: dict
:param API_OPERATIONS: API operations mapping
:type API_OPERATIONS: dict
"""
import sys

__version__ = "2.1.7"

API_PATH = {
    "predictions": "predictions?model.uid={model}&universe.uid={universe}",
    "predictions.prediction": "predictions?from_uid={from_uid}&to_uid={to_uid}",
    "apikeys": "apikeys",
    "apikeys.apikey": "apikeys/{apikey}",
    "models": "models",
    "models.model": "models/{model}",
    "universes": "universes",
    "universes.universe": "universes/{universe}",
    "signals": "signals?model.uid={model}",
    "signals.signal": "signals/{signal}",
    "targets": "targets?universe.uid={universe}",
    "targets.target": "targets/{target}",
    "campaigns": "campaigns?universe.uid={universe}",
    "campaigns.campaign": "campaigns/{campaign}",
    "experiments": "experiments?campaign.uid={campaign}",
    "experiments.experiment": "experiments/{experiment}",
    "abvariants": "abvariants?experiment.uid={experiment}",
    "abvariants.abvariant": "abvariants/{abvariant}",
    "users": "users",
    "users.user": "users/{user}",
}

API_OPERATIONS = {
    "predictions": ["UPDATE", "UPSERT", "DELSERT", "DELETE", "TRANSACTION_STATUS"],
    "predictions.prediction": [],
    "apikeys": ["CREATE", "FILTER", "ALL"],
    "apikeys.apikey": ["GET", "UPDATE", "DELETE"],
    "models": ["CREATE", "GET_OR_CREATE", "FILTER", "ALL"],
    "models.model": ["GET", "UPDATE", "DELETE"],
    "universes": ["CREATE", "GET_OR_CREATE", "FILTER", "ALL"],
    "universes.universe": ["GET", "UPDATE", "DELETE"],
    "signals": ["ALL", "FILTER", "UPSERT", "DELSERT", "DELETE", "TRANSACTION_STATUS"],
    "signals.signal": ["GET"],
    "targets": ["ALL", "FILTER", "UPSERT", "DELSERT", "DELETE", "TRANSACTION_STATUS"],
    "targets.target": ["GET"],
    "campaigns": ["CREATE", "GET_OR_CREATE", "FILTER", "ALL"],
    "campaigns.campaign": ["GET", "UPDATE", "DELETE", "PERSONALISE"],
    "experiments": ["CREATE", "FILTER", "ALL"],
    "experiments.experiment": ["GET", "UPDATE", "DELETE"],
    "abvariants": ["CREATE", "FILTER", "ALL"],
    "abvariants.abvariant": ["GET", "UPDATE", "DELETE"],
    "users": ["CREATE", "FILTER", "ALL"],
    "users.user": ["GET", "UPDATE", "DELETE"],
}

# API_RESOURCE = {
#   'models':                               Collection(Model),
#   'models.model':                         Model,
#   'models.model.signals':                 Collection(Signal),
#   'models.model.signals.signal':          Signal
# }

# 'about_edited':           'r/{subreddit}/about/edited/',
# 'live_focus':             'live/{thread_id}/updates/{update_id}',
# 'multireddit_update':     'api/multi/user/{user}/m/{multi}/r/{subreddit}'}
