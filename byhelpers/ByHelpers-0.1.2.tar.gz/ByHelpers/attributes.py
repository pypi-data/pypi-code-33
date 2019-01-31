#-*- coding: utf-8-*-

import unicodedata
import string
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import re

ATTRIBUTES = [
    {
        "key": "presentation",
        "match": ["presentation", "presentacion"],
    },
    {
        "key": "measure_unit",
        "match": ["units", "measure", "measurement", "medida", "unidades"],
    },
    {
        "key": "size",
        "match": ["size", "talla", "tamano", 'siz'],
    },
    {
        "key": "material",
        "match": ["material", "mtrl"],
    },
    {
        "key": "ingredient",
        "match": ["ingredient", "ingrediente", "ingredients", "ingredientes"]
    },
    {
        "key": "category",
        "match": ["category", "categories", "categoria", "categorias"]
    },
    {
        "key": "laboratory",
        "match": ["laboratorio", "laboratory", "lab"]
    },
    {
        "key": "model",
        "match": ["model", "modelo"]
    },
    {
        "key": "brand",
        "match": ["brand", "marca"]
    },
    {
        "key": "provider",
        "match": ["proveedor", "provider"]
    },
    {
        "key": "flavour",
        "match": ["flavour", "taste", "savor", "sabor"]
    },
    {
        "key": "color",
        "match": ["color"]
    },
    {
        "key": "genre",
        "match": ["genre", "gender", "kind", "genero", "sex", "sexo"]
    },
    {
        "key": "age",
        "match": ["age", "ages", "edad", "edades"]
    },
    {
        "key": "condition",
        "match": ["condition", "condicion", "status", "estado"]
    },
    {
        "key": "height",
        "match": ["height", "alto", "hgt"]
    },
    {
        "key": "width",
        "match": ["width", "ancho", "wdth"]
    },
    {
        "key": "length",
        "match": ["length", "long", "largo"]
    },
    {
        "key": "weight",
        "match": ["weight", "peso"]
    }
]

