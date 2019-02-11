import re

from django.db import connection

from jsql.connector import JSQLConnector


class JSQLExecutor:
    cursor = connection.cursor()
    connector = JSQLConnector()
    paramsError = False

    def executeSelect(self, request):
        data = self.connector.parseRequestToJSON(request)
        query = self.connector.getSQLQuery(data["token"])
        params = None
        try:
            params = data["params"]
        except:
            pass
        if query["code"] >= 400:
            return {'code': query["code"], 'description': query["data"]}
        result = ""
        try:
            finalQuery = self.substituteParams(query["data"], params)
            if self.paramsError is True or finalQuery.lower().startswith('cannot'):
                self.paramsError = False
                return {'code': 400, 'description': finalQuery}
            if finalQuery.split(' ', 1)[0].lower() != "select":
                return {'code': 400, 'description': 'Only `SELECT` queries allowed in this method!'}
            self.cursor.execute(finalQuery)
            columns = self.cursor.description
            result = [{self.toCamelCase(columns[index][0]): column for index, column in enumerate(value)} for value in
                      self.cursor.fetchall()]
        except Exception as e:
            return {'code': 400, 'description': str(e)}

        return result

    def executeUpdateAndDelete(self, request):
        data = self.connector.parseRequestToJSON(request)
        query = self.connector.getSQLQuery(data["token"])
        params = None
        try:
            params = data["params"]
        except:
            pass
        if query["code"] >= 400:
            return {'code': query["code"], 'description': query["data"]}
        try:
            finalQuery = self.substituteParams(query["data"], params)
            if self.paramsError is True or finalQuery.lower().startswith('cannot'):
                self.paramsError = False
                return {'code': 400, 'description': finalQuery}
            if finalQuery.split(' ', 1)[0].lower() != "update" and finalQuery.split(' ', 1)[0].lower() != "delete":
                return {'code': 400, 'description': 'Only `UPDATE` or `DELETE` queries allowed in this method!'}
            self.cursor.execute(finalQuery)
        except Exception as e:
            return {'code': 400, 'description': str(e)}
        return {'status': 'OK'}

    def executeInsert(self, request):
        dialect = self.connector.retrieveDialect()
        if dialect["code"] != 200:
            return {'code': dialect["code"], 'description': dialect["data"]["description"]}
        data = self.connector.parseRequestToJSON(request)
        query = self.connector.getSQLQuery(data["token"])
        params = None
        try:
            params = data["params"]
        except:
            pass
        if query["code"] >= 400:
            return {'code': query["code"], 'description': query["data"]}
        result = ""
        finalQuery = self.substituteParams(query["data"], params)
        if self.paramsError is True or finalQuery.lower().startswith('cannot'):
            self.paramsError = False
            return {'code': 400, 'description': finalQuery}
        if finalQuery.split(' ', 1)[0].lower() != "insert":
            return {'code': 400, 'description': 'Only `INSERT` queries allowed in this method!'}
        if dialect["data"]["data"]["databaseDialect"] == 'POSTGRES':
            try:
                self.cursor.execute(finalQuery + ' returning id')
                result = self.cursor.fetchall()
            except Exception as e:
                return {'code': 400, 'description': str(e)}
        if dialect["data"]["data"]["databaseDialect"] == 'MYSQL':
            try:
                self.cursor.execute(finalQuery)
                self.cursor.execute('SELECT LAST_INSERT_ID()')
                result = self.cursor.fetchall()
            except Exception as e:
                return {'code': 400, 'description': str(e)}
        return {"lastId": result}

    def toCamelCase(self, key):
        parts = key.split("_")
        camelCaseString = ""
        for i in range(len(parts)):
            if i != 0:
                parts[i] = parts[i][:1].upper() + parts[i][1:].lower()
            camelCaseString += parts[i]
        return camelCaseString

    def substituteParams(self, query, params):
        result = query
        splittedSQL = result
        if params is not None:
            if isinstance(params, dict):
                for key, value in params.items():
                    if isinstance(value, str):
                        result = result.replace(":" + key, "'" + str(value) + "'")
                    else:
                        result = result.replace(":" + key, str(value))
            else:
                for param in params:
                    if isinstance(param, str):
                        result = result.replace('?', "'" + str(param) + "'", 1)
                    else:
                        result = result.replace('?', str(param), 1)
        if isinstance(params, dict):
            splittedSQL = re.findall(r":\w+", result)
            errorMessage = "You have to include these params to your request: "
            for s in splittedSQL:
                if ":" in s and "'" not in s and "\"" not in s and "`" not in s:
                    errorMessage += s
                    self.paramsError = True
        else:
            if result.count("?") > 0:
                errorMessage = "You forgot to pass " + str(result.count("?")) + " parameters"
                self.paramsError = True
        if self.paramsError is True:
            return errorMessage
        return result
