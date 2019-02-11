import mock

from morphi.registry import Registry


class TestLocalizationRegistry:
    def test_locales(self):
        registry = Registry()

        registry.locales = 'asdf'
        assert 'asdf' == registry.locales

    def test_subscribe(self):
        registry = Registry()
        translator_a = mock.Mock()
        translator_b = mock.Mock()
        assert translator_a not in registry.translators
        assert translator_b not in registry.translators

        registry.subscribe(translator_a)
        registry.subscribe(translator_b)
        assert translator_a in registry.translators
        assert translator_b in registry.translators

    def test_unsubscribe(self):
        registry = Registry()
        translator_a = mock.Mock()
        translator_b = mock.Mock()
        registry.subscribe(translator_a)
        registry.subscribe(translator_b)

        registry.unsubscribe(translator_a)
        assert translator_a not in registry.translators
        assert translator_b in registry.translators

    def test_locales_setter(self):
        registry = Registry()
        translator = mock.Mock()
        registry.subscribe(translator)

        registry.locales = 'asdf'
        assert 'asdf' == registry.locales
        assert 'asdf' == translator.locales
