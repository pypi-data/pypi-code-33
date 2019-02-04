# -*- coding: utf-8 -*-
from setuptools import setup

rst = '''
Naegin
======

Naegin é uma API Wrapper para o site `naeg.in`_.

A API tem o objetivo de fornecer Imagens para desenvolvedores de bots
fazerem uso das mesmas em seus respectivos projetos.

Você precisa de um token para fazer uso desse serviço. Entre no
`Discord`_ do site para requisitar um.

Instalação
==========

Através do pip, você pode facilmente instalar a Wrapper, basta digitar
**``pip install naegin``** no terminal.

Certifique-se de estar usando o **Python 3**.

Uso
===

.. code:: python

   import naegin

   #Cria uma instância para ser usada
   naegin = naegin.Client('token')

   #Pegar todas as tags disponíveis em uma list
   async def tags():
      tags = await naegin.get_all_tags()
      print(tags)

   #Pegar a URL de uma Imagem aleatória, com uma Tag especifica
   async def random(tag):
      image = await naegin.get_random(tag)
      print(image.url)

.. _naeg.in: https://naeg.in/
.. _Discord: https://discord.gg/kdb4Hvd3
'''

setup(
    name='naegin',
    author='Naegin',
    url='https://github.com/Naegin/naegin',
    version='1.0.2',
    packages=['naegin'],
    install_requires=['aiohttp'],
    description='API Wrapper em Python para Naegin',
    long_description=rst,
    license='MIT License',
    keywords=['naegin', 'api', 'wrapper', 'images', 'pt-br', 'brazilian', 'portuguese'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: Portuguese (Brazilian)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Utilities',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)