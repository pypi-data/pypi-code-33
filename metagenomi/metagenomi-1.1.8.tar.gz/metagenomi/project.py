from boto3.dynamodb.conditions import Key, Attr


from metagenomi.db import (dbconn, testdb)


class MgProject:
    '''
    A representation of a lot of MgObjects
    '''

    def __init__(self, project, db=testdb):
        self.db = db
        self.project = project
        self.reads = []
        self.assemblies = []
        self.samples = []
        self.association_map = {}

        self.response = self.scan()

        # items = self.query(filter_key='mg-identifier',
        #                      filter_value=self.project,
        #                      comparison='contains')
        #
        # for i in items:
        #     mg_identifier = i['mg-identifier']
        #     if any(x in mg_identifier  for x in ['-read', '-tran']):
        #         self.reads.append(MgRead(i))
        #     elif '-assm' in mg_identifier :
        #         self.assemblies.append(MgAssembly(i))
        #     elif '-samp' in mg_identifier :
        #         self.samples.append(MgSample(i))
        #     else:
        #         raise ValueError(f'object with id {mg_identifier} could not be assigned a type')
        #
        # self.derive_associations()


    def query(self, index='project-mg_type-index'):
        """
        """

        response = self.db.table.query(
            IndexName='mgproject_index',
            KeyConditionExpression=Key('mgproject').eq('HYDR')
            # ExpressionAttributeValues={
            #     ':project': {
            #         'S': 'HYDR',
            #         },
            # },
            # KeyConditionExpression='project = :HYDR',
            )

        print(response)

    def scan(self, filter_key=None, filter_value=None, comparison='equals'):
        """
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
                    ExclusiveStartKey=response['LastEvaluatedKey']
                    )
                items += response['Items']
            else:
                break

        return items

        # response = self.db.table.scan(
        #     IndexName='mgproject_index',
        #     KeyConditionExpression=Key('mgproject').eq('HYDR')
        #     # ExpressionAttributeValues={
        #     #     ':project': {
        #     #         'S': 'HYDR',
        #     #         },
        #     # },
        #     # KeyConditionExpression='project = :HYDR',
        #     )
        #
        # print(response)
#
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
#     def derive_associations(self):
#         for assembly in self.assemblies:
#             associated = assembly.getAssociated()
#             for k,v in associated.items():
#                 for v1 in v:
#                     connection =self.getObjectFromID(v1)
#                     if assembly in self.association_map:
#                         self.association_map[assembly] = self.association_map[assembly] + [connection]
#                     else:
#                         self.association_map[assembly] = [connection]
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
#     def getObjectFromID(self, mg_identifier):
#         if isinstance(mg_identifier, MgObj):
#             return mg_identifier
#
#         if any(x in mg_identifier  for x in ['-read', '-tran']):
#             for r in self.reads:
#                 if r.getMgID() == mg_identifier:
#                     return r
#
#         elif '-assm' in mg_identifier :
#             for a in self.assemblies:
#                 if a.getMgID() == mg_identifier:
#                     return a
#
#         elif '-samp' in mg_identifier :
#             for s in self.samples:
#                 if s.getMgID() == mg_identifier:
#                     return s
#
#         else:
#             raise ValueError(f'object with id {mg_identifier} could not be assigned a type')
