# Standard modules
import datetime

# External dependencies
import pytest

# Local modules
from .context import vigil
from vigil import output


@pytest.mark.usefixtures('nosave')
class TestCollection:
    """
    Class to test collection methods.
    """

    def test_check(self, collection, nonotify):
        """
        Test if collection checks properly.
        """
        collection.update('html', 'date', datetime.datetime.utcnow())
        collection.check()
        assert not collection.get('html').diff
        assert collection.get('xml').diff

    def test_check_force(self, collection, nonotify):
        """
        Collection should check all watches with force=True
        """
        date = datetime.datetime.utcnow()
        for watch in collection.get_all():
            collection.update(watch.name, 'date', date)

        collection.check(force=True)
        for watch in collection.get_all():
            assert watch.diff

    def test_add(self, collection, watch):
        """
        Watch should be added to the collection.
        """
        collection.add(watch)
        assert collection.get(watch.name)

    def test_remove(self, collection, watch):
        """
        Watch with given name should be removed from the collection.
        """
        collection.add(watch)
        assert collection.get(watch.name)
        collection.remove(watch.name)
        assert not collection.get(watch.name)

    @pytest.fixture(params=[['url', 'changed'],
                            ['content', 'changed'],
                            ['diff', 'changed'],
                            ['interval', datetime.timedelta(days=10)],
                            ['date', datetime.datetime(2222, 2, 2)],
                            ['tolerance', 10]])
    def update_list(self, request):
        return request.param[0], request.param[1]

    def test_update(self, collection, update_list):
        """
        Attribute of given watch should be updated to new value.
        """
        key, value = update_list
        collection.update('html', key, value)
        watch = collection.get('html')
        assert watch.as_dict()[key] == value

    def test_get(self, collection):
        """
        Should return watch with corresponding name or url.
        """
        gol = collection.get('html')
        assert gol.url == 'http://httpbin.org/html'
        blog = collection.get('http://httpbin.org/xml')
        assert blog.name == 'xml'

    def test_get_all(self, collection):
        """
        Should return all watches in database.
        """
        watches = collection.get_all()
        assert len(watches) == 2

    def test_get_updated(self, collection):
        """
        Should return all updated watched in database.
        """
        collection.update('html', 'diff', 'updated')
        watches = collection.get_updated()
        assert len(watches) == 1

    def test_seen_all(self, collection):
        """
        Should set change to False for all Watch objects in collection.
        """
        for watch in collection.get_all():
            collection.update(watch.name, 'diff', 'updated')

        collection.seen_all()
        for watch in collection.get_all():
            assert not watch.diff

    def test_send_notification(self,
                               collection,
                               monkeypatch,
                               inbox):
        """
        Should send url of changed watches.
        """
        monkeypatch.setitem(collection.config, 'send_diff', False)
        for watch in collection.get_all():
            collection.update(watch.name, 'diff', 'updated')

        collection.send_notification()

        assert not collection.get_updated()
        assert len(inbox) == 1
        assert 'http://' in inbox[0].get_message()

    def test_send_notification_diff(self,
                                    collection,
                                    monkeypatch,
                                    inbox):
        """
        Should send the diff of changed watches.
        """
        monkeypatch.setitem(collection.config, 'send_diff', True)
        for watch in collection.get_all():
            collection.update(watch.name, 'diff', 'diff')

        collection.send_notification()

        assert not collection.get_updated()
        assert len(inbox) == 1
        assert 'httpbin.org/html' in inbox[0].get_message()
        assert 'httpbin.org/xml' in inbox[0].get_message()

    def test_send_notification_separately(self,
                                          collection,
                                          monkeypatch,
                                          inbox):
        """
        Should send changes one by one instead of aggregate.
        """
        monkeypatch.setitem(collection.config, 'send_aggregate', False)
        for watch in collection.get_all():
            collection.update(watch.name, 'diff', 'diff')

        collection.send_notification()

        assert not collection.get_updated()
        assert len(inbox) == 2
        assert 'diff' in inbox[0].get_message()
        assert 'diff' in inbox[1].get_message()


@pytest.mark.usefixtures('nosave')
class TestCollectionBadInput:
    """
    Class for testing bad input in collection methods.
    """

    def test_name_not_unique(self, collection, watch):
        """
        Adding Watch with the same name should raise ValueError.
        """
        collection.add(watch)
        assert collection.get(watch.name)
        with pytest.raises(ValueError):
            watch.url = 'http://www.different.example'
            collection.add(watch)

    def test_url_not_unique(self, collection, watch):
        """
        Adding Watch with the same url should raise ValueError.
        """
        collection.add(watch)
        assert collection.get(watch.name)
        with pytest.raises(ValueError):
            watch.name = 'different name'
            collection.add(watch)

    def test_remove_non_existant(self, collection, watch):
        """
        Removing Watch that is not in collection should raise ValueError.
        """
        with pytest.raises(ValueError):
            collection.remove(watch.name)

    def test_get_outputs_multiple(self, collection):
        """
        Should return an Output class.
        """
        for out in collection._get_outputs():
            assert issubclass(out, output.Output)

    def test_get_outputs_one(self, collection):
        """
        Should return an Output class.
        """
        collection.config['output'] = 'email'
        for out in collection._get_outputs():
            assert issubclass(out, output.Output)