ATTRIBUTES_FIXED = {
    "presentation": {
        "value": [
            {
                "match": ["taza", "copa", "cup"],
                "name": "cup",
                "name_es": "taza"
            },
            {
                "match": ["packs", "unidades", "cnt", "count", "units", "ct"],
                "name": "units",
                "name_es": "unidades"
            },
            {
                "match": ["dose","dosis"],
                "name": 'dose',
                "name_es": "dosis"
            },
            {
                "match": ["canister", "frasco"],
                "name": "canister",
                "name_es": "frasco"
            },
            {
                "match": ["lata", "can"],
                "name": "can",
                "name_es": "lata"
            },
            {
                "match" : ["caja", "box", "boxes"],
                "name": "box",
                "name_es": "caja"
            },
            {
                "name" : "tablet",
                "name_es" : "tabletas",
                "match" : ["tableta","tabletas","tab","tabs","grajeas","grageas","tabl"]
            },
            {
                "name" : "capsule",
                "name_es" : "cápsulas",
                "match" : ["capsula","capsulas","comprimidos","caps","cap"]
            },
            {
                "name" : "cream",
                "name_es" : "crema",
                "match" : ["crema","cream"]
            },
            {
                "name" : "unit",
                "name_es" : "unidades",
                "match" : ["unidades","unidad","units","pieza","piezas","pz","pzs","pzas", "u" , "h87", "1n", "counts"]
            },
            {
                "name" : "kit",
                "name_es" : "paquete",
                "match" : ["set", "kt", "kit", "pack", "paquete", "combo"]
            },
            {
                "name" : "ointment",
                "name_es" : "ungüento",
                "match" : ["unguento", "ung", "ointment"]
            },
            {
                "name" : "suspension",
                "name_es" : "suspensión",
                "match" : ["susp","suspension"]
            },
            {
                "name" : "suppository",
                "name_es" : "supositorio",
                "match" : ["supositorio","suppository"]
            },
            {
                "name" : "env",
                "name_es" : "sobres",
                "match" : ["sobre","sobres","envelopes"]
            },
            {
                "name" : "gel",
                "name_es" : "gel",
                "match" : ["gel"]
            },
            {
                "name" : "solution",
                "name_es" : "solución",
                "match" :["sol","solucion","solution","solución"]
            },
            {
                "name" : "drops",
                "name_es" : "gotas",
                "match" :["gotas","gota","drops"]
            },
            {
                "name" : "tube",
                "name_es" : "tubo",
                "match" : ["tubo","tub","tube"]
            },
            {
                "name" : "ampoule",
                "name_es" : "ampolletas",
                "match" : ["ampolletas","ampoules","ampolleta"]
            },
            {
                "match": ["botella", "bottle"],
                "name": "bottle",
                "name_es": "botella"
            },
            {
                "match": ["bolsa", "bag"],
                "name": "bag",
                "name_es": "bolsa"
            }
        ],
        "fixed": [('value', str)],
        "must": [('value', str)],
        "name": "Presentation",
        "name_es": "Presentación"
    },
    "measure_unit": {
        "value": [
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
                "match" : ["micrograms","ug","miligramo","mcg"]
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
                "name" : "bar",
                "name_es" : "bar(es)",
                "match" : ["bar","bares","bars"]
            },
            {
                "name" : "kg",
                "name_es" : "kilogramo(s)",
                "match" : ["kg","kgs","kilogramos","kilogramo","kilograms","kilogram","kilos", "kilo", "kgm"]
            },
            {
                "name" : "mm",
                "name_es" : "milimetro(s)",
                "match" : ["mm","mms","milimetros","milimetro","millimeters","millimeter", "mmt"]
            },
            {
                "name" : "cm",
                "name_es" : "centimetro(s)",
                "match" : ["cm","cms","centimetros","centimetro","centimeters","centimeter"]
            },
            {
                "name": "in",
                "name_es": "pulgada(s)",
                "match": ["inch", '"', "pulgada", "in", "pulgadas"]
            },
            {
                "name" : "m",
                "name_es" : "metro(s)",
                "match" : ["m","ms","mtr"]
            },
            {
                "name" : "km",
                "name_es" : "kilometro(s)",
                "match" : ["km","kms","kilometros","kilometro","kilometers","kilometer", "kmt"]
            },
            {
                "name" : "par",
                "name_es" : "par(es)",
                "match" : ["par", "pares", "pair", "pairs", "pr"]
            }
        ],
        "fixed": [('value', str)],
        "must": [('value', str)],
        "name": "Measure Units",
        "name_es": "Unidades de Medida"
    },
    "size": {
        "value": [
            {
                "name" : "sm",
                "name_es" : "chico",
                "match" : ["ch","chico","pequeno","pequeño","small","sm","chicos","petite", 's']
            },
            {
                "name" : "md",
                "name_es" : "mediano",
                "match" : ["md","mediano","medium","medianos", 'm']
            },
            {
                "name" : "lg",
                "name_es" : "grande",
                "match" : ["lg","large","grande","grandes", 'l']
            },
            {
                "name" : "xl",
                "name_es" : "extra grande",
                "match" : ["extragrande","extra grande","extra large","xl","xxl","xxxl","extralarge"]
            }
        ],
        "fixed": [('value', str)],
        "must": [('value', str)],
        "type": str,
        "name": "Size",
        "name_es": "Tamaño"
    },
    "material": {
       "name": "Material",
       "name_es": "Material",
       "must": [('value', str)],
    },
    "ingredient": {
        "name": "Ingredient",
        "name_es": "Ingrediente",
        "must": [('value', str)]
    },
    "category":   {
        "name": "Category",
        "name_es": "Categoría",
        "must": [('value', str), ("order", int)],
    },
    "laboratory": {
        "name": "Laboratory",
        "name_es": "Laboratorio",
        "must": [('value', str)]
    },
    "model": {
       "name": "Model",
       "name_es": "Modelo",
       "must": [('value', str)]
    },
    "brand": {
        "name": "Brand",
        "name_es": "Marca",
        "must": [('value', str)]
    },
    "provider": {
        "name": "Provider",
        "name_es": "Proveedor",
        "must": [('value', str)]
    },
    "flavour": {
        "name": "Flavour",
        "name_es": "Sabor",
        "must": [('value', str)]
    },
    "color": {
        "name": "Color",
        "name_es": "Color",
        "must": [('value', str)]
    },
    "genre": {
        "name": "Genre",
        "name_es": "Género",
        "must": [('value', str)]
    },
    "age": {
        "name": "Age",
        "name_es": "Edad",
        "must": [('value', str)]
    },
    "condition": {
        "name": "Condition",
        "name_es": "Condición",
        "must": [('value', str)]
    },
    "height": {
        "name": "Height",
        "name_es": "Alto",
        "unit": [
            {
                "name": "mm",
                "name_es": "milimetro(s)",
                "match": ["mm", "mms", "milimetros", "milimetro", "millimeters", "millimeter", "mmt"]
            },
            {
                "name": "cm",
                "name_es": "centimetro(s)",
                "match": ["cm", "cms", "centimetros", "centimetro", "centimeters", "centimeter"]
            },
            {
                "name": "in",
                "name_es": "pulgada(s)",
                "match": ["inch", '"', "pulgada", "in", "pulgadas"]
            },
            {
                "name": "m",
                "name_es": "metro(s)",
                "match": ["m", "ms", "mtr"]
            },
            {
                "name": "km",
                "name_es": "kilometro(s)",
                "match": ["km", "kms", "kilometros", "kilometro", "kilometers", "kilometer", "kmt"]
            }
        ],
        "fixed": [("unit", str)],
        "must": [('value', float), ("unit", str)]
    },
    "width": {
       "name": "Width",
       "name_es": "Ancho",
       "unit": [
            {
                "name": "mm",
                "name_es": "milimetro(s)",
                "match": ["mm", "mms", "milimetros", "milimetro", "millimeters", "millimeter", "mmt"]
            },
            {
                "name": "cm",
                "name_es": "centimetro(s)",
                "match": ["cm", "cms", "centimetros", "centimetro", "centimeters", "centimeter"]
            },
            {
                "name": "in",
                "name_es": "pulgada(s)",
                "match": ["inch", '"', "pulgada", "in", "pulgadas"]
            },
            {
                "name": "m",
                "name_es": "metro(s)",
                "match": ["m", "ms", "mtr"]
            },
            {
                "name": "km",
                "name_es": "kilometro(s)",
                "match": ["km", "kms", "kilometros", "kilometro", "kilometers", "kilometer", "kmt"]
            }
        ],
       "fixed": [("unit", str)],
       "must": [('value', float), ("unit", str)]
    },
    "length": {
        "name": "Length",
        "name_es": "Largo",
        "unit": [
            {
                "name": "mm",
                "name_es": "milimetro(s)",
                "match": ["mm", "mms", "milimetros", "milimetro", "millimeters", "millimeter", "mmt"]
            },
            {
                "name": "cm",
                "name_es": "centimetro(s)",
                "match": ["cm", "cms", "centimetros", "centimetro", "centimeters", "centimeter"]
            },
            {
                "name": "in",
                "name_es": "pulgada(s)",
                "match": ["inch", '"', "pulgada", "in", "pulgadas"]
            },
            {
                "name": "m",
                "name_es": "metro(s)",
                "match": ["m", "ms", "mtr"]
            },
            {
                "name": "km",
                "name_es": "kilometro(s)",
                "match": ["km", "kms", "kilometros", "kilometro", "kilometers", "kilometer", "kmt"]
            }
        ],
        "fixed": ["unit"],
        "must": ["value", "unit"],
        "type": float
    },
    "weight": {
        "name": "Weight",
        "name_es": "Peso",
        "unit": [
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
                "match" : ["miligrams","miligramos","mg","miligramo","mgs" ]
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
        ],
        "fixed": [("unit", str)],
        "must": [('value', float), ("unit", str)]
    }
}

