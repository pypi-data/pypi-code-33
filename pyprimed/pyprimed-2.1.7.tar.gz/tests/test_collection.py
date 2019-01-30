import pytest
import pyprimed

@pytest.mark.unit
class TestCollection:
    def test_paths(self, pio):
        universe = pyprimed.models.universe.Universe(parent=pio.universes, uid='universe_uid')
        model = pyprimed.models.model.Model(parent=pio.models, uid='model_uid')
        apikey = pyprimed.models.apikey.Apikey(parent=pio.apikeys, uid='apikey_uid')
        user = pyprimed.models.user.User(parent=pio.users, uid='user_uid')

        campaign = pyprimed.models.campaign.Campaign(parent=universe.campaigns, uid='campaign_uid')
        experiment = pyprimed.models.experiment.Experiment(parent=campaign.experiments, uid='experiment_uid')
        abvariant = pyprimed.models.abvariant.Abvariant(parent=experiment.abvariants, uid='abvariant_uid')
        signal = pyprimed.models.signal.Signal(parent=model.signals, uid='signal_uid')
        target = pyprimed.models.target.Target(parent=universe.targets, uid='target_uid')

        assert pio.users.path == 'users'
        assert pio.apikeys.path == 'apikeys'
        assert pio.models.path == 'models'
        assert pio.universes.path == 'universes'

        assert universe.targets.path == 'targets?universe.uid=universe_uid'
        assert universe.campaigns.path == 'campaigns?universe.uid=universe_uid'
        assert model.signals.path == 'signals?model.uid=model_uid'
        assert campaign.experiments.path == 'experiments?campaign.uid=campaign_uid'
        assert experiment.abvariants.path == 'abvariants?experiment.uid=experiment_uid'

        assert pio.predictions.on(model=model, universe=universe).path == 'predictions?model.uid=model_uid&universe.uid=universe_uid'

        assert abvariant.uri == 'abvariants/abvariant_uid'
        assert apikey.uri == 'apikeys/apikey_uid'
        assert campaign.uri == 'campaigns/campaign_uid'
        assert experiment.uri == 'experiments/experiment_uid'
        assert model.uri == 'models/model_uid'
        assert signal.uri == 'signals/signal_uid'
        assert target.uri == 'targets/target_uid'
        assert universe.uri == 'universes/universe_uid'
        assert user.uri == 'users/user_uid'
