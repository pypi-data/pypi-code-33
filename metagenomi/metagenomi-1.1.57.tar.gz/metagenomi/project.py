from boto3.dynamodb.conditions import Key, Attr


from metagenomi.db import dbconn
from metagenomi.models.assembly import Assembly
from metagenomi.models.sequencing import Sequencing
from metagenomi.models.sample import Sample
from metagenomi.base import MgObj
import time


class MgProject:
    '''
    A representation of a lot of MgObjects
    '''

    def __init__(self, mgproject, type=None, db=dbconn, check=True):

        self.db = db
        self.check = check

        # self.items = self.query(self.mgproject)
        self.mgproject = mgproject

        self.assemblies = None
        self.samples = None
        self.sequencings = None


    def get_assemblies(self):
        '''
        Extremeley slow loading of the ORM objects
        '''
        items = self.query(self.mgproject, filtervalue='assembly')
        self.assemblies = [Assembly(db=self.db, check=self.check, **i) for i in items]

        # items = items[:2]
        #
        # start = time.time()
        # print("hello")
        # # a = Assembly(**items[0], db=self.db, check=False)
        # # print(a.created)
        # self.assemblies = []
        # for i in items:
        #     self.assemblies.append(Assembly)
        #
        # self.assemblies = [Assembly(db=self.db, check=self.check, **i) for i in items]
        # end = time.time()
        # print(end - start)

    def get_samples(self):
        items = self.query(self.mgproject, filtervalue='sample')
        self.samples = [Sample(db=self.db, check=self.check, **i) for i in items]

    def get_sequencings(self):
        items = self.query(self.mgproject, filtervalue='sequencing')
        self.sequencings = [Sequencing(db=self.db, check=self.check, **i) for i in items]

        # self.derive_associations()

    # def load_assemblies(self):
    #     items = self.query(self.mgproject)
    #     return [Assembly(db=db, check=check, **i) for i in items
    #                       if i['mgtype'] == 'assembly']
    #
    # def load_sequencings(self):
    #     return [Sequencing(db=db, check=check, **i) for i in self.items
    #                         if i['mgtype'] == 'sequencing']
    #
    # def load_samples(self):
    #     return [Sample(db=db, check=check, **i) for i in self.items
    #                     if i['mgtype'] == 'sample']

    def query(self, value, index='mgproject-mgtype-index', key='mgproject',
              filterkey='mgtype', filtervalue=None):
        """
        testing filter expressions
        """

        if filtervalue is not None:
            response = self.db.table.query(
                IndexName=index,
                KeyConditionExpression=Key(key).eq(value) & Key(filterkey).eq(filtervalue)
                )

            items = response['Items']
            while True:

                if response.get('LastEvaluatedKey'):
                    response = self.db.table.query(
                        IndexName=index,
                        KeyConditionExpression=Key(key).eq(value) & Key(filterkey).eq(filtervalue),
                        ExclusiveStartKey=response['LastEvaluatedKey']
                        )
                    items += response['Items']
                    print(f'found {len(items)} items')
                else:
                    break

            return items

        #
        # else:
        #     response = self.db.table.query(
        #         IndexName=index,
        #         KeyConditionExpression=Key(key).eq(value)
        #         )
        #
        #     items = response['Items']
        #     while True:
        #         if response.get('LastEvaluatedKey'):
        #             response = self.db.table.query(
        #                 IndexName=index,
        #                 KeyConditionExpression=Key(key).eq(value),
        #                 ExclusiveStartKey=response['LastEvaluatedKey']
        #                 )
        #             items += response['Items']
        #         else:
        #             break
        #     return items

    # def query(self, value, index='mgproject-mgtype-index', key='mgproject'):
    #     """
    #     Queries the database given a value, index, and key.
    #     First selects the index, and then returns all items (in a pageinated
    #     fasion where Key(key).eq(value).
    #     """
    #
    #     response = self.db.table.query(
    #         IndexName=index,
    #         KeyConditionExpression=Key('mgproject').eq(self.mgproject)
    #         )
    #
    #     items = response['Items']
    #     while True:
    #         if response.get('LastEvaluatedKey'):
    #             response = self.db.table.query(
    #                 IndexName=index,
    #                 KeyConditionExpression=Key('mgproject').eq(self.mgproject),
    #                 ExclusiveStartKey=response['LastEvaluatedKey']
    #                 )
    #             items += response['Items']
    #         else:
    #             break
    #
    #     return items

    def scan(self, filter_key=None, filter_value=None, comparison='equals'):
        """
        not currently in use
        """

        if filter_key and filter_value:
            if comparison == 'equals':
                filtering_exp = Key(filter_key).eq(filter_value)
            elif comparison == 'contains':
                filtering_exp = Attr(filter_key).contains(filter_value)

            response = self.db.table.scan(
                FilterExpression=filtering_exp)

        else:
            response = self.db.table.scan()

        items = response['Items']
        while True:
            print(len(response['Items']))
            if response.get('LastEvaluatedKey'):
                response = self.db.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=filtering_exp
                    )
                items += response['Items']
            else:
                break

        return items

    def derive_associations(self):
        '''

        '''
        for mgobj in self.assemblies + self.samples + self.sequencings:
            for type, mgobj_list in mgobj.associated.items():
                for o in mgobj_list:
                    if not o == 'None':
                        connection = self.find_mgobj(o)
                        if mgobj in self.association_map:
                            self.association_map[
                                mgobj
                                ] = self.association_map[mgobj] + [connection]
                        else:
                            self.association_map[mgobj] = [connection]

    def find_mgobj(self, o):
        '''
        Given the mgid of an object, return the instance of that object.
        TODO: Test speed of this function
        '''
        if isinstance(o, MgObj):
            return o

        for i in self.assemblies + self.samples + self.sequencings:
            if i.mgid == o:
                return i

        raise ValueError(f'Object {o} is not in this project')


