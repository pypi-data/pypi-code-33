from django.template import Context
from django.template import Template
from django.test import TestCase
from faker import Faker

from django_populate import Faker as DjangoFaker
from django_populate.populator import Populator
from tests.models import Game, Player, Action

fake = Faker()


class PopulatorTestCase(TestCase):

    def test_population(self):
        populator = Populator(fake)
        populator.addEntity(Game, 10)
        self.assertEqual(len(populator.execute()[Game]), 10)

    def test_guesser(self):
        def title_fake(arg):
            title_fake.count += 1
            name = fake.company()
            return name

        title_fake.count = 0

        populator = Populator(fake)
        populator.addEntity(Game, 10, {
            'title': title_fake
        })
        self.assertEqual(len(populator.execute()[Game]), title_fake.count)

    def testFormatter(self):
        populator = Populator(fake)

        populator.addEntity(Game, 5)
        populator.addEntity(Player, 10, {
            'score': lambda x: fake.random_int(0, 1000),
            'nickname': lambda x: fake.email()
        })
        populator.addEntity(Action, 30)

        inserted_pks = populator.execute()

        self.assertTrue(len(inserted_pks[Game]) == 5)
        self.assertTrue(len(inserted_pks[Player]) == 10)

        self.assertTrue(any([0 <= p.score <= 1000 and '@' in p.nickname for p in Player.objects.all()]))


class TemplateTagsTestCase(TestCase):

    @staticmethod
    def render(template, context=None):
        t = Template("{% load fakers %}" + template)
        c = Context(context or {})
        text = t.render(c)
        return text

    # do_fake: fake
    def testSimpleFakeTag(self):
        self.assertNotEqual(self.render("{% fake 'name' as myname %}{{ myname }}"), "")

    def testSimpleFakeTagWithArguments(self):
        self.assertNotEqual(self.render("{% fake 'date_time_between' '-10d' as mydate %}{{ mydate }}"), "")

    def testSimpleFakeTagFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{% fake 'not_founded_fake' as foo %}")

    def testSimpleFakeTagOptionalAssignment(self):
        self.assertNotEqual(self.render("{% fake 'name' %}"), "")
        self.assertEqual(len(self.render("{% fake 'md5' %}")), 32)

    # do_fake_filter: fake
    def testFakeFilterTag(self):
        self.assertIn(self.render("{{ 'random_element'|fake:'test_string' }}"), 'test_string')

    def testFakeFilterWithValueFromContext(self):
        mylist = [100, 200, 300]
        rendered = self.render("{{ 'random_element'|fake:mylist }}", {'mylist': mylist})
        self.assertIn(int(rendered), mylist)

    def testFakeFilterFormatterNotFoundRaisesException(self):
        with self.assertRaises(AttributeError):
            self.render("{{ 'not_founded_fake'|fake:mylist }}", {'mylist': [100, 200, 300]})

    def testFakeFilterAsIfCondition(self):
        self.assertEqual(self.render("{% if 'boolean'|fake:100 %}True forever{% endif %}"), "True forever")
        self.assertEqual(self.render("{% if 'boolean'|fake:0 %}{% else %}False forever{% endif %}"), "False forever")

    def testFakeFilterAsForInRange(self):
        times = 10
        rendered = self.render("{% for word in 'words'|fake:times %}{{ word }}\n{% endfor %}", {'times': times})
        words = [word for word in rendered.split('\n') if word.strip()]
        self.assertEqual(len(words), times)

    # do_or_fake_filter: or_fake
    def testOrFakeFilterTag(self):
        self.assertEqual(len(self.render("{{ unknown_var|or_fake:'md5' }}")), 32)

    def testFullXmlContact(self):
        self.assertTrue(self.render("""<?xml version="1.0" encoding="UTF-8"?>
<contacts>
    {% fake 'random_int' 10 20 as times %}
    {% for i in 10|get_range %}
    <contact firstName="{% fake 'first_name' %}" lastName="{% fake 'last_name' %}" email="{% fake 'email' %}"/>
        <phone number="{% fake 'phone_number' %}"/>
        {% if 'boolean'|fake:25 %}
        <birth date="{{ 'date_time_this_century'|fake|date:"D d M Y" }}" place="{% fake 'city' %}"/>
        {% endif %}
        <address>
            <street>{% fake 'street_address' %}</street>
            <city>{% fake 'city' %}</city>
            <postcode>{% fake 'postcode' %}</postcode>
            <state>{% fake 'state' %}</state>
        </address>
        <company name="{% fake 'company' %}" catch-phrase="{% fake 'catch_phrase' %}">
        {% if 'boolean'|fake:25 %}
            <offer>{% fake 'bs' %}</offer>
        {% endif %}
        {% if 'boolean'|fake:33 %}
            <director name="{% fake 'name' %}" />
        {% endif %}
        </company>
        {% if 'boolean'|fake:15 %}
        <details>
        <![CDATA[
        {% fake 'text' 500 %}
        ]]>
        </details>
        {% endif %}
    </contact>
    {% endfor %}
</contacts>
"""))


class APIDjangoFakerTestCase(TestCase):

    def testDjangoFakerSingleton(self):
        self.assertEqual(DjangoFaker(), DjangoFaker())
        self.assertIs(DjangoFaker(), DjangoFaker())

    def testFakerCacheGenerator(self):
        self.assertEqual(DjangoFaker().getGenerator(), DjangoFaker().getGenerator())
        self.assertIs(DjangoFaker().getGenerator(), DjangoFaker().getGenerator())
        self.assertIs(DjangoFaker().getGenerator(codename='default'), DjangoFaker().getGenerator(codename='default'))

        self.assertEqual(DjangoFaker().getGenerator(locale='it_IT'), DjangoFaker().getGenerator(locale='it_IT'))
        self.assertIs(DjangoFaker().getGenerator(locale='it_IT'), DjangoFaker().getGenerator(locale='it_IT'))

    def testFakerCachePopulator(self):
        self.assertEqual(DjangoFaker().getPopulator(), DjangoFaker().getPopulator())
        self.assertIs(DjangoFaker().getPopulator(), DjangoFaker().getPopulator())
        self.assertIs(DjangoFaker().getPopulator().generator, DjangoFaker().getPopulator().generator)

        self.assertEqual(DjangoFaker().getPopulator(locale='it_IT'), DjangoFaker().getPopulator(locale='it_IT'))
        self.assertIs(DjangoFaker().getPopulator(locale='it_IT'), DjangoFaker().getPopulator(locale='it_IT'))
