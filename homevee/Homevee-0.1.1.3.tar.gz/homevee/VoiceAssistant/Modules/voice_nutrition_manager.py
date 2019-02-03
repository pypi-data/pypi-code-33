#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import re

from homevee.Functions.nutrition_data import get_nutrition_data, add_edit_user_day_nutrition_item, get_user_nutrition_overview, \
    get_user_fitness_profile
from homevee.VoiceAssistant.context_keys import ADD_NUTRITION
from homevee.VoiceAssistant.helper import set_context, generate_string
from homevee.VoiceAssistant.voice_patterns import PATTERN_NUTRITION_INFO

MAX_PORTION_DEVIATION = 10

def get_pattern(db):
    return PATTERN_NUTRITION_INFO

def get_label():
    return "nutritiondata"

def run_command(username, text, context, db):
    return voice_get_nutrition_info(username, text, context, db)

def voice_add_nutrition_item(username, text, context, db):
    answer = "add_nutrition_item"

    text = re.sub(r'([\d]+)g', '\1 Gramm', text)

    print text

    words = text.split(" ")

    number_words = ['ein', 'einer', 'eine', 'einem', 'einen']

    amount_words = ['gramm', 'milliliter', 'kilo', 'kilogramm', 'liter', 'stück', 'scheiben', 'scheibe', 'brötchen']

    eat_words = ['esse', 'gegessen', 'essen', 'ess', 'trink', 'trinke', 'trinken', 'getrunken']

    time_words = ['jetzt', 'gerade', 'eben']

    daytime_words = ['morgens', 'morgen', 'mittag', 'mittags', 'abend', 'abends', 'snack', 'snacks', 'zwischendurch']

    is_name = False

    item = None

    amount = None
    amount_type = None

    daytime = None

    current_hour = datetime.datetime.now().hour

    for word in words:
        if(word in time_words):
            daytime = 'snacks'
            if current_hour >= 5 and current_hour < 10:
                daytime = 'morning'
            elif current_hour >= 11 and current_hour < 13:
                daytime = 'noon'
            elif current_hour >= 17 and current_hour < 19:
                daytime = 'evening'

        if(word in daytime_words and daytime is None):
            if word in ['morgens', 'morgen']:
                daytime = 'morning'
            elif word in ['mittag', 'mittags']:
                daytime = 'noon'
            elif word in ['abends', 'abend']:
                daytime = 'evening'
            elif word in ['snack', 'snacks', 'zwischendurch']:
                daytime = 'snacks'

        if is_name and word in eat_words:
            is_name = False

        if is_name:
            if item is None:
                item = word
            else:
                item = item + " " +word

        if word in number_words:
            is_name = True
            amount = 1

        if word in amount_words:
            amount = words[words.index(word)-1]
            amount_type = word
            is_name = True

    print str(item)+" => "+str(amount)+" => "+str(amount_type)+" => "+str(daytime)

    nutrition_data = None

    if(context is not None):

        if('query' in context):
            if(context['query'] == 'amount'):
                for word in words:
                    if word in number_words:
                        amount = 1
                        break

                if amount is None:
                    numbers_in_text = [int(s) for s in text.split() if s.isdigit()]

                    if (len(numbers_in_text) != 0):
                        amount = numbers_in_text[0]
            elif(context['query'] == 'item'):
                item = text
            elif(context['query'] == 'daytime'):
                for word in words:
                    if (word in daytime_words and daytime is None):
                        if word in ['morgens', 'morgen']:
                            daytime = 'morning'
                        elif word in ['mittag', 'mittags']:
                            daytime = 'noon'
                        elif word in ['abends', 'abend']:
                            daytime = 'evening'
                        elif word in ['snack', 'snacks', 'zwischendurch']:
                            daytime = 'snacks'

        if daytime is None and 'daytime' in context and context['daytime'] is not None:
            daytime = context['daytime']

        if amount is None and 'amount' in context and context['amount'] is not None:
            amount = context['amount']

        if amount_type is None and 'amount_type' in context and context['amount_type'] is not None:
            amount_type = context['amount_type']

        if nutrition_data is None and 'nutrition_data' in context and context['nutrition_data'] is not None:
            nutrition_data = context['nutrition_data']
            item = nutrition_data['name']

    #print "Amount: "+str(amount)

    if(item is not None):
        if(nutrition_data is None):
            nutrition_data = get_nutrition_data(username, item, db)

        if(nutrition_data is None or nutrition_data is False):
            answer = "Zum Suchbegriff "+item+" wurden keine Einträge gefunden."
            return {'msg_speech': answer, 'msg_text': answer}

        date = datetime.datetime.today().strftime("%d.%m.%Y")

        if(amount is None):
            answer = "Wie viel " + nutrition_data['portionunit'] + " hast du von " + nutrition_data[
                'name'] + " verzehrt?"
            context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type,
                       'daytime': daytime, 'query': 'amount'}
            set_context(username, ADD_NUTRITION, context, db)
        elif(daytime is None):
            answer = "Wann hast du " + nutrition_data['name'] + " verzehrt? Morgens, Mittags, Abends oder zwischendurch?"
            context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type,
                       'daytime': daytime, 'query': 'daytime'}
            set_context(username, ADD_NUTRITION, context, db)
        else:
            #print "amount: "+str(amount)
            portion_deviation = float(amount) / float(nutrition_data['portionsize'])

            #print portion_deviation

            if(portion_deviation >= MAX_PORTION_DEVIATION or portion_deviation <= 1.0/float(MAX_PORTION_DEVIATION)):
                #invalid portion size

                answer = "Wie viel "+nutrition_data['portionunit']+" hast du von "+nutrition_data['name']+" verzehrt?"
                context = {'nutrition_data': nutrition_data, 'amount': amount, 'amount_type': amount_type, 'daytime': daytime, 'query': 'amount'}
                set_context(username, ADD_NUTRITION, context, db)
            else:
                #anhand der aktuellen uhrzeit die daytime errechnen

                answer = "Ok, " + str(amount) + " " + nutrition_data['portionunit'] + " "+ nutrition_data['name'] +" wurde deinem Ernährungstagebuch hinzugefügt."

                add_edit_user_day_nutrition_item(username, None, date, daytime, nutrition_data['name'], amount,
                                             nutrition_data['portionsize'], nutrition_data['portionunit'],
                                             nutrition_data['calories'], nutrition_data['fat'], nutrition_data['saturated'],
                                             nutrition_data['unsaturated'], nutrition_data['carbs'], nutrition_data['sugar'],
                                             nutrition_data['protein'], db)

                calories_left = get_user_nutrition_overview(username, db)['data']['nutrition_day_data']['calories_left']

                if (calories_left >= 0):
                    answer = answer + ' Du hast heute noch ' + str(calories_left) + ' Kalorien übrig.'
                else:
                    answer = answer + ' Du bist heute ' + str(-1*calories_left) + ' Kalorien über deinem Ziel.'
    else:
        answer = "Was möchtest du deinem Ernährungstagebuch hinzufügen?"
        context = {'amount': amount, 'amount_type': amount_type, 'daytime': daytime, 'query': 'item'}
        set_context(username, ADD_NUTRITION, context, db)

    #determine amount

    #determine product

    return {'msg_speech': answer, 'msg_text': answer}