# )
#
#         if filter_key and filter_value:
#             if comparison == 'equals':
#                 filtering_exp = Key(filter_key).eq(filter_value)
#             elif comparison == 'contains':
#                 filtering_exp = Attr(filter_key).contains(filter_value)
#
#             response = table.scan(
#                 FilterExpression=filtering_exp)
#
#         else:
#             response = table.scan()
#
#         items = response['Items']
#         while True:
#             # print(len(response['Items']))
#             if response.get('LastEvaluatedKey'):
#                 response = table.scan(
#                     ExclusiveStartKey=response['LastEvaluatedKey']
#                     )
#                 items += response['Items']
#             else:
#                 break
#
#         return items
#
#     def getRelatedAssemblies(self, sampleName=None):
#         related = []
#         if sampleName:
#             for assembly in self.assemblies:
#                 if sampleName in assembly.getMgID():
#                     related.append(assembly)
#         return related
#
#
#
#     def getAssociatedReads(self, mg_identifier):
#         query = self.getObjectFromID(mg_identifier)
#
#         if isinstance(query, MgObj):
#             associations = []
#             samples = self.getAssociatedSamples(query)
#             for s in samples:
#                 associations = associations + self.getReads(s)
#             return associations
#
#         else:
#             raise ValueError('f{mg_identifier} is not an object or mg-identifier ')
#
#
#     def getReads(self, mg_identifier):
#         query = self.getObjectFromID(mg_identifier)
#
#         if isinstance(query, MgAssembly) or isinstance(query, MgSample):
#             return(self.association_map[query])
#
#         else:
#             raise ValueError('f{mg_identifier} is not a sample or an assembly ')
#
#
#     def getAssociatedSamples(self, mg_identifier):
#         # if isinstance(mg_identifier, str):
#         query = self.getObjectFromID(mg_identifier)
#         # print(query)
#         # else:
#         #     query = mg_identifier
#         associated_samples = []
#         if isinstance(query, MgRead):
#             for v in self.association_map[query]:
#                 if v.type == 'sample':
#                     associated_samples.append(v)
#             return associated_samples
#
#         # If it is an assembly, first get associated reads
#         elif isinstance(query, MgAssembly):
#             reads = self.getReads(query)
#             for r in reads:
#                 # And then return samples associated with each read
#                 for v in self.association_map[r]:
#                     if v.type == 'sample':
#                         associated_samples.append(v)
#             return associated_samples
#
#         # if it is a sample, return itself.
#         elif isinstance(query, MgSample):
#             print('Warning: Cannot find samples associated because query is sample')
#             return [query]
#         else:
#             raise ValueError('f{mg_identifier} is not an assembly object or id')
#
#
#     def printAssociationMap(self):
#         # Print in longform the association map
#         for k,v in self.association_map.items():
#             print(f'{k.getMgID()} : ')
#             for v1 in v:
#                 print(f'\t{v1.getMgID()}')
#
#
#     def getAssociationMapIDs(self):
#         # Return dictionary of associations with only mg-identifiers
#         d = {}
#         for k,v in self.association_map.items():
#             d[k.getMgID()] = []
#             for v1 in v:
#                 d[k.getMgID()] = d[k.getMgID()] + [v1.getMgID()]
#         return(d)
#
#
#     def getAssociationMapMD(self):
#         # Return dictionary of associations with metadata
#         d = {}
#         for k,v in self.association_map.items():
#             d[k.getMetadata()] = []
#             for v1 in v:
#                 d[k.getMetadata()] = d[k.getMetadata()] + [v1.getMetadata()]
#         return(d)
#
#     def getAssociationMap(self):
#         return(self.association_map)
#

#
#         for read in self.reads:
#             associated = read.getAssociated()
#             for k,v in associated.items():
#                 for v1 in v:
#                     connection =self.getObjectFromID(v1)
#                     if read in self.association_map:
#                         self.association_map[read] = self.association_map[read] + [connection]
#                     else:
#                         self.association_map[read] = [connection]
#
#         for sample in self.samples:
#             associated = sample.getAssociated()
#             for k,v in associated.items():
#                 for v1 in v:
#                     connection =self.getObjectFromID(v1)
#                     if sample in self.association_map:
#                         self.association_map[sample] = self.association_map[sample] + [connection]
#                     else:
#                         self.association_map[sample] = [connection]
#
#
