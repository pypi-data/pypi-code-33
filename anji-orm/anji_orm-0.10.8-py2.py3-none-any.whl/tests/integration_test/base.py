# pylint: disable=invalid-name,too-many-public-methods
import asyncio
from datetime import timedelta, datetime
import time
import threading
import unittest

import asynctest
from toolz.itertoolz import count

from anji_orm import orm_register
from anji_orm.extensions import files

from .models import T1, X1, Y1, Next1Model, Next2Model, AbstractModel, T2, ModelWithFile, ModelWithFileDict
from ..base import purge_query_row_cache


class SyncTestSkeleton(unittest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def extensions(cls):
        return {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        extensions = cls.extensions()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstract class")
        purge_query_row_cache(T1, AbstractModel, T2)
        orm_register.init(connection_uri, pool_kwargs, extensions=extensions)

    def setUp(self):
        orm_register.load()
        orm_register.sync_strategy.truncate_table(T1._table)
        orm_register.sync_strategy.truncate_table(T2._table)
        orm_register.sync_strategy.truncate_table(AbstractModel._table)
        orm_register.sync_strategy.truncate_table(ModelWithFile._table)
        orm_register.sync_strategy.truncate_table(ModelWithFileDict._table)

    @classmethod
    def tearDownClass(cls):
        orm_register.close()

    def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        t1.send()
        t2.send()
        t1_list = T1.all().run()
        self.assertEqual(count(t1_list), 2)

    def test_get(self):
        t1 = T1(c1='5')
        t1.send()
        t1_1 = T1.get(t1.id)
        self.assertEqual(t1.c1, t1_1.c1)

    def test_simple_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = list((T1.c1 > '5').run())
        self.assertEqual(count(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_child_search(self):
        for c1 in map(str, range(0, 5)):
            Next1Model(c1=c1).send()
        for c1 in map(str, range(0, 5)):
            Next2Model(c1=c1, c2='5').send()
        self.assertEqual(Next1Model.all().count().run(), 5)
        self.assertEqual(Next2Model.all().count().run(), 5)
        self.assertEqual(AbstractModel.all().count().run(), 10)

    def test_child_sorting_and_filter(self):
        for c1 in map(str, range(0, 10)):
            Next1Model(c1=c1).send()
        self.assertEqual(Next1Model.c1.le('5').order_by(Next1Model.c1.amount).first().c1, '0')

    def test_related(self):
        t1 = T1(c1='5')
        t1.send()
        t2 = T2(t1=t1.id)
        t2.send()
        new_t2 = T2.all().first()
        self.assertEqual(new_t2.t1.id, t1.id)

    def test_list_related(self):
        t11 = T1(c1='5')
        t12 = T1(c1='6')
        t12.send()
        t11.send()
        t2 = T2()
        t2.t2.append(t11)
        t2.t2.append(t12.id)
        t2.send()
        new_t2 = T2.all().first()
        self.assertEqual(len(new_t2.t2), 2)
        self.assertEqual(new_t2.t2[0].id, t11.id)
        self.assertEqual(new_t2.t2[1].id, t12.id)

    def test_list_related_setter(self):
        t11 = T1(c1='5')
        t12 = T1(c1='6')
        t12.send()
        t11.send()
        t2 = T2(t2=[t11, t12.id])
        t2.send()
        new_t2 = T2.all().first()
        self.assertEqual(len(new_t2.t2), 2)
        self.assertEqual(new_t2.t2[0].id, t11.id)
        self.assertEqual(new_t2.t2[1].id, t12.id)

    def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        t1_1.send()
        t1_2 = T1.all().first()
        t1_2.c2 = '7'
        t1_2.send()
        t1_1.load()
        self.assertEqual(t1_1.c2, '7')

    def test_datetime(self):
        test_datetime = datetime.utcnow() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        t1_original.send()
        t1_1 = T1.all().first()
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = (T1.c3 == test_datetime).first()
        self.assertEqual(t1_2.c3, t1_original.c3)

    def test_complex_search(self):
        for c1 in map(str, range(0, 10)):
            T1(c1=c1, c2='5').send()
        t1_list = list(((T1.c1 > '5') & (T1.c1 < '8')).run())
        self.assertEqual(count(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    def test_sorting(self):
        for c1 in map(str, range(0, 3)):
            for c2 in map(str, range(0, 3)):
                T1(c1=c1, c2=c2).send()
        t1_list = T1.all().order_by(T1.c1.amount.desc, T1.c2.amount.desc).run()
        t1_first = next(t1_list)
        self.assertEqual(t1_first.c1, '2')
        self.assertEqual(t1_first.c2, '2')

    def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        t1.send()
        t1_search = next((T1.c4.c2 == 5).run())
        self.assertEqual(t1.c4, t1_search.c4)

    def test_complex_nested_queries(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        t1_list = ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).run()
        self.assertEqual(count(t1_list), 6)

    def test_internval_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).run()
        self.assertEqual(count(t1_list), 2)

    def test_in_nested_queries(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = (T1.c4.c1.one_of(1, 2)).run()
        self.assertEqual(count(t1_list), 2)

    def test_sample(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        t1_list = T1.all().sample(2).run()
        self.assertEqual(count(t1_list), 2)

    def test_base_aggregation(self):
        for c1 in range(0, 5):
            T1(c1='v' + str(c1)).send()
        self.assertEqual(T1.all().max(T1.c1).run(), 'v4')

    def test_nested_aggregation(self):
        for c1 in range(0, 5):
            T1(c4={"c1": c1}).send()
        self.assertEqual(T1.all().max(T1.c4.c1).run(), 4)

    def test_complicated_aggregation(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        self.assertEqual((T1.c4.c1 > T1.c4.c2).count().run(), 10)

    def test_complicated_query(self):
        for c1 in range(0, 5):
            for c2 in range(0, 5):
                T1(c4={"c1": c1, "c2": c2}).send()
        self.assertEqual(count((T1.c4.c1 > T1.c4.c2).run()), 10)

    def test_base_match(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}").send()
        self.assertEqual(count(T1.c5.match('v0').run()), 5)

    def test_match_aggregation(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}").send()
        self.assertEqual(T1.c5.match('v0').count().run(), 5)

    def test_match_complicated(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c5=f"v{c2}.{c1}", c1=str(c1), c2=str(c2)).send()
        self.assertEqual((T1.c5.match('v0') & (T1.c1 != T1.c2)).count().run(), 4)

    def test_group(self):
        for c1 in range(0, 5):
            for c2 in range(0, 2):
                T1(c1=str(c1), c2=str(c2)).send()
        self.assertEqual(T1.c1.ne(T1.c2).group(T1.c2).count().run(), {'0': 4, '1': 4})

    def test_enum(self):
        t1_1 = T1(c6=X1.t)
        t1_2 = T1(c7=Y1.t)
        t1_1.send()
        t1_2.send()
        t1_1_2 = T1.c6.eq(X1.t).first()
        t1_2_2 = T1.c7.eq(Y1.t).first()
        self.assertEqual(t1_1.id, t1_1_2.id)
        self.assertEqual(t1_2.id, t1_2_2.id)

    def test_changes(self):
        event_list = []

        def changes_sender(t1_list):
            time.sleep(2)
            for t1 in t1_list:
                t1.c1 = '2'
                t1.send()
            time.sleep(2)

        def changes_aggregator():
            for event in T1.c2.eq('1').changes(with_types=True).run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2=str(c2))
            for c1 in range(0, 5) for c2 in range(0, 2)
        ]
        for t1 in t1_list:
            t1.send()
        additional_thread = threading.Thread(target=changes_aggregator, daemon=True)
        additional_thread.start()
        changes_sender(t1_list)
        self.assertEqual(len(event_list), 5)
        for event in event_list:
            self.assertEqual(event.get('type'), 'change')
            self.assertTrue('doc' in event)

    def test_complex_changes(self):
        event_list = []

        def changes_sender(t1_list):
            time.sleep(5)
            for t1 in t1_list:
                t1.c1 = '-'
                t1.send()
            time.sleep(5)

        def changes_aggregator():
            for event in T1.c1.le(T1.c2).changes(with_types=True, with_initial=True).run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2='3')
            for c1 in range(0, 5)
        ]
        for t1 in t1_list:
            t1.send()
        additional_thread = threading.Thread(target=changes_aggregator, daemon=True)
        additional_thread.start()
        changes_sender(t1_list)
        self.assertEqual(len(event_list), 9)
        for event in event_list:
            self.assertIn(event.get('type'), ('change', 'add', 'initial'))
            self.assertTrue('doc' in event)

    def test_update(self):
        for c1 in range(0, 5):
            T1(c1=str(c1), c2='5').send()
        update_result = T1.c2.eq('5').update({'c2': '6'}).run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', T1.all().run())
        ))

    def test_atomic_update(self):
        for c1 in range(0, 5):
            T1(c1=str(c1), c2='5').send()
        update_result = T1.c2.eq('5').update({'c2': '6'}, atomic=True).run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', T1.all().run())
        ))

    def test_base_file_interaction(self):
        file_content = 'asdfaasdfasdfhvasdjfbasdf'
        file_name = 'test_file'
        file_content2 = 'reeetssd'
        file_name2 = 'test_file2'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        c1.send()
        c11: ModelWithFile = ModelWithFile.get(c1.id)
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content)
        c1.cute_file1 = files.FileRecord(file_name2, content=file_content2)
        c1.send()
        c11.load()
        self.assertEqual(c11.cute_file1.name, file_name2)
        self.assertEqual(c11.cute_file1.content, file_content2)
        c11.send()

    def test_internal_file_interaction(self):
        file_content = 'asdfaasdfasdfhvasdjfbasdf'
        file_content2 = 'ssdfsdufysgaerktertfecgfgdghft'
        file_name = 'test_file'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        c1.send()
        c1.cute_file1.content = file_content2
        c1.send()
        c11: ModelWithFile = ModelWithFile.get(c1.id)
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content2)

    def test_bytes_file_usage(self):
        file_content = bytes([1, 2, 4, 5, 6, 6])
        file_name = 'test_file'
        file_content2 = bytes([6, 6, 6, 6, 6, 6])
        file_name2 = 'test_file2'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        c1.send()
        c11: ModelWithFile = ModelWithFile.get(c1.id)
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content)
        c1.cute_file1 = files.FileRecord(file_name2, content=file_content2)
        c1.send()
        c11.load()
        self.assertEqual(c11.cute_file1.name, file_name2)
        self.assertEqual(c11.cute_file1.content, file_content2)
        c11.send()

    def test_base_file_dict_interaction(self):
        file_dict = {
            'first_file': files.FileRecord('first_file-01', 'huavsdfvasdfvasdhgfvasdf'),
            'second_file': files.FileRecord('second_file-01', 'aaaaaa'),
            'to_del_file': files.FileRecord('to-del-file', 'ytytythbTT!'),
        }
        c1 = ModelWithFileDict(cute_files=file_dict)
        c1.send()
        c11: ModelWithFileDict = ModelWithFileDict.get(c1.id)
        self.assertEqual(len(c11.cute_files), 3)
        for file_key in file_dict:
            self.assertEqual(c11.cute_files[file_key].name, file_dict[file_key].name)
            self.assertEqual(c11.cute_files[file_key].content, file_dict[file_key].content)
        c1.cute_files['first_file'].content = 'yeyeyeyeyeyeyeye'
        c1.cute_files['second_file'] = files.FileRecord('second_file_02', 'htgtgtgtgt')
        del c1.cute_files['to_del_file']
        c1.cute_files['third_file'] = files.FileRecord('third_file_01', 'yyyyyyy')
        c1.send()
        c11.load()
        self.assertEqual(len(c11.cute_files), 3)
        self.assertEqual(c11.cute_files['first_file'].content, 'yeyeyeyeyeyeyeye')
        self.assertEqual(c11.cute_files['second_file'].name, 'second_file_02')
        self.assertEqual(c11.cute_files['second_file'].content, 'htgtgtgtgt')
        self.assertEqual(c11.cute_files['third_file'].name, 'third_file_01')
        self.assertEqual(c11.cute_files['third_file'].content, 'yyyyyyy')
        self.assertFalse('to_del_file' in c11.cute_files)
        c11.send()


