import json
import os
import pytest


DATABASE = os.environ.get('DATABASE', 'DUMMY')
IS_PG = DATABASE not in ('cockroachdb', 'DUMMY')


@pytest.mark.skipif(not IS_PG, reason='Must be pg')
async def test_search_pg(container_requester):
    async with container_requester as requester:
        await requester(
            'POST', '/db/guillotina/',
            data=json.dumps({
                "@type": "Item",
                "title": "Item1",
                "id": "item1",
            })
        )

        resp, status = await requester(
            'POST', '/db/guillotina/@search',
            data=json.dumps({
                'title': 'Item1'
            }))
        assert status == 200
        assert len(resp['member']) == 1

        resp, status = await requester(
            'POST', '/db/guillotina/@search',
            data=json.dumps({
                'title': 'Foobar'
            }))
        assert status == 200
        assert len(resp['member']) == 0
