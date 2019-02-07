from cubicweb_celery import app


@app.cwtask(name='newgroup')
def newgroup(self, name, user_eid=None):
    with self.cnx(user_eid) as cnx:
        if name == u'magic':
            raise ValueError('Cannot add a magic group')
        entity = cnx.create_entity('CWGroup', name=name).eid
        return entity
