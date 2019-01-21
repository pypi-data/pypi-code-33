from .command_auth import AuthCommand
from rockset import Q, F

class Get(AuthCommand):
    def usage(self):
        return """
usage: rock get [-h] <name> <document_id>...

Fetch one or more documents as JSON from a Rockset collection.

arguments:
    <name>              name of the collection
    <document_id>       id of the documents you wish to fetch from the
                        collection

options:
    -h, --help          show this help message and exit
        """

    def go(self):
        q = Q.none
        for doc_id in self.document_id:
            q |= F["_id"] == doc_id
        c = self.client.retrieve(self.name)
        self.print_list(0, c.query(q).results())
        return 0