class AsyncTestSkeleton(asynctest.TestCase):

    @classmethod
    def generate_connection_uri(cls):
        return None, {}

    @classmethod
    def extensions(cls):
        return {}

    @classmethod
    def setUpClass(cls):
        connection_uri, pool_kwargs = cls.generate_connection_uri()
        extensions = cls.extensions()
        if connection_uri is None:
            raise unittest.SkipTest("Skip abstract class")
        purge_query_row_cache(T1, AbstractModel, T2)
        orm_register.init(connection_uri, pool_kwargs, async_mode=True, extensions=extensions)

    async def setUp(self):
        await orm_register.async_load()
        await asyncio.gather(
            orm_register.async_strategy.truncate_table(T1._table),
            orm_register.async_strategy.truncate_table(T2._table),
            orm_register.async_strategy.truncate_table(AbstractModel._table),
            orm_register.async_strategy.truncate_table(ModelWithFile._table),
            orm_register.async_strategy.truncate_table(ModelWithFileDict._table)
        )

    @classmethod
    def tearDownClass(cls):
        asyncio.get_event_loop().run_until_complete(orm_register.async_close())

    async def test_get(self):
        t1 = T1(c1='5')
        await t1.async_send()
        t1_1 = await T1.async_get(t1.id)
        self.assertEqual(t1.c1, t1_1.c1)

    async def test_base_interaction(self):
        t1 = T1(c1='5', c2='6')
        t2 = T1(c1='6', c2='7')
        await asyncio.gather(t1.async_send(), t2.async_send())
        t1_list = await T1.all().async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_simple_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = list(await (T1.c1 > '5').async_run())
        self.assertEqual(count(t1_list), 4)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_child_search(self):
        next1 = asyncio.gather(*[Next1Model(c1=str(c1)).async_send() for c1 in range(0, 5)])
        next2 = asyncio.gather(*[Next2Model(c1=str(c1)).async_send() for c1 in range(0, 5)])
        await asyncio.gather(next1, next2)
        self.assertEqual(await Next1Model.all().count().async_run(), 5)
        self.assertEqual(await Next2Model.all().count().async_run(), 5)
        self.assertEqual(await AbstractModel.all().count().async_run(), 10)

    async def test_related(self):
        t1 = T1(c1='5')
        await t1.async_send()
        t2 = T2(t1=t1.id)
        await t2.async_send()
        new_t2 = await T2.all().async_first(ensure_related=True)
        self.assertEqual(new_t2.t1.id, t1.id)

    async def test_list_related(self):
        t11 = T1(c1='5')
        t12 = T1(c1='6')
        await asyncio.gather(
            t12.async_send(),
            t11.async_send()
        )
        t2 = T2()
        t2.t2.append(t11)
        t2.t2.append(t12.id)
        await t2.async_send()
        new_t2 = await T2.all().async_first(ensure_related=True)
        self.assertEqual(len(new_t2.t2), 2)
        self.assertEqual(new_t2.t2[0].id, t11.id)
        self.assertEqual(new_t2.t2[1].id, t12.id)

    async def test_list_related_setter(self):
        t11 = T1(c1='5')
        t12 = T1(c1='6')
        await asyncio.gather(
            t12.async_send(),
            t11.async_send()
        )
        t2 = T2(t2=[t11, t12.id])
        await t2.async_send()
        new_t2 = await T2.all().async_first(ensure_related=True)
        self.assertEqual(len(new_t2.t2), 2)
        self.assertEqual(new_t2.t2[0].id, t11.id)
        self.assertEqual(new_t2.t2[1].id, t12.id)

    async def test_child_sorting_and_filter(self):
        await asyncio.wait([Next1Model(c1=str(c1)).async_send() for c1 in range(0, 10)])
        self.assertEqual((await Next1Model.c1.le('5').order_by(Next1Model.c1.amount).async_first()).c1, '0')

    async def test_magic_update(self):
        t1_1 = T1(c1='5', c2='6')
        await t1_1.async_send()
        t1_2 = next(await T1.all().async_run())
        t1_2.c2 = '7'
        await t1_2.async_send()
        await t1_1.async_load()
        self.assertEqual(t1_1.c2, '7')

    async def test_datetime(self):
        test_datetime = datetime.utcnow() + timedelta(minutes=5)
        t1_original = T1(c3=test_datetime)
        await t1_original.async_send()
        t1_1 = next(await T1.all().async_run())
        self.assertEqual(t1_1.c3, t1_original.c3)
        t1_2 = next(await (T1.c3 == test_datetime).async_run())
        self.assertEqual(t1_2.c3, t1_original.c3)

    async def test_complex_search(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 10)])
        t1_list = list(await ((T1.c1 > '5') & (T1.c1 < '8')).async_run())
        self.assertEqual(count(t1_list), 2)
        for t1 in t1_list:
            self.assertEqual(t1.c2, '5')

    async def test_sorting(self):
        await asyncio.wait([
            T1(c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 3) for c2 in range(0, 3)
        ])
        t1_list = await T1.all().order_by(T1.c1.amount.desc, T1.c2.amount.desc).async_run()
        t1_el = next(t1_list)
        self.assertEqual(t1_el.c1, '2')
        self.assertEqual(t1_el.c2, '2')

    async def test_nested_queries(self):
        t1 = T1(c4={"c2": 5})
        await t1.async_send()
        t1_search = next(await (T1.c4.c2 == 5).async_run())
        self.assertEqual(t1.c4, t1_search.c4)

    async def test_complex_nested_queries(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        t1_list = await ((T1.c4.c1 > 2) & (T1.c4.c2 < 3)).async_run()
        self.assertEqual(count(t1_list), 6)

    async def test_internval_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await ((T1.c4.c1 < 4) & (T1.c4.c1 > 1)).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_in_nested_queries(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await (T1.c4.c1.one_of(1, 2)).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_sample(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        t1_list = await T1.all().sample(2).async_run()
        self.assertEqual(count(t1_list), 2)

    async def test_base_aggregation(self):
        await asyncio.wait([T1(c1='v' + str(c1)).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c1).async_run(), 'v4')

    async def test_nested_aggregation(self):
        await asyncio.wait([T1(c4={"c1": c1}).async_send() for c1 in range(0, 5)])
        self.assertEqual(await T1.all().max(T1.c4.c1).async_run(), 4)

    async def test_complicated_aggregation(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        self.assertEqual(await (T1.c4.c1 > T1.c4.c2).count().async_run(), 10)

    async def test_complicated_query(self):
        await asyncio.wait([
            T1(c4={"c1": c1, "c2": c2}).async_send()
            for c1 in range(0, 5) for c2 in range(0, 5)
        ])
        self.assertEqual(count(await (T1.c4.c1 > T1.c4.c2).async_run()), 10)

    async def test_base_match(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}").async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(count(await T1.c5.match('v0').async_run()), 5)

    async def test_match_aggregation(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}").async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await T1.c5.match('v0').count().async_run(), 5)

    async def test_match_complicated(self):
        await asyncio.wait([
            T1(c5=f"v{c2}.{c1}", c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await (T1.c5.match('v0') & (T1.c1 != T1.c2)).count().async_run(), 4)

    async def test_group(self):
        await asyncio.wait([
            T1(c1=str(c1), c2=str(c2)).async_send()
            for c1 in range(0, 5) for c2 in range(0, 2)
        ])
        self.assertEqual(await T1.c1.ne(T1.c2).group(T1.c2).count().async_run(), {'0': 4, '1': 4})

    async def test_changes(self):
        event_list = []

        async def changes_sender(t1_list):
            await asyncio.sleep(2)
            for t1 in t1_list:
                t1.c1 = '2'
                await t1.async_send()
            await asyncio.sleep(2)

        async def changes_aggregator():
            async for event in await T1.c2.eq('1').changes(with_types=True).async_run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2=str(c2))
            for c1 in range(0, 5) for c2 in range(0, 2)
        ]
        await asyncio.wait([t1.async_send() for t1 in t1_list])
        await asyncio.wait([
            changes_sender(t1_list),
            changes_aggregator()
        ], return_when=asyncio.FIRST_COMPLETED)
        self.assertEqual(len(event_list), 5)
        for event in event_list:
            self.assertEqual(event.get('type'), 'change')
            self.assertTrue('doc' in event)

    async def test_complex_changes(self):
        event_list = []

        async def changes_sender(t1_list):
            await asyncio.sleep(2)
            for t1 in t1_list:
                t1.c1 = '-'
                await t1.async_send()
            await asyncio.sleep(2)

        async def changes_aggregator():
            async for event in await T1.c1.le(T1.c2).changes(with_types=True, with_initial=True).async_run():
                event_list.append(event)

        t1_list = [
            T1(c1=str(c1), c2='3')
            for c1 in range(0, 5)
        ]
        await asyncio.wait([t1.async_send() for t1 in t1_list])
        await asyncio.wait([
            changes_sender(t1_list),
            changes_aggregator()
        ], return_when=asyncio.FIRST_COMPLETED)
        self.assertEqual(len(event_list), 9)
        for event in event_list:
            self.assertIn(event.get('type'), ('change', 'add', 'initial'))
            self.assertTrue('doc' in event)

    async def test_update(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 5)])
        update_result = await T1.c2.eq('5').update({'c2': '6'}).async_run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', await T1.all().async_run())
        ))

    async def test_atomic_update(self):
        await asyncio.wait([T1(c1=str(c1), c2='5').async_send() for c1 in range(0, 5)])
        update_result = await T1.c2.eq('5').update({'c2': '6'}, atomic=True).async_run()
        self.assertTrue(isinstance(update_result, dict))
        self.assertEqual(update_result.get('replaced'), 5)
        self.assertEqual(update_result.get('skipped'), 0)
        self.assertTrue(all(
            map(lambda x: x.c2 == '6', await T1.all().async_run())
        ))

    async def test_enum(self):
        t1_1 = T1(c6=X1.t)
        t1_2 = T1(c7=Y1.t)
        await t1_1.async_send()
        await t1_2.async_send()
        t1_1_2 = await T1.c6.eq(X1.t).async_first()
        t1_2_2 = await T1.c7.eq(Y1.t).async_first()
        self.assertEqual(t1_1.id, t1_1_2.id)
        self.assertEqual(t1_2.id, t1_2_2.id)

    async def test_base_file_interaction(self):
        file_content = 'asdfaasdfasdfhvasdjfbasdf'
        file_name = 'test_file'
        file_content2 = 'reeetssd'
        file_name2 = 'test_file2'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        await c1.async_send()
        c11: ModelWithFile = await ModelWithFile.async_get(c1.id)
        await c11.cute_file1.ensure()
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content)
        c1.cute_file1 = files.FileRecord(file_name2, content=file_content2)
        await c1.async_send()
        await c11.async_load()
        await c11.cute_file1.ensure()
        self.assertEqual(c11.cute_file1.name, file_name2)
        self.assertEqual(c11.cute_file1.content, file_content2)

    async def test_internal_file_interaction(self):
        file_content = 'asdfaasdfasdfhvasdjfbasdf'
        file_content2 = 'ssdfsdufysgaerktertfecgfgdghft'
        file_name = 'test_file'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        await c1.async_send()
        c1.cute_file1.content = file_content2
        await c1.async_send()
        c11: ModelWithFile = await ModelWithFile.async_get(c1.id)
        await c11.cute_file1.ensure()
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content2)

    async def test_bytes_file_usage(self):
        file_content = bytes([1, 2, 4, 5, 6, 6])
        file_name = 'test_file'
        file_content2 = bytes([6, 6, 6, 6, 6, 6])
        file_name2 = 'test_file2'
        file_record = files.FileRecord(file_name, content=file_content)
        c1 = ModelWithFile(cute_file1=file_record)
        await c1.async_send()
        c11: ModelWithFile = await ModelWithFile.async_get(c1.id)
        await c11.cute_file1.ensure()
        self.assertEqual(c11.cute_file1.name, file_name)
        self.assertEqual(c11.cute_file1.content, file_content)
        c1.cute_file1 = files.FileRecord(file_name2, content=file_content2)
        await c1.async_send()
        await c11.async_load()
        await c11.cute_file1.ensure()
        self.assertEqual(c11.cute_file1.name, file_name2)
        self.assertEqual(c11.cute_file1.content, file_content2)

    async def test_base_file_dict_interaction(self):
        file_dict = {
            'first_file': files.FileRecord('first_file-01', 'huavsdfvasdfvasdhgfvasdf'),
            'second_file': files.FileRecord('second_file-01', 'aaaaaa'),
            'to_del_file': files.FileRecord('to-del-file', 'ytytythbTT!'),
        }
        c1 = ModelWithFileDict(cute_files=file_dict)
        await c1.async_send()
        c11: ModelWithFileDict = await ModelWithFileDict.async_get(c1.id)
        await c11.cute_files.ensure()
        self.assertEqual(len(c11.cute_files), 3)
        for file_key in file_dict:
            self.assertEqual(c11.cute_files[file_key].name, file_dict[file_key].name)
            self.assertEqual(c11.cute_files[file_key].content, file_dict[file_key].content)
        c1.cute_files['first_file'].content = 'yeyeyeyeyeyeyeye'
        c1.cute_files['second_file'] = files.FileRecord('second_file_02', 'htgtgtgtgt')
        del c1.cute_files['to_del_file']
        c1.cute_files['third_file'] = files.FileRecord('third_file_01', 'yyyyyyy')
        await c1.async_send()
        await c11.async_load()
        await c11.cute_files.ensure()
        self.assertEqual(len(c11.cute_files), 3)
        self.assertEqual(c11.cute_files['first_file'].content, 'yeyeyeyeyeyeyeye')
        self.assertEqual(c11.cute_files['second_file'].name, 'second_file_02')
        self.assertEqual(c11.cute_files['second_file'].content, 'htgtgtgtgt')
        self.assertEqual(c11.cute_files['third_file'].name, 'third_file_01')
        self.assertEqual(c11.cute_files['third_file'].content, 'yyyyyyy')
        self.assertFalse('to_del_file' in c11.cute_files)
        await c11.async_send()
