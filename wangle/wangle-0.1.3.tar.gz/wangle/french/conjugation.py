import re

class Conjugator:
    def calculate_lemma_model(self, lemma):
        if lemma == 'être':
            return 'être'
        elif lemma == 'avoir':
            return 'avoir'
        elif lemma == 'aller':
            return 'aller'
        elif lemma.endswith('er'):
            appeler_exceptions = ['agneler', 'celer', 'ciseler', 'congeler', 'déceler', 'décongeler', 'dégeler', 'démanteler', 'écarteler', 'geler', 'harceler', 'marteler', 'modeler', 'peler', 'receler', 'regeler', 'remodeler', 'surgeler']
            jeter_exceptions = ['acheter', 'bégueter', 'caqueter', 'corseter', 'crocheter', 'duveter', 'fileter', 'fureter', 'haleter', 'racheter']
            peser_regex = re.compile('.+e[nsv]er$')
            céder_regex = re.compile('.+é(gl|tr|[dlrt])er$')
            if lemma.endswith('guer'):
                return 'fatiguer'
            elif lemma.endswith('quer'):
                return 'fabriquer'
            elif lemma.endswith('ier'):
                return 'prier'
            elif lemma.endswith('cer') and not lemma.endswith('écer') and not lemma.endswith('ecer'):
                return 'lancer'
            elif lemma.endswith('ger') and not lemma.endswith('éger'):
                return 'manger'
            elif lemma.endswith('eler') and lemma not in appeler_exceptions:
                return 'appeler'
            elif lemma.endswith('eter') and lemma not in jeter_exceptions:
                return 'jeter'
            elif peser_regex.match(lemma) is not None or lemma in appeler_exceptions or lemma in jeter_exceptions:
                return 'peser'
            elif céder_regex.match(lemma) is not None:
                return 'céder'
            elif lemma in ['dépecer', 'clamecer']:
                return 'dépecer'
            elif lemma == 'rapiécer':
                return 'rapiécer'
            elif lemma.endswith('éger'):
                return 'protéger'
            elif (lemma.endswith('oyer') and lemma not in ['envoyer', 'renvoyer']) or lemma.endswith('uyer'):
                return 'employer'
            elif lemma.endswith('ayer'):
                return 'payer'
            elif lemma in ['envoyer', 'renvoyer']:
                return 'envoyer'
            else:
                return 'parler'
        elif lemma.endswith('oir'):
            if lemma in ['voir', 'entrevoir', 'revoir']:
                return 'voir'
            elif lemma == 'prévoir':
                return 'prévoir'
            elif lemma == 'pourvoir':
                return 'pourvoir'
            elif lemma in ['devoir', 'redevoir']:
                return 'devoir'
            elif lemma.endswith('cevoir'):
                return 'recevoir'
            elif lemma == 'mouvoir':
                return 'mouvoir'
            elif lemma in ['promouvoir', 'émouvoir']:
                return 'promouvoir'
            elif lemma in ['pleuvoir', 'repleuvoir']:
                return 'pleuvoir'
            elif lemma in ['valoir', 'équivaloir', 'revaloir']:
                return 'valoir'
            elif lemma == 'prévaloir':
                return 'prévaloir'
            elif lemma == 'falloir':
                return 'falloir'
            elif lemma == 'pouvoir':
                return 'pouvoir'
            elif lemma == 'savoir':
                return 'savoir'
            elif lemma in ['vouloir', 'revouloir']:
                return 'vouloir'
            elif lemma in ['asseoir', 'rasseoir']:
                return 'asseoir'
            elif lemma == 'surseoir':
                return 'surseoir'
        elif lemma.endswith('ir') or lemma.endswith('ïr'):
            if lemma == 'haïr':
                return 'haïr'
            elif lemma.endswith('ouvrir') or lemma in ['offrir', 'souffrir']:
                return 'couvrir'
            elif lemma in ['assaillir', 'défaillir', 'saillir', 'tressaillir']:
                return 'assaillir'
            elif lemma in ['cueillir', 'accueillir', 'recueillir']:
                return 'cueillir'
            elif lemma == 'bouillir':
                return 'bouillir'
            elif lemma in ['partir', 'départir', 'repartir', 'sortir', 'ressortir', 'servir', 'desservir', 'resservir', 'dormir', 'endormir', 'rendormir'] or (lemma.endswith('entir') and lemma not in ['ralentir', 'ratentir']):
                return 'partir'
            elif lemma in ['fuir', 'enfuir']:
                return 'fuir'
            elif lemma.endswith('quérir'):
                return 'acquérir'
            elif lemma.endswith('courir'):
                return 'courir'
            elif lemma == 'mourir':
                return 'mourir'
            elif lemma in ['vêtir', 'dévêtir', 'revêtir']:
                return 'vêtir'
            elif lemma.endswith('venir') or lemma.endswith('tenir'):
                return 'venir'
            else:
                return 'finir'
        elif lemma.endswith('re'):
            if lemma == 'maudire':
                return 'maudire'
            elif (lemma.endswith('endre') and not lemma.endswith('prendre')) or lemma.endswith('ondre') or lemma in ['répandre', 'épandre', 'perdre', 'reperdre'] or lemma.endswith('ordre'):
                return 'rendre'
            elif lemma in ['rompre', 'corrompre', 'interrompre']:
                return 'rompre'
            elif lemma.endswith('prendre'):
                return 'prendre'
            elif lemma.endswith('battre'):
                return 'battre'
            elif lemma.endswith('mettre'):
                return 'mettre'
            elif lemma in ['suivre', 'poursuivre', 'ensuivre']:
                return 'suivre'
            elif lemma in ['vivre', 'revivre', 'survivre']:
                return 'vivre'
            elif lemma.endswith('écrire') or lemma.endswith('scrire'):
                return 'écrire'
            elif lemma in ['dire', 'redire']:
                return 'dire'
            elif lemma in ['prédire', 'dédire', 'interdire', 'médire']:
                return 'prédire'
            elif lemma == 'suffire':
                return 'suffire'
            elif lemma == 'circoncire':
                return 'circoncire'
            elif lemma.endswith('duire') or lemma.endswith('truire') or lemma.endswith('cuire'):
                return 'conduire'
            elif lemma.endswith('nuire') or lemma.endswith('luire'):
                return 'nuire'
            elif lemma in ['lire', 'élire', 'réelire', 'relire']:
                return 'lire'
            elif lemma in ['rire', 'sourire']:
                return 'rire'
            elif lemma.endswith('aindre') or lemma.endswith('eindre') or lemma.endswith('oindre'):
                return 'plaindre'
            elif lemma in ['absoudre', 'dissoudre']:
                return 'absoudre'
            elif lemma == 'résoudre':
                return 'résoudre'
            elif lemma in ['coudre', 'découdre', 'recoudre']:
                return 'coudre'
            elif lemma == 'moudre':
                return 'moudre'
            elif lemma in ['exclure', 'conclure']:
                return 'exclure'
            elif lemma in ['inclure', 'occlure']:
                return 'inclure'
            elif lemma == 'boire':
                return 'boire'
            elif lemma == 'croire':
                return 'croire'
            elif lemma == 'croître':
                return 'croître'
            elif lemma in ['accroître', 'décroître']:
                return 'accroître'
            elif lemma.endswith('aître') and lemma not in ['naître', 'renaître']:
                return 'connaître'
            elif lemma in ['naître', 'renaître']:
                return 'naître'
            elif lemma in ['plaire', 'complaire', 'déplaire']:
                return 'plaire'
            elif lemma == 'taire':
                return 'taire'
            elif lemma.endswith('faire'):
                return 'faire'
            elif lemma.endswith('raire'):
                return 'traire'
            elif lemma in ['vaincre', 'convaincre']:
                return 'vaincre'

    def calculate_conjugation_group(self, model):
        if model.endswith('er') and model != 'aller':
            return 1
        elif model == 'finir' or model == 'haïr':
            return 2
        else:
            return 3

    def calculate_infinitive_stem(self, lemma):
        if lemma.endswith('oir'):
            return lemma[:-3]
        elif lemma.endswith('er') or lemma.endswith('ir') or lemma.endswith('ïr') or lemma.endswith('re'): 
            return lemma[:-2]

    def calculate_présent_stem(self, lemma, model, subject_group):
        stem = self.calculate_infinitive_stem(lemma)
        
        if stem is None:
            return None

        if model in ['employer', 'envoyer']:
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                stem = stem[:-1] + 'i'
        elif model == 'finir' or model == 'haïr':
            if subject_group in ['S1', 'S2', 'S3']:
                stem += 'i'
            elif model == 'haïr':
                stem += 'ïss'
            else:
                stem += 'iss'
        elif model == 'maudire' and subject_group in ['P1', 'P2', 'P3']:
            # despite being a group 3 verb, maudire conjugates like finir
            stem += 'ss'
        elif model == 'bouillir' and subject_group in ['S1', 'S2', 'S3']:
            # single conjugations lose the 'ill' at the end of the stem
            stem = stem[:-3] 
        elif model in ['voir', 'prévoir', 'pourvoir']:
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                stem += 'oi'
            else:
                stem += 'oy'
        elif model in ['devoir', 'recevoir']:
            if subject_group in ['S1', 'S2', 'S3']:
                # ev -> oi
                stem = stem[:-2] + 'oi'
            elif subject_group == 'P3':
                # ev -> oiv
                stem = stem[:-2] + 'oiv'
        elif model in ['mouvoir', 'promouvoir', 'pleuvoir', 'pouvoir', 'vouloir']:
            if subject_group in ['S1', 'S2', 'S3']:
                stem = stem[:-1]
                if stem.endswith('ou'):
                    # ou -> eu
                    stem = stem[:-2] + 'eu'
            elif subject_group == 'P3':
                # replace ou one letter in from the end if it is there
                # eg mouv -> meuv
                if stem[-3:-1] == 'ou':
                    stem = stem[:-3] + 'eu' + stem[-1]
        elif model in ['valoir', 'prévaloir', 'falloir']:
            if subject_group in ['S1', 'S2', 'S3']:
                if stem.endswith('all'):
                    # all -> au
                    stem = stem[:-3] + 'au'
                elif stem.endswith('al'):
                    # al -> au
                    stem = stem[:-2] + 'au'
        elif model in ['savoir']:
            if subject_group in ['S1', 'S2', 'S3']:
                # v -> i
                stem = stem[:-1] + 'i'
        elif model in ['asseoir']:
            if subject_group in ['S1', 'S2', 'S3']:
                # e -> ied
                stem = stem[:-1] + 'ied'
            else:
                stem += 'y'
        elif model in ['surseoir']:
            #TODO: 'asseoir' can also conjugate like this, how do we deal with multiple valid conjugations
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                # e -> oi
                stem = stem[:-1] + 'oi'
            else:
                # e -> oy
                stem = stem[:-1] + 'oy'
        elif model in ['croire', 'traire']:
            if subject_group in ['P1', 'P2']:
                # i -> y
                stem = stem[:-1] + 'y'
        elif model in ['battre', 'mettre']:
            if subject_group in ['S1', 'S2', 'S3']:
                # remove a 't'
                stem = stem[:-1]
        elif model in ['suivre', 'vivre']:
            if subject_group in ['S1', 'S2', 'S3']:
                # remove a 'v'
                stem = stem[:-1]
        elif model == 'écrire':
            if subject_group in ['P1', 'P2', 'P3']:
                # remove a 'v'
                stem = stem + 'v'
        elif model == 'plaindre':
            if subject_group in ['S1', 'S2', 'S3']:
                # remove a 'd'
                stem = stem[:-1]
            else:
                # nd -> gn
                stem = stem[:-2] + 'gn'
        elif model in ['absoudre', 'résoudre']:
            if subject_group in ['S1', 'S2', 'S3']:
                # remove a 'd'
                stem = stem[:-1]
            else:
                # ud -> lv
                stem = stem[:-2] + 'lv'
        elif model == 'coudre':
            if subject_group in ['P1', 'P2', 'P3']:
                # d -> s
                stem = stem[:-1] + 's'
        elif model == 'moudre':
            if subject_group in ['P1', 'P2', 'P3']:
                # d -> l
                stem = stem[:-1] + 'l'
        elif model in ['dire', 'prédire', 'suffire', 'circoncire', 'conduire', 'nuire', 'lire']:
            if subject_group in ['P1', 'P2', 'P3']:
                # add an 's'
                stem += 's'
        elif model in ['plaire', 'taire', 'faire']:
            if subject_group in ['P1', 'P2', 'P3']:
                # add an 's'
                stem += 's'
            elif model == 'plaire' and subject_group == 'S3':
                # i => î
                stem = stem[:-1] + 'î'
        elif model in ['croître', 'accroître', 'connaître', 'naître']:
            if subject_group in ['S1', 'S2']:
                if model == 'croître':
                    # remove the 't'
                    stem = stem[:-1]
                else:
                    # ît -> i
                    stem = stem[:-2] + 'i'
            elif subject_group == 'S3':
                # remove the 't'
                stem = stem[:-1]
            else:
                # ît -> iss
                stem = stem[:-2] + 'iss'
        elif model == 'vaincre':
            if subject_group in ['P1', 'P2', 'P3']:
                # c -> qu
                stem = stem[:-1] + 'qu'
        elif model == 'prendre':
            if subject_group in ['P1', 'P2']:
                # remove the d
                stem = stem[:-1]
            elif subject_group == 'P3':
                # d -> n
                stem = stem[:-1] + 'n'
        elif model == 'boire':
            if subject_group in ['P1', 'P2']:
                # oi -> uv
                stem = stem[:-2] + 'uv'
            elif subject_group == 'P3':
                # add a 'v'
                stem += 'v'
        elif model == 'partir':
            if subject_group in ['S1', 'S2', 'S3']:
                # remove last consonant
                stem = stem[:-1]
        elif model == 'fuir':
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                # add 'i'
                stem += 'i'
            else:
                # add 'y'
                stem += 'y'
        elif model == 'mourir':
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                # our -> eur
                stem = stem[:-3] + 'eur'
        elif model == 'venir':
            if subject_group in ['S1', 'S2', 'S3']:
                # en -> ien 
                stem = stem[:-2] + 'ien'
            elif subject_group == 'P3':
                # en -> ienn 
                stem = stem[:-2] + 'ienn'
        elif model == 'acquérir':
            if subject_group in ['S1', 'S2', 'S3']:
                # ér -> er 
                stem = stem[:-2] + 'ier'
            elif subject_group == 'P3':
                # ér -> iér 
                stem = stem[:-2] + 'ièr'

        return stem

    def calculate_présent_suffix(self, model, subject_group, stem):
        suffix = ''

        conjugation_group = self.calculate_conjugation_group(model)

        if conjugation_group == 1 or model in ['couvrir', 'assaillir', 'cueillir']:
            if subject_group == 'S1':
                suffix = 'e'
            elif subject_group == 'S2':
                suffix = 'es'
            elif subject_group == 'S3':
                suffix = 'e'
        else:
            if subject_group == 'S1':
                suffix = 's'
            elif subject_group == 'S2':
                suffix = 's'
            elif subject_group == 'S3':
                suffix = 't'

        if subject_group == 'P1':
            suffix = 'ons'
        elif subject_group == 'P2':
            suffix = 'ez'
        elif subject_group == 'P3':
            suffix = 'ent'
            
        # EXCEPTIONS
        # vouloir is a weird exception
        if model in ['vouloir', 'valoir', 'prévaloir', 'pouvoir'] and subject_group in ['S1', 'S2']:
           suffix = 'x'

        # don't add 't' if stem ends in 'c', 'd', or 't'
        if suffix == 't' and stem[-1] in ['c', 'd', 't']:
            suffix = ''
        return suffix

    def calculate_présent(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        if model == 'être':
            if subject_group == 'S1':
                return 'suis'
            elif subject_group == 'S2':
                return 'es'
            elif subject_group == 'S3':
                return 'est'
            if subject_group == 'P1':
                return 'sommes'
            elif subject_group == 'P2':
                return 'êtes'
            elif subject_group == 'P3':
                return 'sont'
        elif model == 'avoir':
            if subject_group == 'S1':
                return 'ai'
            elif subject_group == 'S2':
                return 'as'
            elif subject_group == 'S3':
                return 'a'
            elif subject_group == 'P3':
                return 'ont'
        elif model == 'aller':
            if subject_group == 'S1':
                return 'vais'
            elif subject_group == 'S2':
                return 'vas'
            elif subject_group == 'S3':
                return 'va'
            elif subject_group == 'P3':
                return 'vont'
        elif model == 'faire':
            if subject_group == 'P2':
                return 'faites'
            elif subject_group == 'P3':
                return 'font'
        elif model == 'dire':
            if subject_group == 'P2':
                # -dire -> -dites
                return lemma[:-2] + 'tes'

        stem = self.calculate_présent_stem(lemma, model, subject_group)
        if stem is None:
            return None

        suffix = self.calculate_présent_suffix(model, subject_group, stem)
        if suffix is None:
            return None

        # apply consonant doubling if required
        if model in ['appeler', 'jeter'] and suffix in ['e', 'es', 'ent']:
            stem += stem[-1]

        # do e -> è replacement if required
        if model in ['peser', 'dépecer'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('e')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        # do é -> è replacement if required
        if model in ['céder', 'rapiécer', 'protéger'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('é')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        result = stem + suffix

        # do c -> ç replacement if required
        if model in ['lancer', 'dépecer', 'rapiécer', 'recevoir']:
            index = result.rfind('c')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'o', 'u']:
                result = result[:index] + 'ç' + result[index + 1:]

        # do g -> ge replacement if required
        if model in ['manger', 'protéger']:
            index = result.rfind('g')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'o']:
                result = result[:index] + 'ge' + result[index + 1:]

        return result

    def calculate_past_participle_stem(self, lemma, model):
        stem = self.calculate_infinitive_stem(lemma)

        if model == 'couvrir':
            # r -> er
            stem = stem[:-1] + 'er'
        elif model in ['devoir', 'recevoir']:
            # remove 'ev'
            stem = stem[:-2]
        elif model == 'savoir':
            # remove 'av'
            stem = stem[:-2]
        elif model in ['mouvoir', 'promouvoir', 'pleuvoir', 'pouvoir']:
            # remove 'ouv' or 'euv'
            stem = stem[:-3]
        elif model in ['asseoir', 'surseoir']:
            # remove 'e'
            stem = stem[:-1]
        elif model == 'prendre':
            # remove 'end'
            stem = stem[:-3]
        elif model == 'mettre':
            # remove 'ett'
            stem = stem[:-3]
        elif model == 'vivre':
            # iv -> éc
            stem = stem[:-2] + 'éc'
        elif model == 'plaindre':
            # remove 'd'
            stem = stem[:-1]
        elif model in ['boire', 'croire']:
            # remove 'oi'
            stem = stem[:-2]
        elif model in ['maudire', 'conduire', 'dire', 'prédire', 'écrire', 'faire', 'traire', ]:
            # remove 'i'
            stem = stem[:-1]
        elif model in ['exclure', 'inclure']:
            # remove 'u'
            stem = stem[:-1]
        elif model == 'couvrir':
            # remove 'r'
            stem = stem[:-1]
        elif model in ['croître', 'accroître']:
            # remove 'oît'
            stem = stem[:-3]
        elif model in ['connaître', 'naître']:
            # remove 'aît'
            stem = stem[:-3]
        elif model in ['plaire', 'taire']:
            # remove 'aî'
            stem = stem[:-2]
        elif model in ['ecrire', 'nuire', 'lire', 'rire', 'suffire', 'circoncire']:
            # remove 'i'
            stem = stem[:-1]
        elif model == 'absoudre':
            # remove 'd'
            stem = stem[:-1]
        elif model == 'résoudre':
            # ud -> l
            stem = stem[:-2] + 'l'
        elif model == 'coudre':
            # d -> s
            stem = stem[:-1] + 's'
        elif model == 'moudre':
            # d -> l
            stem = stem[:-1] + 'l'
        elif model == 'acquérir':
            # remove 'ér'
            stem = stem[:-2]
        elif model == 'mourir':
            # our -> or
            stem = stem[:-3] + 'or'
        elif model == 'être':
            stem = 'ét'
        elif model == 'avoir':
            stem = 'e'

        return stem

    def calculate_past_participle_suffix(self, model, masculine):
        conjugation_group = self.calculate_conjugation_group(model)

        suffix = None

        if conjugation_group == 1 or model in ['naître', 'être', 'aller']:
            suffix = 'é'
        elif model in ['finir', 'assaillir', 'cueillir', 'bouillir', 'nuire', 'suivre', 'rire', 'suffire', 'partir', 'fuir']:
            suffix = 'i'
        elif model == 'haïr':
            suffix = 'ï'
        elif model in ['asseoir', 'surseoir', 'prendre', 'mettre', 'circoncire', 'acquérir']:
            suffix = 'is'
        elif model in ['couvrir', 'plaindre', 'mourir']:
            suffix = 't'
        elif model in ['maudire', 'conduire', 'dire', 'prédire', 'écrire', 'faire', 'traire']:
            suffix = 'it'
        elif model in ['voir', 'prévoir', 'pourvoir', 'récevoir', 'promouvoir', 'pleuvoir', 'recevoir', 'valoir', 'prévaloir', 'falloir', 'pouvoir', 'savoir', 'vouloir', 'avoir', 'rendre', 'rompre', 'battre', 'vivre', 'lire', 'exclure', 'boire', 'croire', 'accroître', 'connaître', 'plaire', 'taire', 'coudre', 'moudre', 'résoudre', 'vaincre', 'courir', 'vêtir', 'venir']:
            suffix = 'u'
        elif model in ['devoir', 'mouvoir', 'croître']:
            suffix = 'û'
        elif model == 'inclure':
            suffix = 'us'
        elif model == 'absoudre':
            if masculine:
                suffix = 's'
            else:
                suffix = 't'

        return suffix

    def calculate_past_participle(self, lemma, masculine, plural):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_past_participle_stem(lemma, model);
        if stem is None:
            return None
        
        suffix = self.calculate_past_participle_suffix(model, masculine);
        if suffix is None:
            return None

        if stem.endswith('d') and suffix == 't':
            # drop last 'd' to avoid 'dt'
            stem = stem[:-1]

        if stem.endswith('i') and suffix == 'i':
            # drop last 'i' to avoid duplicated letter
            stem = stem[:-1]

        if stem.endswith('u') and suffix == 'u':
            # drop last 'u' to avoid duplicated letter
            stem = stem[:-1]

        if stem.endswith('ec') and suffix == 'u':
            # c -> ç
            stem = stem[:-1] + 'ç'

        result = stem + suffix

        # some past participles do not decline
        if model in ['suffire', 'nuire', 'rire', 'plaire', 'taire', 'pouvoir', 'être']:
            return result

        if model in ['devoir', 'mouvoir', 'croître'] and (plural or not masculine):
            # these past participles lose the circumflex on their 'u' when declining
            # û -> u
            result = result[:-1] + 'u'

        # perform past participle declension
        if not masculine:
            result += 'e'

        if plural and not result.endswith('s'):
            result += 's'
        
        return result

    def calculate_imparfait_stem(self, lemma, model): 
        if lemma == 'être':
            return 'ét'

        return self.calculate_présent_stem(lemma, model, 'P1')

    def calculate_imparfait_suffix(self, subject_group):
        suffix = ''

        if subject_group == 'S1':
            suffix = 'ais'
        elif subject_group == 'S2':
            suffix = 'ais'
        elif subject_group == 'S3':
            suffix = 'ait'
        elif subject_group == 'P1':
            suffix = 'ions'
        elif subject_group == 'P2':
            suffix = 'iez'
        elif subject_group == 'P3':
            suffix = 'aient'

        return suffix

    def calculate_imparfait(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_imparfait_stem(lemma, model)
        if stem is None:
            return None

        suffix = self.calculate_imparfait_suffix(subject_group)
        if suffix is None:
            return None

        result = stem + suffix

        # do c -> ç replacement if required
        if model in ['lancer', 'dépecer', 'rapiécer', 'recevoir']:
            index = result.rfind('c')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'o', 'u']:
                result = result[:index] + 'ç' + result[index + 1:]

        # do g -> ge replacement if required
        if model in ['manger', 'protéger']:
            index = result.rfind('g')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'o']:
                result = result[:index] + 'ge' + result[index + 1:]

        return result

    def calculate_futur_stem(self, lemma, model): 
        stem = lemma

        if model in ['appeler', 'jeter']:
            stem = stem[:-2] + stem[-3] + 'er'
        elif model in ['peser', 'dépecer']:
            index = stem[:-2].rfind('e')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]
        elif model == 'employer':
            stem = stem[:-3] + 'ier'
        elif model == 'envoyer':
            stem = stem[:-4] + 'err'
        elif model == 'maudire':
            stem = stem[:-1]
        elif model == 'cueillir':
            stem = stem[:-2] + 'er'
        elif model == 'voir':
            stem = stem[:-3] + 'err'
        elif model in ['devoir', 'recevoir', 'mouvoir', 'premouvoir', 'promouvoir', 'pleuvoir']:
            stem = stem[:-3] + 'r'
        elif model in ['valoir', 'prévaloir']:
            stem = stem[:-5] + 'audr'
        elif model == 'falloir':
            stem = stem[:-6] + 'audr'
        elif model == 'pouvoir':
            stem = stem[:-6] + 'ourr'
        elif model in ['savoir', 'avoir']:
            stem = stem[:-5] + 'aur'
        elif model == 'vouloir':
            stem = stem[:-4] + 'dr'
        elif model == 'asseoir':
            stem = stem[:-4] + 'iér'
        elif model == 'faire':
            stem = stem[:-4] + 'er'
        elif model == 'acquérir':
            stem = stem[:-4] + 'érr'
        elif model in ['courir', 'mourir']:
            stem = stem[:-2] + 'r'
        elif model == 'venir':
            stem = stem[:-4] + 'iendr'
        elif model == 'être':
            stem = 'ser'
        elif model == 'aller':
            stem = 'ir'
        elif model.endswith('re'):
            stem = stem[:-1]

        return stem

    def calculate_futur_suffix(self, subject_group):
        suffix = ''

        if subject_group == 'S1':
            suffix = 'ai'
        elif subject_group == 'S2':
            suffix = 'as'
        elif subject_group == 'S3':
            suffix = 'a'
        elif subject_group == 'P1':
            suffix = 'ons'
        elif subject_group == 'P2':
            suffix = 'ez'
        elif subject_group == 'P3':
            suffix = 'ont'

        return suffix

    def calculate_futur(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_futur_stem(lemma, model)
        if stem is None:
            return None

        suffix = self.calculate_futur_suffix(subject_group)
        if suffix is None:
            return None

        # apply consonant doubling if required
        if model in ['appeler', 'jeter'] and suffix in ['e', 'es', 'ent']:
            stem += stem[-1]

        # do e -> è replacement if required
        if model in ['peser', 'dépecer'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('e')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        # do é -> è replacement if required
        if model in ['céder', 'rapiécer', 'protéger'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('é')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        result = stem + suffix

        return result

    def calculate_conditionnel_suffix(self, subject_group):
        suffix = ''

        if subject_group == 'S1':
            suffix = 'ais'
        elif subject_group == 'S2':
            suffix = 'ais'
        elif subject_group == 'S3':
            suffix = 'ait'
        elif subject_group == 'P1':
            suffix = 'ions'
        elif subject_group == 'P2':
            suffix = 'iez'
        elif subject_group == 'P3':
            suffix = 'aient'

        return suffix

    def calculate_conditionnel(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_futur_stem(lemma, model)
        if stem is None:
            return None

        suffix = self.calculate_conditionnel_suffix(subject_group)
        if suffix is None:
            return None

        result = stem + suffix

        return result

    def calculate_passé_simple_stem(self, lemma, model): 
        stem = ""
        if model == 'être':
            stem = lemma[:-4] + 'fu'
        elif model == 'naître':
            stem = lemma[:-4] + 'qui'
        elif model in ['couvrir', 'mourir']:
            stem = self.calculate_infinitive_stem(lemma)
            if model == 'couvrir':
                stem += 'i'
            else:
                stem += 'u'
        elif model == 'plaindre':
            stem = self.calculate_présent_stem(lemma, model, 'P1') + 'i'
        else:
            pp_stem = self.calculate_past_participle_stem(lemma, model)
            pp_suffix = self.calculate_past_participle_suffix(model, True)
            if lemma.endswith('er'):
                stem = pp_stem + 'a'
            elif pp_suffix in ['i', 'ï', 'is', 'it']:
                stem = pp_stem
                if model == 'faire':
                    stem = stem[:-1]
                elif model == 'conduire':
                    stem += 'is'
                elif model == 'écrire':
                    stem += 'iv'
                elif model == 'nuire':
                    stem += 'is'

                if pp_suffix == 'ï':
                    stem += 'ï'
                else:
                    stem += 'i'
            elif pp_suffix in ['u', 'û', 'us']:
                stem = pp_stem
                if model in ['voir', 'prévoir', 'rendre', 'rompre', 'battre', 'coudre', 'vaincre', 'vêtir']:
                    if model == 'vaincre':
                        # vaincre changes -c -> -qu
                        stem = stem[:-1] + 'qu'
                    stem += 'i'
                elif model == 'venir':
                    # venir/tenir changes -enu -> -in
                    stem = stem[:-2] + 'in'
                elif model == 'croître':
                    stem += 'û'
                else:
                    stem += 'u'

        return stem

    def calculate_passé_simple_suffix(self, subject_group, stem):
        suffix = ''

        if stem.endswith('a'):
            if subject_group == 'S1':
                suffix = 'i'
            elif subject_group == 'S2':
                suffix = 's'
            elif subject_group == 'S3':
                suffix = ''
        else:
            if subject_group == 'S1':
                suffix = 's'
            elif subject_group == 'S2':
                suffix = 's'
            elif subject_group == 'S3':
                suffix = 't'
        if subject_group == 'P1':
            suffix = '^mes'
        elif subject_group == 'P2':
            suffix = '^tes'
        elif subject_group == 'P3':
            suffix = 'rent'

        return suffix

    def calculate_passé_simple(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_passé_simple_stem(lemma, model)
        if stem is None:
            return None

        suffix = self.calculate_passé_simple_suffix(subject_group, stem)
        if suffix is None:
            return None

        result = None

        if suffix.startswith("^"):
            last_vowel = ''
            index = len(stem) - 1
            while 0 <= index < len(stem) and stem[index] not in 'aâeéèêhiîïoôu':
                index -= 1
            if 0 <= index < len(stem) and stem[index] in 'aiu':
                replacement = None
                if stem[index] == 'a':
                    replacement = 'â'
                elif stem[index] == 'i':
                    replacement = 'î'
                elif stem[index] == 'u':
                    replacement = 'û'
                result = stem[0:index] + replacement + stem[index + 1:] + suffix[1:]
            else:
                result = stem + suffix[1:]
        elif stem.endswith('a') and suffix == 'rent':
            result = stem[:-1] + 'è' + suffix
        else:
            result = stem + suffix

        # do c -> ç replacement if required
        if model in ['lancer', 'dépecer', 'rapiécer', 'recevoir']:
            index = result.rfind('c')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'â', 'u', 'û']:
                result = result[:index] + 'ç' + result[index + 1:]

        # do g -> ge replacement if required
        if model in ['manger', 'protéger']:
            index = result.rfind('g')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'â']:
                result = result[:index] + 'ge' + result[index + 1:]

        return result

    def calculate_subjonctif_présent_stem(self, lemma, model, subject_group):
        if lemma == 'être':
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                return 'soi'
            else:
                return 'soy'
        elif lemma == 'avoir':
            if subject_group in ['S1', 'S2', 'S3', 'P3']:
                return 'ai'
            else:
                return 'ay'
        elif lemma == 'savoir':
            return 'sach'
        elif lemma == 'pouvoir':
            return 'puiss'
        elif lemma == 'aller' and subject_group in ['S1', 'S2', 'S3', 'P3']:
            return 'aill'
        elif lemma == 'falloir':
            return 'faill'
        elif lemma == 'vouloir' and subject_group in ['S1', 'S2', 'S3', 'P3']:
            return 'veuill'
        elif model == 'faire':
            return lemma[:-3] + 'ss'
        elif model == 'valoir' and subject_group in ['S1', 'S2', 'S3', 'P3']:
            return lemma[:-4] + 'ill'
        elif subject_group in ['S1', 'S2', 'S3', 'P3']:
            return self.calculate_présent_stem(lemma, model, 'P3')
        else:
            return self.calculate_présent_stem(lemma, model, 'P1')

    def calculate_subjonctif_présent_suffix(self, model, subject_group):
        suffix = ''
        if model == 'être':
            if subject_group == 'S1':
                return 's'
            elif subject_group == 'S2':
                return 's'
            elif subject_group == 'S3':
                return 't'
            elif subject_group == 'P1':
                return 'ons'
            elif subject_group == 'P2':
                return 'ez'
        elif model == 'avoir':
            if subject_group == 'S3':
                return 't'
            elif subject_group == 'P1':
                return 'ons'
            elif subject_group == 'P2':
                return 'ez'

        if subject_group == 'S1':
            suffix = 'e'
        elif subject_group == 'S2':
            suffix = 'es'
        elif subject_group == 'S3':
            suffix = 'e'
        elif subject_group == 'P1':
            suffix = 'ions'
        elif subject_group == 'P2':
            suffix = 'iez'
        elif subject_group == 'P3':
            suffix = 'ent'

        return suffix

    def calculate_subjonctif_présent(self, lemma, subject_group):
        model = self.calculate_lemma_model(lemma)

        stem = self.calculate_subjonctif_présent_stem(lemma, model, subject_group)
        if stem is None:
            return None

        suffix = self.calculate_subjonctif_présent_suffix(model, subject_group)
        if suffix is None:
            return None

        # apply consonant doubling if required
        if model in ['appeler', 'jeter'] and suffix in ['e', 'es', 'ent']:
            stem += stem[-1]

        # do e -> è replacement if required
        if model in ['peser', 'dépecer'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('e')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        # do é -> è replacement if required
        if model in ['céder', 'rapiécer', 'protéger'] and suffix in ['e', 'es', 'ent']:
            index = stem.rfind('é')
            if 0 <= index < len(stem):
                stem = stem[:index] + 'è' + stem[index + 1:]

        result = stem + suffix

        # do c -> ç replacement if required
        if model in ['lancer', 'dépecer', 'rapiécer', 'recevoir']:
            index = result.rfind('c')
            if 0 <= index and index + 1 < len(result) and result[index + 1] in ['a', 'o', 'u']:
                result = result[:index] + 'ç' + result[index + 1:]


        return result

    def calculate_subj_group(self, sentence, verb):
        subject = None
        if verb.has_tag("agrees_with"):
            subject = sentence.words[verb.get_tag_value("agrees_with")]
            subj_group = None
            if subject.lemma == "je":
                subj_group = "S1"
            elif subject.lemma == "tu":
                subj_group = "S2"
            elif subject.lemma == "nous":
                subj_group = "P1"
            elif subject.lemma == "vous":
                subj_group = "P2"
            elif subject.has_tag("is_plural"):
                if subject.get_tag_value("is_plural"):
                    subj_group = "P3"
                else:
                    subj_group = "S3"
        return subj_group

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

    def conjugate(self, sentence, verb, save_parameters=True):
        if verb.has_tag("finite_verb"):
            subj_group = self.calculate_subj_group(sentence, verb)

            if subj_group is not None:
                verb.set_tag("conj_subj_group", value=subj_group)
                conj_mood = verb.get_tag_value("conj_mood")
                conj_tense = verb.get_tag_value("conj_tense")
                if conj_mood == "indicatif":
                    if conj_tense == "présent":
                        verb.inflection = self.calculate_présent(verb.lemma, subj_group)
                    elif conj_tense == "imparfait":
                        verb.inflection = self.calculate_imparfait(verb.lemma, subj_group)
                    elif conj_tense == "futur":
                        verb.inflection = self.calculate_futur(verb.lemma, subj_group)
                    elif conj_tense == "passé simple":
                        verb.inflection = self.calculate_passé_simple(verb.lemma, subj_group)
                elif conj_mood == "conditionnel":
                    if conj_tense == "présent":
                        verb.inflection = self.calculate_conditionnel(verb.lemma, subj_group)
                elif conj_mood == "subjonctif":
                    if conj_tense == "présent":
                        verb.inflection = self.calculate_subjonctif_présent(verb.lemma, subj_group)
        elif verb.has_tag("past_participle"):
            gender = self.word_gender(sentence, verb, save_parameters)
            is_plural = self.word_is_plural(sentence, verb, save_parameters)
            verb.inflection = self.calculate_past_participle(verb.lemma, gender == "masc", is_plural)
