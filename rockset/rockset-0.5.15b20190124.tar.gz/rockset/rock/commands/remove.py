from .command_auth import AuthCommand


class Remove(AuthCommand):
    def usage(self):
        return """
usage: rock rm [-h] <name> <document_id>...

Remove one or more documents from a Rockset collection.

arguments:
    <name>              name of the collection
    <document_id>       id of the documents you wish to remove from the
                        collection

options:
    -h, --help          show this help message and exit
        """

    def go(self):
        resource = self.client.Collection.retrieve(self.name)
        docs = [{'_id': docid} for docid in self.document_id]
        self.print_list(
            0,
            resource.remove_docs(docs=docs),
            field_order=['collection', 'id', 'status', 'error']
        )
        return 0
