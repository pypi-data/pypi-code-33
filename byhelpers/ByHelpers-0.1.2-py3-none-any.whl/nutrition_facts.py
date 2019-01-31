#-*- coding: utf-8-*-

import unicodedata
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re


NUTRIMENTS = [
    {
        "key": "calories",
        "match": ["calories", "calorias", "calorie", "caloria", "calory", "kilocalories", "ener", "energy", "energia", 'kcal'],
        "name": "Calories",
        "name_es": "Calorias"
    },
    {
        "name": "Polyunsaturated Fat",
        "name_es": "Grasas Poliinsaturadas",
        "key": "poly_fat",
        "match": ["fapucis", "polyunsaturated fat", "grasas poliinsaturadas", "grasa poliinsaturada"]
    },
    {
        "name": "Monounsaturated Fat",
        "name_es": "Grasas Monoinsaturadas",
        "key": "mono_fat",
        "match": ["famscis", "monounsaturated fat", "grasas monoinsaturadas", "grasa monoinsaturada"]
    },
    {
        "name": "Trans Fat",
        "name_es": "Grasas Trans",
        "key": "trans_fat",
        "match": ["grasas trans", "trans fat", "acidos grasos trans", "trans fatty acids"]
    },
    {
        "name": "Total Fat",
        "name_es": "Grasas Totales",
        "key": "fat",
        "match": ["fat", "grasa", "grasas", "acidos grasos", "grasa total", "total fat"],
    },
    {

        "key": "niacin",
        "match": ["nia", "niacin", "niacina"],
        "name": "Niacin",
        "name_es": "Niacina"
    },
    {
        "name": "Docosahexaenoic Acid",
        "name_es": "Ácido Docosahexaenoico",
        "key": "dha",
        "match": ["docosahexaenoic", "docosahexaenoico", "dha"]
    },
    {
        "name": "Riboflavin",
        "name_es": "Riboflavina",
        "key": "riboflavin",
        "match": ["riboflavin", "riboflavina", "ribf"]
    },
    {
        "name": "Potassium",
        "name_es": "Potasio",
        "key": "k",
        "match": ["potassium", "potasio", "k"]
    },
    {
        "name": "Vitamin E",
        "name_es": "Vitamina E",
        "key": "vite",
        "match": ["vitamin e", 'vitamina e'],
    },
    {
        "name": "Iodized Salt",
        "name_es": "Yodo",
        "key": "iodine",
        "match": ["iodized_salt", "yodo", 'sal iodada']
    },
    {
        "name": "Carnitine",
        "name_es": "Carnitina",
        "key": "carnitine",
        "match": ["carnitine", "l carnitine", "carnitina"]
    },
    {
        "name": "Thiamin",
        "name_es": "Tiamina",
        "key": "tiamin",
        "match": ["thia", "thiamin", "thiamine","tiamina", "vitb1", "vitamina b1", "vitamine b1"]
    },
    {
        "name": "Saccharose",
        "name_es": "Sacarosa",
        "key": "saccharose",
        "match": ["saccharose", "sacarosa"]
    },
    {
        "name": "Vitamin C",
        "name_es": "Vitamina C",
        "key": "vitc",
        "match": ["vitamina c", "vitamin c"],
    },
    {
        "name": "Erythritol",
        "name_es": "Eritritol",
        "key": "eritritol",
        "match": ["eritritol", "erythritol"]
    },
    {
        "name": "Carbohydrate",
        "name_es": "Carbohidratos",
        "key": "carbohydrate",
        "match": ["carbohydrate", "carbohidrato", "choavl", "total carbohydrate", "carbohidratos totales"]
    },
    {
        "name": "Lactose",
        "name_es": "Lactosa",
        "key": "lactose",
        "match": ["lactose", "lactosa"]
    },
    {
        "name": "Zinc",
        "name_es": "Zinc",
        "key": "zinc",
        "match": ["zinc"]
    },
    {
        "name": "Folic Acid",
        "name_es": "Ácido Fólico",
        "key": "folic_acid",
        "match": ["folic acid", "acido folico", "acid folico", "acido folic", "acid folic", "foldfe"]
    },
    {
        "name": "Vitamin A",
        "name_es": "Vitamina A",
        "key": "vita",
        "match": ["vitamina a", "vitamin a"]
    },
    {
        "name": "Vitamin D",
        "name_es": "Vitamina D",
        "key": "vitd",
        "match": ["vitamina d", "vitamin d"]
    },
    {
        "name": "Cholesterol",
        "name_es": "Colesterol",
        "key": "cholesterol",
        "match": ["cholesterol", "colesterol"]
    },
    {
        "name": "Sugar",
        "name_es": "Azúcares",
        "key": "sugar",
        "match": ["sugar", "sugares", "azucar", "azucares", "azucares totales", "total sugars", "sugars"]
    },
    {
        "name": "Calcium",
        "name_es": "Calcio",
        "key": "calcium",
        "match": ["calcium", "calcio"]
    },
    {
        "name": "Selenium",
        "name_es": "Selenio",
        "key": "selenium",
        "match": ["selenium", "selenio"]
    },
    {
        "name": "Pantothenic Acid",
        "name_es": "Ácido Pantoténico",
        "key": "pantothenic_acid",
        "match": ["pantothenic acid", "pantac", "acido pantotenico"]
    },
    {
        "name": "Vitamin B12",
        "name_es": "Vitamina B12",
        "key": "vitb12",
        "match": ["vitb12", "vitamina b12", "vitamin b12"]
    },
    {
        "name": "Vitamin B2",
        "name_es": "Vitamina B2",
        "key": "vitb2",
        "match": ["vitb2", "vitamina b2", "vitamin b2"]
    },
    {
        "name": "Vitamin B6",
        "name_es":"Vitamina B6",
        "key": "vitb6",
        "match": ["vitb6", "vitb6", "vitamina b6", "vitamin b6"]
    },
    {
        "name": "Vitamin K",
        "name_es":"Vitamina K",
        "key": "vitk",
        "match": ["vitamina k", "vitamin k"]
    },
    {
        "name": "Fibre",
        "name_es": "Fibra",
        "key": "fibre",
        "match": ["fibtg", "fibre", "fibra", "dietary fiber", "fibra dietetica", "roughage"]
    },
    {
        "name": "Magnesium",
        "name_es": "Magnesio",
        "key": "magnesium",
        "match": ["magnessium", "magnesio"]
    },
    {
        "name": "Net Content",
        "name_es": "Contenido Neto",
        "key": "net_content",
        "match": ["net content", "netcontent", "contenido neto"]
    },
    {
        "name": "Iodide",
        "name_es": "Yoduro",
        "key": "iodide",
        "match": ["iodide", "yoduro"]
    },
    {
        "name": "Serving Quantity Information",
        "name_es": "Tamaño de porción",
        "key": "serving_quantity",
        "match": ["serving quantity", "serving quantity information", "tamano de porcion", "serv size", "serving size",
                  "serv quantity",  "serv qty"]
    },
    {
        "name": "Polyols",
        "name_es": "Polioles",
        "key": "polyols",
        "match": ["polyols", "polioles", "polyl"]
    },
    {
        "name": "Sodium Chloryde",
        "name_es": "Cloruro de Sodio",
        "key": "sodium_chloryde",
        "match": ["sodium chloryde", "cloruro de sodio", "nacl", "sales"]
    },
    {
        "name": "Saturated Fat",
        "name_es": "Grasas Saturadas",
        "key": "sat_fat",
        "match": ["fasat", "saturated fat", "grasas saturadas", "grasa saturada"]
    },
    {
        "name": "Protein",
        "name_es": "Proteína",
        "key": "protein",
        "match": ["protein", "proteina"]
    },
    {
        "name": "Galactose",
        "name_es": "Galactosa",
        "key": "galactose",
        "match": ["galactose", "galactosa"]
    },
    {
        "name": "Bicarbonate",
        "name_es": "Bicarbonato",
        "key": "bicarbonate",
        "match": ["bicarbonate", "bicarbonato", "g hc"]
    },
    {
        "name": "Iron",
        "name_es": "Hierro",
        "key": "iron",
        "match": ["hierro", "iron"]
    },
    {
        "name": "Biotin",
        "name_es": "Biotina",
        "key": "biotin",
        "match": ["biotin", "biot", "biotina"]
    },
    {
        "name": "Oleic Acid",
        "name_es": "Ácido Oleico",
        "key": "oleic_acid",
        "match": ["oleic acid", "omega 9", "acido oleico", "acid oleico", "acido oleic", "oleic acido"]
    },
    {
        "name": "Phosphorus",
        "name_es": "Fósforo",
        "key": "phosphorus",
        "match": ["phosphorus", "fosforo"]
    },
    {
        "name": "Copper",
        "name_es": "Cobre",
        "key": "copper",
        "match": ["copper", "cobre"]
    },
    {
        "name": "Sodium",
        "name_es": "Sodio",
        "key": "sodium",
        "match": ["sodio", "sodium"]
    }
]


