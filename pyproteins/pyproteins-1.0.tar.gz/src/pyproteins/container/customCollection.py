import os

'''
GL 2015-07-08 Givin up trying to adpat this module to Peptides
 May come back to it later,if Peptide usage is needed on a long term
indexer arguments supply a indexing function to be called for each objects
    -->(typically setting object accessors key based on their fileName)
cIndexer arguments supply a common indexing function to be called once for the entiere collection
    --> eg: Read from a single catalogue file the mapping between object accessors and their fileName
'''
class EntrySet(object):
    def __init__(self, collectionPath=None, constructor=None, typeCheck=None, indexer=None, cIndexer=None):

        if not collectionPath:
            raise ValueError("You must specify a filesystem path to local cache")
        if not constructor:
            raise ValueError("You must bind an object constructor at cache invocation")
        if not indexer and not cIndexer:
            raise ValueError("You must specify an indexer function to map filename <-> collection key")

        self.typeCheck = typeCheck
        self.constructor = constructor
        self.indexer = indexer

        self.root = collectionPath
        self.data = {}
        # Try to index files
        self._index()

# Change cache location, re-index
    def setCache(self, location=None, reIndex=True):
        self.root = location
        print ("Changing cache location to " + self.root)
        if reIndex:
            print ("Reindexing " + self.root)
            self._index()

    def _index(self):
        for fileName in os.listdir(self.root): # lazy initialization of objects
            id = self.indexer(fileName)
            if id:
                self.data[id] = { 'updated' : False, 'location' : self.root + '/' + fileName, 'e' : None }  #Entry(id,fileName = self.root + '/' + fileName
        print ("Acknowledged " + str(len(self.data)) + " entries (" +  self.root + ")")

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for k,d in self.data.items():
            yield d

    def __repr__(self):
        string = "Cache pool size " + str(len(self)) + '\n'
        for k,d in self.data.items():
            if not k or not d:
                raise TypeError('Error here ::-> ' + str(k) + ' // ' + str(d) )
            status = "LOADED" if d['e'] else "LAZY"
            string += str(k) + '\t' + str(status) + "\n"
        return string

    def add(self, id, force=False):
        if not isinstance(id, str):
            for i in id:
                if not force and i in self.data:
    #                print str(i) + ' already part of collection'
                    continue
                self.data[i] = { 'updated' : True, 'location' : None, 'e' : self.constructor(i) } # Newly added object dont have location
        else :
            if not force and id in self.data:
    #            print str(i) + ' already part of collection'
                return
            self.data[id] = { 'updated' : True, 'location' : None, 'e' : self.constructor(id) } # Newly added object dont have location

    def clear(self):
        n=len(self.data)
        id=[ k for k in self.data ]
        for k in id:
            self.delete(k)
        print ("All " + str(n) + " entries deleted!")

    def delete(self, id):
        if os.path.isfile(self.data[id]['location']):
            os.remove(self.data[id]['location'])
        self.data.pop(id, None)

    def get(self, id, reload=False):
        if self.typeCheck:
            if not self.typeCheck(id):
                raise TypeError("invalid supplied identifier \"" + id + "\"")

        if id in self.data and reload:
            print ("Erasing prev ref")
            self.delete(id)
        # Present but lazy initialized
        if id in self.data and not self.data[id]['e'] and self.data[id]['location']:
            self.data[id]['e'] = self.constructor(id, fileName = self.data[id]['location'])
            self.data[id]['updated'] = True
        # Not present
        if not id in self.data:
            self.add(id)


        return self.data[id]['e']

    def serialize(self, force=False):
        c = 0
        t = 0
        for d in self:
            t += 1

            if not d['e']: # LAZY instantiated object, we skip it
                continue

            if d['updated'] or force:
                if d['e']:
                    d['location'] = self.root + '/' + d['e'].id + '.xml' if not d['location'] else d['location']

                mode = "wb"
                try:
                    data = d['e'].serialize().decode()
                    print(d['e'].id + ' has byte content')
                except AttributeError:
                    print(d['e'].id + ' has non byte content')
                    #print(d['e'].serialize())
                    mode = "w"

                with open(d['location'], mode) as textFile:
                    textFile.write(d['e'].serialize())
                c +=1
                d['updated'] = False
        print (str(c) + " entries updated, total pool is " + str(t))
