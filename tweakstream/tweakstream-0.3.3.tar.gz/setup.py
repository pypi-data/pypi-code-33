# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tweakstream']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'click>=7.0,<8.0',
 'crayons>=0.1.2,<0.2.0',
 'tabulate>=0.8.3,<0.9.0',
 'tweakers>=0.3.2,<0.4.0']

setup_kwargs = {
    'name': 'tweakstream',
    'version': '0.3.3',
    'description': 'Stream topics from gathering.tweakers.net',
    'long_description': '# tweakstream\n\nStream topics from [gathering.tweakers.net](https://gathering.tweakers.net) in your terminal.\n\n## Install\nNote: `tweakstream` requires Python >= 3.6.\n```\npip install tweakstream\n```\n\n## Usage\n\n### List active topics\n```\n$ tweakstream list\n\n   #  Titel                                                         Laatste reactie\n---  ------------------------------------------------------------  -----------------\n  1  Lucht/Water warmtepomp om mee te verwarmen en koelen #6       19:50\n  2  Het Hardstyle-topic - deel 2                                  19:50\n  3  Panasonic Monoblock [H versie ] ervaringen - settings - help  19:50\n  4  [Slowchat] Het grote cryptocurrency slowchat topic #5         19:50\n  5  Is de LG 49" 49SK7 een goeie televisie?                       19:49\n  6  Welke wielmoeren voor stalen velgen?                          19:49\n  7  [Google Assistent] Ervaringen & Discussie                     19:49\n  8  Het grote Ford topic                                          19:49\n  9  [Verzamel] Long exposure fotografie (ND... filters)           19:48\n 10  De gasdiscussie : wanneer stap jij van het gas af?            19:48\n```\n\n### Stream a specific topic\n```\n$ tweakstream stream https://gathering.tweakers.net/forum/list_messages/1852751\n19:46 burnebie https://gathering.tweakers.net/forum/list_message/56741767#56741767\nJe weet het allemaal nogal \n\n19:50 freestyler2 https://gathering.tweakers.net/forum/list_message/56741793#56741793\nGraag wil ik iedereen erop wijzen dat er een Masternodes topic is. Discussies hieromtrent graag hier bespreken:\nfreestyler2 in "[Masternodes] Het grote Masternodes topic deel 1" \n\n19:51 Jaapio https://gathering.tweakers.net/forum/list_message/56741815#56741815\nBartvandelaar schreef op donderdag 11 oktober 2018 @ 19:24:\n[...]\n\n\nIk moet toch altijd smakelijk lachen om jou reacties. Voor dat we beide miljonair zijn gaan wij nog eens samen een biertje doen in de kroeg. Een avondje hard lachen.\nDat moet een keertje goed komen. En dan tegen random mensen aan de bar zeggen: \'tis toch wat met die shitcoins, dikke pump en dumps man. Hopen dat de uitbraak van de triangle gigantisch naar boven is, anders geen lambo dit jaar ben ik bang...\' en weglopen.\n\nAltijd leuk. \n```\n\n### Search for topics\n```\n$ tweakstream search "F1"\n\n   #  Titel                                                Laatste reactie\n---  ---------------------------------------------------  -----------------\n  1  [Pocophone F1] Levertijden & Prijzen                 19:43\n  2  [F1] Seizoen 2018 - deel 2                           19:48\n  3  [F1 2018] Race 17 - GP van Japan                     09-10\n  4  [Multi] F1 2018                                      09:45\n  5  [PC] F1 2018 race buddies                            01-09\n  6  [Pocophone F1] Accessiores                           30-09\n  7  Oneplus 6T vs Pocophone F1                           02-10\n  8  [F1] Racemanagers/pools 2017                         13-02\n  9  Koppeling f1 2017                                    09-03\n 10  [Xiaomi Pocophone F1] Stock Android installeren      25-09\n \nChoose a topic to stream (1-10): \n```',
    'author': 'Timo',
    'author_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
