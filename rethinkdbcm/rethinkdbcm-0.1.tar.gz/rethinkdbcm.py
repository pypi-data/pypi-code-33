import rethinkdb as db
from rethinkdb.errors import ReqlOpFailedError


class UseDatabase:
    def __init__(self, config: dict, db=None) -> None:
        self.config = config
        self.config['db'] = db

    def __enter__(self):
        """Подключение к базе данных RethinkDB"""
        self.conn = db.connect(**self.config).repl()
        return self

    def all_db(self):
        """Получение всех баз данных"""
        try:
            return db.db_list().run()
        except ReqlOpFailedError:
            return {self.config['db']: 'does not exist'}

    def create_db(self, name):
        """Создание новой базы данных"""
        try:
            return db.db_create(name).run()
        except ReqlOpFailedError:
            return {name: 'the database is already there'}

    def del_db(self, name):
        """Удаление базы данных"""
        try:
            return db.db_drop(name).run()
        except ReqlOpFailedError:
            return {name: 'database not found'}

    def all_table(self, name_db):
        """Получение всех таблиц из подключенной БД"""
        try:
            t = db.table_list().run(self.conn)
            if not t:  # Если таблиц нет
                t = {'table in DB ' + name_db: 'not found'}
            return t
        except ReqlOpFailedError:
            return {'DB ' + name_db: 'does not exist'}

    def create_tab(self, name_db, name_t):
        """Создание новой таблицы в базе данных"""
        try:
            return db.db(name_db).table_create(name_t).run()
        except ReqlOpFailedError:
            return {name_t + ' in DB ' + name_db: 'the table already exists'}

    def del_tab(self, name_db, name_t):
        """Удаление таблицы из базы данных"""
        try:
            return db.db(name_db).table_drop(name_t).run()
        except ReqlOpFailedError:
            return {name_t + ' in DB ' + name_db: 'the table does not exist'}

    def insert(self, name_t, json):
        """Добавление новой записи в таблицу БД"""
        try:
            return db.table(name_t).insert(json).run()
        except ReqlOpFailedError:
            return {name_t: 'the table does not exist'}

    def countid(self, name_t, id_name, req):
        """Определение записи в таблице БД по определнному ID
        0 - записи нет, 1 - запись имеется"""
        return db.table(name_t).filter({id_name: req}).count().run()

    def gettasks(self, name_t):
        """Получение всех записей из таблицы базы данных"""
        try:
            return list(db.table(name_t).run())
        except (ReqlOpFailedError, IndexError):
            return None

    def getroot(self, name_t):
        """Получение записи только из первой таблицы (root) базы данных"""
        # Метод является частным случаем
        try:
            return list(db.table(name_t).run())[0]
        except (ReqlOpFailedError, IndexError):
            return None

    def gettask(self, name_t, req):
        """Получение записей из таблицы базы данных по определенному ID"""
        return db.table(name_t).get(req).run()

    def updetask(self, name_t, id_name, json):
        """Обновление записи в таблице БД по определнному ID"""
        return db.table(name_t).get(id_name).update(json).run()

    def delltask(self, name_t, id_name):
        """Удаление записи в таблице БД по определнному ID"""
        return db.table(name_t).get(id_name).delete().run()

    def getval(self, name_t, id_name):
        """Получение значений, без ключей из таблицы БД по определенному ID"""
        return list(db.table(name_t).get(id_name).values().run())

    def countall(self, name_t):
        """Определение количества записи в таблице БД"""
        return db.table(name_t).count().run()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Отключение от БД"""
        self.conn.close()
