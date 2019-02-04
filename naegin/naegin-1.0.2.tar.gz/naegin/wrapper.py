# -*- coding: utf-8 -*-
from .errors import *
from .image import NaeginImage

import aiohttp

class Client:
    '''API Wrapper para Naeg.in

    - Descrição:
        Cria uma instância

    - Parâmetros:
        token : str
        (Token fornecido para usar a API)
    '''
    def __init__(self, token):
        if not isinstance(token, str):
            raise ArgumentoInvalido('Tokens devem ser strings')

        self.url = 'https://api.naeg.in/img?token=' + token

    async def get_all_tags(self):
        '''API Wrapper para Naeg.in

        - Descrição:
            Retorna todas as tags disponíveis em uma list
        '''
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as r:
                if r.status != 200:
                    raise RespostaInvalida('Falha na requisição: Código inválido retornado')
            
                data = await r.json()
                if data['erro'] and data['mensagem'] != 'Tag Invalida':
                    raise ArgumentoInvalido(data['mensagem'])
                
                return data['tags']

    async def get_random(self, tag, nsfw = False):
        '''API Wrapper para Naeg.in

        - Descrição:
            Busca e retorna o link de uma imagem com a tag fornecida

        - Parâmetros:
            tag : str
            (Usada para buscar imagens)

            nsfw : bool (opcional)
            (NOTA: Tags NSFW apenas vão funcionar se você especificar "nsfw" como True)
        '''
        if not isinstance(tag, str):
            raise ArgumentoInvalido('Tags devem ser strings')
        
        if not isinstance(nsfw, bool):
            raise ArgumentoInvalido('Valor NSFW deve ser boolean')

        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.url}&tag={tag}&nsfw={nsfw}') as r:
                if r.status != 200:
                    raise RespostaInvalida('Falha na requisição: Código inválido retornado')
            
                data = await r.json()
                if data['erro']:
                    raise ArgumentoInvalido(data['mensagem'])
            
                return NaeginImage(**data)