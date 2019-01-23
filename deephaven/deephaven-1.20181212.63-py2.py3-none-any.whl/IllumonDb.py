#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#

import jpy
import logging
import random

from .java_to_python import frozen_table_to_df
from .python_to_java import df_to_table


class IllumonDb:
    """
    IllumonDb session.
    """

    def __init__(self):
        """Create a new Iris session."""
        DbGroovySession = jpy.get_type('com.illumon.integrations.common.IrisIntegrationGroovySession')
        self.session = DbGroovySession("Python Session", True)

    def reconnect(self):
        """Disconnect and then reconnect the session.  Iris state will be lost."""
        DbGroovySession = jpy.get_type('com.illumon.integrations.common.IrisIntegrationGroovySession')
        self.session.getDb().shutdown()
        self.session = DbGroovySession("Python Session", True)

    def db(self):
        """Gets an Iris database object."""
        return self.session.getDb()

    def execute(self, groovy):
        """Execute Iris groovy code."""
        self.session.execute(groovy)

    def executeFile(self, file):
        """Execute Iris groovy code contained in a file."""
        self.session.executeFile(file)

    def get(self, variable):
        """Gets a variable from the groovy session.

        variable -- variable name
        """
        return self.session.getVariable(variable)

    def __getitem__(self, variable):
        """Gets a variable from the groovy session.

        variable -- variable name
        """
        return self.get(variable)

    def get_df(self, variable):
        """Gets a Pandas dataframe from the groovy session.

        variable -- variable name
        """
        try:
            xrange
        except NameError:
            xrange = range

        x = random.sample(xrange(100), 3)
        table_name = "__FROZEN_TABLE%s%s%s" % (x[0], x[1], x[2])
        self.execute("%s = %s.isLive() ? db.makeRemote(emptyTable(0)).snapshot(%s,true) : %s" % (
            table_name, variable, variable, variable))
        t = self.get(table_name)
        self.execute('%s = null' % table_name)
        self.execute("""binding.variables.remove '%s'""" % table_name)

        return frozen_table_to_df(t)

    def push_df(self, name, df):
        """Pushes a Pandas dataframe to the Iris groovy session.

        name -- variable name for the dataframe in the groovy session
        df -- Pandas dataframe
        """

        logging.info("Dataframe %s push..." % name)
        t = df_to_table(df)
        self.session.publishTable(name, t)
        logging.info("...Dataframe %s push done." % name)