WEIGHT_UNITS = [
    {
        "name" : "ml",
        "name_es" : "mililitro(s)",
        "match" : ["ml","mililitros","mltrs","mls","militers", "mlt"]
    },
    {
        "name" : "l",
        "name_es" : "litro(s)",
        "match" : ["l","litros","ltrs","liters", "ltr"]
    },
    {
        "name" : "mg",
        "name_es" : "miligramo(s)",
        "match" : ["miligrams","miligramos","mg","miligramo","mgs"]
    },
    {
        "name" : "ug",
        "name_es" : "microgramo(s)",
        "match" : ["micrograms","ug","miligramo", "mcg"]
    },
    {
        "name" : "g",
        "name_es" : "gramo(s)",
        "match" : ["grams","gramos","g","gramo","gr", "grm"]
    },
    {
        "name" : "onz",
        "name_es" : "onza(s)",
        "match" : ["ounce","ounces","onza","onzas","onz"]
    },
    {
        "name" : "pnt",
        "name_es" : "pinta(s)",
        "match" : ["pint","pinta","ptd", "pti"]
    },
    {
        "name" : "kg",
        "name_es" : "kilogramo(s)",
        "match" : ["kg","kgs","kilogramos","kilogramo","kilograms","kilogram","kilos", "kilo", "kgm"]
    }
]