def voice_get_nutrition_info(username, text, context, db):
    words = text.split(" ")

    number_words = ['ein', 'einer', 'eine', 'einem', 'einen']

    if 'in' in words:
        in_index = words.index('in')
        del words[in_index]

        index = None

        for number_word in number_words:
            if number_word in words:
                index = words.index(number_word)

        if index is not None:
            del words[index]

    nutrition_types = ['fett', 'eiweiß', 'protein', 'kohlenhydrate', 'kalorien', 'zucker', 'proteine']

    nutrition_value = None

    for word in words:
        if word in nutrition_types:
            nutrition_value = word
            break

    if nutrition_value is None:
        return {'msg_speech': 'Es gab einen Fehler.',
                'msg_text': 'Es gab einen Fehler.'}

    item = None
    trigger = ['ist', 'sind', 'haben', 'hat']
    add_word = False
    add_word_index = None
    amount_type = None
    amount = None
    for i in range(0, len(words)):
        word = words[i]

        if add_word_index is not None and i == add_word_index:
            add_word = True

        if add_word:
            if word in number_words:
                continue

            if item is None:
                item = word
            else:
                item = item + " " + word
            continue

        if word in trigger:
            if 'gramm' in words:
                index = words.index('gramm')
                amount_type = 'gramm'
            elif 'kili' in words:
                index = words.index('kilo')
                amount_type = 'kilo'
            elif 'milliliter' in words:
                index = words.index('milliliter')
                amount_type = 'milliliter'
            elif 'liter' in words:
                index = words.index('liter')
                amount_type = 'liter'
            else:
                add_word = True
                continue

            amount = words[index - 1]
            add_word_index = index + 1

    answer = ""

    # Daten abfragen
    nutrition_data = get_nutrition_data(username, item, db)

    #print nutrition_data

    if nutrition_data is not None:
        if nutrition_data is not False:
            portionsize = nutrition_data['portionsize']

            if portionsize == 1:
                portionsize_string = "Ein"
            else:
                portionsize_string = str(portionsize)

            portion_string = portionsize_string + " " + nutrition_data['portionunit']

            name = nutrition_data['name']

            if (nutrition_value == "fett"):
                value = nutrition_data['fat']
                unit = "Gramm Fett"
            elif (nutrition_value in ['eiweiß', 'protein', 'proteine']):
                value = nutrition_data['protein']
                unit = "Gramm Eiweiß"
            elif (nutrition_value == "kohlenhydrate"):
                value = nutrition_data['carbs']
                unit = "Gramm Kohlenhydrate"
            elif (nutrition_value == "zucker"):
                value = nutrition_data['sugar']
                unit = "Gramm Zucker"
            elif (nutrition_value == "kalorien"):
                value = nutrition_data['calories']
                unit = "Kalorien"

            have_verb = "hat"

            if (portionsize > 1):
                have_verb = "haben"

            answer = portion_string + " " + name + " " + have_verb + " " + str(value) + " " + unit + "."

            context_data = {'nutrition_type': nutrition_value}
            # set_context(username, 'nutrition', context_data, db)
        else:
            answer = "Es wurden keine Lebensmittel zum Suchbegriff "+item+" gefunden."

    else:
        #fehlermeldung ausgeben

        answer = "Die Nährwertdaten konnten nicht abgefragt werden."

    amount_text = ''
    if amount_type is not None and amount is not None:
        amount_text = ' => ' + amount + ' ' + amount_type

    return {'msg_speech': answer, 'msg_text': answer}