class Attributes:
    def __init__(self, language='en'):
        self.langage=language
        self.raw_attributes={}
        self.attributes={}

    @staticmethod
    def create_attribute(key=None, name=None, value=None, unit=None, qty=None, order=None):
        return {
            "key": key,
            "name": name,
            "value": value,
            "unit": unit,
            "qty": qty,
            "order": order
        }

    def guess_attr(self, text):
        name = self.get_name(text)
        if name is not False:
            self.add_attribute(text, name=name, is_raw=True)
        else:
            self.add_attribute(text, name='raw', is_raw=True)

    def add_attribute(self, *args, **kargs):
        """
        This method helps you to add attributes easily

        Individual attributes:
            :param name: Type of attribute. Ex: 'brand', 'ingredient', 'category'
            :param value: The value of the attribute. Ex: 'Brand's Name', 'Ingredient's Name'
            :param unit: The units of the attribute. Ex: 'Kg', 'Kilograms', 'Lt'
            :param qty: The quantity of the attribute. Ex 1, 100, 150
            :param order: The order of the attribute
            :return: Update the attributes & raw_attributes

        Batch attributes:
            :param Dict of attributes {'name': 'value'}
        """
        if args:
            if len(args) == 1:
                if isinstance(args[0], dict):
                    if kargs.get('name', False) is not False:
                        for value, qty in args[0].items():
                            self.add_attribute(name=kargs.get('name'), value=value, qty=qty)
                    else:
                        for name, value in args[0].items():
                            self.add_attribute(name=name, value=value)
                elif isinstance(args[0], str):
                    if kargs.get('name', False) is not False:
                        self.add_attribute(value=args[0], qty=args[0], unit=args[0], name=kargs.get('name'), is_raw=kargs.get('is_raw', False))
                    else:
                       self.guess_attr(args[0])
                elif isinstance(args[0], list) or isinstance(args[0], tuple) or isinstance(args[0], set):
                    if kargs.get('name', False) is not False:
                        if isinstance(args[0], list) or isinstance(args[0], tuple):
                            for index, value in enumerate(args[0]):
                                if value:
                                    self.add_attribute(value=value,  name=kargs.get('name'), order=index+1)
                        else:
                            for value in args[0]:
                                if value:
                                    self.add_attribute(value=value, qty=value, unit=value, name=kargs.get('name'))
                    else:
                        for value in args[0]:
                            if value:
                                self.guess_attr(value)
                else:
                    print("ERROR adding attribute: {} type is not supported ({})".format(str(args[0]), type(args[0])))
                    return False
        elif kargs:
            name = kargs.get('name', 'raw')
            good_name = self.get_name(name)
            if good_name is not False:
                name = good_name
                is_raw = False
            else:
                is_raw = True
            attributes = [('value', str), ('unit', str), ('qty', float), ('order', str)]

            attr = ATTRIBUTES_FIXED.get(name, {})
            if len(attr) == 0:
                is_raw = True

            attr_dict = {
                            'key': name,
                            'name': attr.get('name_es', name) if self.langage == 'es' else attr.get('name', name)
                        }
            fixed = {attr_fixed[0]: attr_fixed[1] for attr_fixed in attr.get('fixed', [])}
            must = {attr_must[0]: attr_must[1] for attr_must in attr.get('must', [])}

            for attribute, default_type in attributes:
                if attribute in fixed.keys() and kargs.get(attribute, False) is not False:
                    for fixed_values in attr.get(attribute):
                        match = fixed_values.get('match')
                        match_found = fixed_values.get('name_es') if self.langage == 'es' else fixed_values.get('name')
                        result = self.get_attr(kargs.get(attribute, False), match, expected_type=fixed.get(attribute))
                        if result is True:
                            result = match_found
                            break
                    else:
                        result = kargs.get(attribute)
                        is_raw = True
                elif attribute in must.keys() and kargs.get(attribute, False) is not False:
                    can_be_numeric = attr_dict['key'] in ['brand', 'provider', 'laboratory', 'model']
                    result = self.check_attr(kargs.get(attribute), expected_type=must.get(attribute), can_be_numeric=can_be_numeric)
                    if result is None:
                        result = kargs.get(attribute)
                        is_raw = True
                else:
                    result = None
                    # result = self.check_attr(kargs.get(attribute), expected_type=default_type)
                    # if result is None:
                    #     result = kargs.get(attribute)

                attr_dict[attribute] = result

            if kargs.get('is_raw', False) is True:
                is_raw = True

            self.update_attr(attr_dict, is_raw)
        else:
            print("ERROR adding attribute: You should pass at least 1 paramenter")

    def update_attr(self, parsed_attr, is_raw=True):
        if is_raw is True:
            key = parsed_attr.get('key', 'raw')
            attr = self.raw_attributes.get(key, False)
            if attr is False:
                self.raw_attributes[key] = [parsed_attr]
            elif isinstance(attr, list):
                self.raw_attributes[key].append(parsed_attr)
        else:
            key = parsed_attr.get('key', 'raw')
            attr = self.attributes.get(key, False)
            if attr is False:
                self.attributes[key] = [parsed_attr]
            elif isinstance(attr, list):
                self.attributes[key].append(parsed_attr)

    @staticmethod
    def get_name(text, min_score=80, trusty_score=90):
        text = ''.join(x for x in unicodedata.normalize('NFKD', text) if x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        max_score = float('-inf')
        closer_attr = False
        for attr in ATTRIBUTES:
            choices = attr.get("match")
            result = process.extractOne(text, choices, scorer=fuzz.partial_token_set_ratio, score_cutoff=min_score)
            if result and result[1] > max_score:
                closer_attr = attr.get('key')
                max_score = result[1]
            if max_score > trusty_score:
                return closer_attr
        if max_score > min_score:
            return closer_attr
        else:
            return False

    @staticmethod
    def get_attr(value, choices, min_score=90, expected_type=str):
        if isinstance(value, str):
            if expected_type is str:
                text = ''.join(x for x in unicodedata.normalize('NFKD', value) if x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
                text = text.strip()
                text = re.sub(r'\s+', ' ', text)
                result = process.extractOne(text, choices, scorer=fuzz.UWRatio, score_cutoff=min_score)
                if result and result[1] > min_score:
                    return True
                else:
                    return False
            elif expected_type is int or expected_type is float:
                value = re.sub(r'[^.,\s\d]', '', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                try:
                    return expected_type(value)
                except:
                    return False

        elif type(value) is expected_type:
            return value
        else:
            return False

    @staticmethod
    def check_attr(value, expected_type=str, can_be_numeric=False):
        if isinstance(value, str):
            if expected_type is str:
                if can_be_numeric == False:
                    text = ''.join(x for x in unicodedata.normalize('NFKD', value) if
                                   x in string.ascii_letters or x in [" ", '"', "'", '.', ',']).lower()
                else:
                    text = ''.join(x for x in unicodedata.normalize('NFKD', value) if
                                    x in string.ascii_letters
                                    or x in [" ", '"', "'", '.', ',']
                                    or x in string.digits
                                ).lower()
                text.strip()
                text = re.sub(r'\s+', ' ', text)
                text = text.strip()
                if text:
                    return text
                else:
                    return None
            elif expected_type is int or expected_type is float:
                value = re.sub(r'[^.,\s\d]', '', value)
                value = re.sub(r'\s+', ' ', value)
                value = value.strip()
                try:
                    return expected_type(value)
                except:
                    return None

        elif type(value) is expected_type:
            return value
        else:
            return None

    def get_attrs(self):
        return self.attributes, self.raw_attributes