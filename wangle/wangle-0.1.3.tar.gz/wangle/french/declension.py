
class Decliner:
    def calculate_declension(self, lemma, masculine, plural):
        result = lemma
        if not self.is_invariable(lemma):
            if not masculine:
                result = self.feminize(result)
            if plural:
                result = self.pluralize(result)
        return result

    def is_invariable(self, word):
        # colours
        if word in ['abricot','amarante', 'améthyste', 'bistre', 'cerise', 'chocolat', 'citron', 'corail', 'ivoire', 'lilas', 'mandarine', 'marron', 'moutarde', 'noisette', 'orange', 'paille', 'prune']:
            return True
        return word in ['arrière', 'avant', 'bien', 'cool', 'in', 'mal', 'nord', 'relax', 'sexy', 'soi-disant', 'super', 'vidéo']

    def feminize(self, word):
        exceptions = {
            'blanc': 'blanche',
            'clos': 'close',
            'doux': 'douce',
            'épais': 'épaisse',
            'favori': 'favorite',
            'fou': 'folle',
            'frais': 'fraîche',
            'franc': 'franche',
            'gentil': 'gentille',
            'grec': 'grecque',
            'inquiet': 'inquiète',
            'majeur': 'majeure',
            'mou': 'molle',
            'public': 'publique',
            'roux': 'rousse',
            'ras': 'rase',
            'sec': 'sèche',
            'turc': 'turque',
            'vieux': 'vieille',
        }
        
        #normal rules
        if word in exceptions:
            return exceptions[word]
        elif word.endswith('eilleur'):
            return word + 'e'
        elif word.endswith('érieur'):
            return word + 'e'
        if word.endswith('aître'):
            return word + 'sse'
        elif word.endswith('long'):
            return word + 'ue'
        elif word.endswith('teur'):
            return word[:-4] + 'trice'
        elif word.endswith('cret') or word.endswith('plet'):
            return word[:-2] + 'ète'
        elif word.endswith('eil'):
            return word[:-3] + 'eille'
        elif word.endswith('oul') or word.endswith('oûl') or word.endswith('eul'):
            return word + 'e'
        elif word.endswith('aux'):
            return word[:-3] + 'ausse'
        elif word.endswith('eur'):
            return word[:-3] + 'euse'
        elif word.endswith('eau'):
            return word[:-3] + 'elle'
        elif word.endswith('as'):
            return word[:-2] + 'asse'
        elif word.endswith('ay'):
            return word
        elif word.endswith('ef'):
            return word[:-2] + 'ève'
        elif word.endswith('el'):
            return word[:-2] + 'elle'
        elif word.endswith('en'):
            return word[:-2] + 'enne'
        elif word.endswith('er'):
            return word[:-2] + 'ère'
        elif word.endswith('ès'):
            return word[:-2] + 'esse'
        elif word.endswith('et'):
            return word[:-2] + 'ette'
        elif word.endswith('ic'):
            return word
        elif word.endswith('on'):
            return word[:-2] + 'onne'
        elif word.endswith('os'):
            return word[:-2] + 'osse'
        elif word.endswith('ul'):
            return word[:-2] + 'ulle'
        elif word.endswith('e') or word.endswith('a'):
            return word
        elif word.endswith('f'):
            return word[:-1] + 've'
        elif word.endswith('û'):
            return word[:-1] + 'ue'
        elif word.endswith('um'):
            return word
        elif word.endswith('x'):
            return word[:-1] + 'se'
        else:
            return word + 'e'

    def pluralize(self, word):
        exceptions = {
            'banal': 'banals',
            'fatal': 'fatals',
        }
        
        #normal rules
        if word in exceptions:
            return exceptions[word]
        elif word[-1] in ['s', 'z', 'x']:
            return word
        elif word.endswith('al'):
            return word[:-2] + 'aux'
        elif word.endswith('au'):
            return word + 'x'
        elif word.endswith('û'):
            return word[:-1] + 'us'
        else:
            return word + 's'

    def word_gender(self, sentence, word, save_parameters=True):
        if word.has_tag("gender"):
            return word.get_tag_value("gender")

        if word.has_tag("agrees_with"):
            agrees_with = sentence.words[word.get_tag_value("agrees_with")]
            return self.word_gender(sentence, agrees_with, save_parameters)

        return "masc"

    def word_is_plural(self, sentence, word, save_parameters=True):
        if word.has_tag("is_plural"):
            return word.get_tag_value("is_plural")

        if word.has_tag("agrees_with"):
            agrees_with = sentence.words[word.get_tag_value("agrees_with")]
            return self.word_is_plural(sentence, agrees_with, save_parameters)

        return False

    def decline(self, sentence, word, save_parameters=True):
        gender = self.word_gender(sentence, word, save_parameters)
        is_plural = self.word_is_plural(sentence, word, save_parameters)
        word.inflection = self.calculate_declension(word.lemma, gender == "masc", is_plural)