def voice_query_nutrition_diary(username, text, context, db):
    words = text.split(" ")

    queried_value = None

    for word in words:
        if word == 'fett':
            queried_value = 'FAT'
        elif word == 'kalorien':
            queried_value = 'CALORIES'
        elif word == 'kohlenhydrate':
            queried_value = 'CARBS'
        elif word == 'zucker':
            queried_value = 'SUGAR'
        elif word in ['protein', 'proteine', 'eiweiß']:
            queried_value = 'PROTEIN'
        else:
            continue

        break

    user_profile = get_user_fitness_profile(username, db)

    print user_profile

    if (user_profile is False):
        answer = "Du hast noch kein Profil für den Ernährungsmanager erstellt. Das kannst du in der App im Menüpunkt Ernährungsmanager tun."
    elif queried_value is None:
        #Kein Wert gefunden
        answer = "Welchen Nährwert möchtest du abfragen?"

        answer_data = [
            ['Welcher Nährwert soll abgefragt werden.'],
            ['Welchen Nährwert ', ['magst', 'möchtest', 'willst'],' du abfragen.'],
        ]
    else:
        with db:
            cur = db.cursor()
            cur.execute("SELECT * FROM NUTRITION_DATA WHERE USER = :user AND DATE = :date",
                        {'user': username, 'date': datetime.datetime.today().strftime("%d.%m.%Y")})

            eaten_queried_value_today = 0

            for item in cur.fetchall():
                amount = (float(item['EATEN_PORTION_SIZE']) / float(item['PORTIONSIZE']))

                eaten_queried_value_today += item[queried_value] * amount

            unit = None

            if queried_value == 'FAT':
                value_left = user_profile['fatgoal']-eaten_queried_value_today
                unit = "Gramm Fett"
            elif queried_value == 'CALORIES':
                value_left = int(user_profile['caloriesgoal']-eaten_queried_value_today)
                eaten_queried_value_today = int(eaten_queried_value_today)
                unit = 'Kalorien'
            elif queried_value == 'CARBS':
                value_left = user_profile['carbsgoal']-eaten_queried_value_today
                unit = 'Gramm Kohlenhydrate'
            elif queried_value == 'SUGAR':
                value_left = user_profile['sugargoal']-eaten_queried_value_today
                unit = 'Gramm Zucker'
            elif queried_value == 'PROTEIN':
                value_left = user_profile['proteingoal']-eaten_queried_value_today
                unit = 'Gramm Protein'

            answer_data = [
                ['Du hast heute ', ['schon', 'bereits'], ' ', str(eaten_queried_value_today), " ", unit, ' ',
                 ['gegessen', 'verzehrt', 'aufgenommen', 'zu dir genommen'], ' und ', ['noch', 'weitere'], ' ',
                 str(value_left), ' ', unit, ' ', ['übrig', 'frei', 'offen'], '.']
            ]

            #answer = "Du hast heute schon "+str(eaten_queried_value_today)+" "+unit+" zu dir genommen und noch "+str(value_left)+" "+unit+" übrig."

    answer = generate_string(answer_data)

    return {'msg_speech': answer, 'msg_text': answer}