from Rmysql import Rmysql

# db = Rmysql('0.0.0.0', 'test', 'root', 'root', 3307)
# db.set("INSERT INTO pet (name, owner, species, sex) VALUES(%s, %s, %s, %s)", ('Rex', 'Alex', 'dogger', 1)) 
#  
# print(db.get("SELECT name FROM pet"))  
 

from Rsqlite import Rsqlite
# import os
# dir_path = os.path.dirname(os.path.realpath(__file__))

# db = Rsqlite('lend.db', path=dir_path+'/') 
# db.set('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(40), age INT)') 
# db.set("INSERT INTO users (name, age) VALUES(?, ?)", [('Alex', 22), ('Peter', 55)]) 
# db.set("INSERT INTO users (name) VALUES(?)", [('Alex',)]) 
# db.set("INSERT INTO users (name,age) VALUES('Joan', 30)", ) 

# print(db.get("SELECT * FROM users WHERE age < 25"))
# print(db.get("SELECT * FROM users WHERE age > ? AND name = ?", ('25', 'Joan') ))


from Rpostgres import Rpostgres
# db = Rpostgres('0.0.0.0', 'test', 'root', 'root', 5432)
# db = db.set("INSERT INTO users (id, name) VALUES(1, 'Alex')" )
# db = db.set("INSERT INTO users (id, name) VALUES(%s, %s)", (2, 'Joan'))
# print(db.get("SELECT * FROM users WHERE id > %s", ('1')))  