class Nutriments:
    def __init__(self, language='en'):
        self.langage=language
        self.raw_nutriments={}
        self.nutriments={}
        self.good_name = None
        self.nutriment = False


    @staticmethod
    def create_nutriment(key=None, name=None, daily=None, unit=None, qty=None):
        return {
            "key": key,
            "name": name,
            "unit": unit,
            "qty": qty,
            "daily": daily
        }


    def guess_nutr(self, text):
        name, self.nutriment = self.get_name(text)
        if name is not False:
            self.add_nutriment(text, name=name, is_raw=True)
        else:
            self.add_nutriment(text, name='raw', is_raw=True)


    def add_nutriment(self, *args, **kargs):
        """
        This method helps you to add nutriments easily

        Individual nutriments:
            :param name: Type of nutriment. Ex: 'brand', 'ingredient', 'category'
            :param daily: The daily of the nutriment. Ex: 'Brand's Name', 'Ingredient's Name'
            :param unit: The units of the nutriment. Ex: 'Kg', 'Kilograms', 'Lt'
            :param qty: The quantity of the nutriment. Ex 1, 100, 150
            :param order: The order of the nutriment
            :return: Update the nutriments & raw_nutriments

        Batch nutriments:
            :param Dict of nutriments {'name': 'daily'}
        """
        if args:
            if len(args) == 1:
                if isinstance(args[0], dict):
                    if kargs.get('name', False) is not False:
                        for daily, qty in args[0].items():
                            self.add_nutriment(name=kargs.get('name'), qty=qty, daily=daily)
                    else:
                        for name, value in args[0].items():
                            self.add_nutriment(name=name, values=value)
                elif isinstance(args[0], str):
                    if kargs.get('name', False) is not False:
                        self.add_nutriment(name=kargs.get('name'), values=args[0])
                    else:
                       self.guess_nutr(args[0])
                elif isinstance(args[0], list) or isinstance(args[0], tuple) or isinstance(args[0], set):
                    if kargs.get('name', False) is not False:
                        if isinstance(args[0], list) or isinstance(args[0], tuple):
                            for value in args[0]:
                                if value:
                                    self.add_nutriment(name=kargs.get('name'), values=value)
                    else:
                        for value in args[0]:
                            if value:
                                self.guess_nutr(value)
                else:
                    print("ERROR adding nutrition fact: {} type is not supported ({})".format(str(args[0]), type(args[0])))
                    return False
        elif kargs:
            name = kargs.get('name', 'raw')
            values = kargs.get('values', '')
            if self.nutriment is None or self.nutriment is False:
                name_matched, self.nutriment = self.get_name(name)
            if self.nutriment is not False:
                nutr_dict = {
                    'key': self.nutriment.get('key'),
                    'name': self.nutriment.get('name_es') if self.langage == 'es' else self.nutriment.get('name')
                }
                is_raw = False
                nutr_dict.update(self.gess_values(self.nutriment,  daily=kargs.get('daily'), unit=kargs.get('unit'), qty=kargs.get('qty'), values=values))
            else:
                nutr_dict = {
                    'key': name,
                    'name': name + ' ' + values
                }
                is_raw = True
                nutr_dict.update(self.gess_values(None,  daily=kargs.get('daily'), unit=kargs.get('unit'), qty=kargs.get('qty'), values=values))




            if kargs.get('is_raw', False) is True:
                is_raw = True




            self.update_nutr(nutr_dict, is_raw)
        else:
            print("ERROR adding nutrition fact: You should pass at least 1 paramenter")


    def update_nutr(self, parsed_nutr, is_raw=True):
        key = parsed_nutr.get('key', 'raw')
        if key not in ['calories', 'serving_quantity'] and\
                (parsed_nutr.get('unit') is None or parsed_nutr.get('qty') is None):
            is_raw = True

        if is_raw is True:
            nutr = self.raw_nutriments.get(key, False)
            if nutr is False:
                self.raw_nutriments[key] = [parsed_nutr]
            elif isinstance(nutr, list):
                self.raw_nutriments[key].append(parsed_nutr)
        else:
            nutr = self.nutriments.get(key, False)
            if nutr is False:
                self.nutriments[key] = [parsed_nutr]
            elif isinstance(nutr, list):
                self.nutriments[key].append(parsed_nutr)
        self.nutriment = None


    @staticmethod
    def get_name(text, min_score=90, trusty_score=95):
        text = ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters or x in [" ", '1', '2' , '6', '9']).lower()
        text.strip()
        text = re.sub(r'\s+', ' ', text)
        max_score = float('-inf')
        closer_nutr = False
        for nutr in NUTRIMENTS:
            choices = nutr.get("match")
            result = process.extractOne(text, choices, scorer=fuzz.WRatio, score_cutoff=min_score)
            if result and result[1] > max_score:
                closer_nutr = nutr.get('key')
                closer_dict = nutr
                closer_dict['closer_match'] = result[0]
                max_score = result[1]
                if max_score >= trusty_score:
                    return closer_nutr, nutr
        if max_score >= min_score:
            return closer_nutr, closer_dict
        else:
            return False, False


    def gess_values(self, nutr, daily=None, unit=None, qty=None, values=None):
        guess_dict ={
            "qty": None,
            "daily": None,
            "unit": None
        }
        if qty is not False:
            if isinstance(qty, str):
                if unit is False:
                    unit, closer_unit = self.get_unit(qty)
                qty = self.str_to_float(qty)
                qty = qty if qty is not False else None

            elif isinstance(qty, float) or isinstance(qty, float):
                qty = float(qty)

        if daily is not False:
            if isinstance(daily, str):
                daily = self.str_to_float(daily)
                daily = daily if daily is not False else None

            elif isinstance(daily, float) or isinstance(daily, float):
                daily = float(daily)

        if unit is not False and isinstance(unit, str):
            unit, closer_unit = self.get_unit(unit, is_trusty=True)
            if unit is not False:
                unit = unit

        if values and isinstance(values, str):
            values_txt = ''.join(
            x for x in unicodedata.normalize('NFKD', values) if x in string.ascii_letters or x in [" ", "%"]).lower()
            if nutr is not None:
                values_txt = values_txt.replace(nutr.get('closer_match'), '')
            if unit is None:
                unit, closer_unit = self.get_unit(values_txt)
            if qty is None:
                qty_search = re.search(r'([\d\.]+) *{unit}'.format(unit=closer_unit), values)
                if qty_search:
                    try:
                        qty = float(qty_search.group(1))
                    except:
                        qty = None
                if qty is None:
                    qty_search = re.findall(r'([\d\.]+)', values)
                    if len(qty_search) == 1:
                        if '%' not in values:
                            try:
                                qty = float(qty_search[0])
                            except:
                                qty = None
                        else:
                            try:
                                daily = float(qty_search[0])
                            except:
                                daily = None
                    elif len(qty_search) == 2:
                        if '%' in values:
                            daily_search = re.search(r'([\d\.]+) *%', values)
                            if daily_search:
                                try:
                                    daily_str = daily_search.group(1)
                                    qty = set(qty_search) - {daily_search}

                                    if len(qty) == 1:
                                        try:
                                            qty = float(qty)
                                        except:
                                            qty = None
                                    daily = float(daily_str)
                                except:
                                    daily = None
            if daily is None and '%' in values:
                daily_search = re.findall(r'([\d\.]+)', values)
                if len(daily_search) == 1:
                    try:
                        daily = float(qty_search[0])
                    except:
                        daily = None
                else:
                    daily_search = re.search(r'([\d\.]+) *%', values)
                    if daily_search:
                        try:
                            daily = float(daily_search.group(1))
                        except:
                            daily = None

        if guess_dict["qty"] is None:
            guess_dict["qty"] = qty
        if guess_dict["daily"] is None:
            guess_dict["daily"] = daily
        if guess_dict["unit"] is None:
            guess_dict["unit"] = unit

        return guess_dict


    def get_unit(self, text, is_trusty=False, min_score=95, trusty_score=100):
        if not isinstance(text, str):
            return False
        text = ''.join(
            x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters or x in [" "]).lower()
        text.strip()
        text = re.sub(r'[\d%]', '', text)
        text = re.sub(r'\s+', ' ', text)
        if is_trusty:
            trustier_text = re.search('[\d\.]* *([\(\)a-z]+)', text)
            trustier_text = trustier_text.group(1) if trustier_text else False
        else:
            trustier_text = False
        max_score = float('-inf')
        closer_unit = False
        closer_match = False
        for unit in WEIGHT_UNITS:
            choices = unit.get("match")
            if trustier_text is not False:
                result = process.extractOne(text, choices, scorer=fuzz.UWRatio, score_cutoff=min_score)
                if result is not None:
                    aux = unit.get('name_es') if self.langage == 'es' else unit.get('name')
                    return aux, result[0]
                continue
            result = process.extractOne(text, choices, scorer=fuzz.token_set_ratio, score_cutoff=min_score)
            if result and result[1] >= max_score:
                closer_unit = unit.get('name_es') if self.langage == 'es' else unit.get('name')
                closer_match = result[0]
                max_score = result[1]
            if is_trusty is True or max_score >= trusty_score:
                return closer_unit, closer_match
        if max_score > min_score:
            return closer_unit, closer_match
        else:
            return False, False


    @staticmethod
    def str_to_float(text):
        if not isinstance(text, str):
            return False
        text = re.sub(r'\s+', ' ', text)

        text = re.sub(r'[^\d\.]', '', text)
        text.strip()
        try:
            return float(text)
        except:
            return False


    def get_nutrs(self):
        return self.nutriments, self.raw_nutriments

