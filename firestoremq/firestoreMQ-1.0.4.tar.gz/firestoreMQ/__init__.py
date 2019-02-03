import datetime
import google.api_core.exceptions
import time
from firebase_admin import firestore
import json
import pytz


'''
TODO TTL
'''

def delete_collection(coll_ref, batch_size=100):
    docs = coll_ref.limit(10).get()
    deleted = 0

    for doc in docs:
        print(u'Deleting doc {} => {}'.format(doc.id, doc.to_dict()))
        doc.reference.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

class Queue:
    errored_collection = 'errored'
    assigned_collection = 'assigned'
    unassigned_collection = 'unassigned'

    def __init__(self, id):
        self.id = id
        self.ref = None

    def status(self, db):
        self.ref = db.collection('queues').document(self.id)
        unassigned_docs = self.ref.collection(Queue.unassigned_collection).get()
        assigned_docs = self.ref.collection(Queue.assigned_collection).get()
        errored_docs = self.ref.collection(Queue.errored_collection).get()

        print('tasks: %i, errors: %i' % (len(list(unassigned_docs)), len(list(errored_docs))))
        for doc in assigned_docs:
            print('Task %s being processed by worker %s' % (doc.id, doc.to_dict()['assigned_to']))

    def create(self, db):
        self.ref = db.collection('queues').document(self.id)
        self.ref.set({'created_at': datetime.datetime.now(pytz.UTC)})

    def dump(self, db):
        self.ref = db.collection('queues').document(self.id)

        out = {
            'unassigned': {},
            'assigned': {},
            'errored': {},
        }

        unassigned_docs = self.ref.collection(Queue.unassigned_collection).get()
        for doc in unassigned_docs: out['unassigned'][doc.id] = doc.to_dict()

        assigned_docs = self.ref.collection(Queue.assigned_collection).get()
        for doc in assigned_docs: out['assigned'][doc.id] = doc.to_dict()

        errored_docs = self.ref.collection(Queue.errored_collection).get()
        for doc in errored_docs: out['errored'][doc.id] = doc.to_dict()

        def default(o):
            if isinstance(o, (datetime.date, datetime.datetime)):
                return o.isoformat()

        return json.dumps(out, indent=2, sort_keys=True, default=default)

    '''Check for stuck jobs (i.e. worker died), wait 30 seconds after TTL before requeue'''
    def expire_ttl(self, db, margin_seconds=30):
        expire_time = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=margin_seconds)
        task_docs = db.collection('queues').document(self.id).collection(Queue.assigned_collection).where('ttl', '<', datetime.datetime.now(pytz.UTC)).get()
        for task_doc in task_docs:
            task = Task.from_doc(self.id, task_doc)
            task.requeue(db)
            print('Task %s task expired, requeueing' % task.id)

    def delete(self, db):
        self.ref = db.collection('queues').document(self.id)
        delete_collection(self.ref.collection(Queue.unassigned_collection))
        delete_collection(self.ref.collection(Queue.assigned_collection))
        delete_collection(self.ref.collection(Queue.errored_collection))
        self.ref.delete()

    def __repr__(self):
        return self.id

class Task:
    '''Static method create a task from a doc'''
    def from_doc(queue, doc):
        dict = doc.to_dict()

        return Task(queue, dict['data'], dict['ttl'], doc.id, doc.reference, dict['assigned_to'], dict['priority'], dict['created'])

    def __init__(self, queue, data, ttl=60, id=None, ref=None, assigned_to=None, priority=0, created=None):
        self.queue = queue
        self.data = data
        self.ttl = ttl
        self.id = id
        self.ref = ref
        self.assigned_to = assigned_to
        self.priority = priority
        self.created = created

    def to_dict(self):
        if self.created is None:
            self.created = datetime.datetime.now(pytz.UTC)

        task_dict = {
            'created': self.created,
            'data': self.data,
            'ttl': self.ttl,
            'assigned_to': None,
            'priority': self.priority
        }

        if self.assigned_to is not None:
            task_dict['assigned_to'] = self.assigned_to

        return task_dict

    '''Add a task to a queue'''
    def create(self, db):
        # TODO run Queue(args.queue).create(db) to add a document so we can search for it
        self.ref = db.collection('queues').document(self.queue).collection(Queue.unassigned_collection).document();
        self.id = self.ref.id
        self.ref.create(self.to_dict()); # TODO create if dosen't exist?

    '''Assign to a worker
    Returns Boolean - True if assign successful
    '''
    def assign(self, db, worker_id):
        self.ref.delete()
        self.assigned_to = worker_id

        if self.ttl is not None and type(self.ttl) == int:
            self.ttl = datetime.datetime.now(pytz.UTC) + datetime.timedelta(seconds=self.ttl)

        new_ref = db.collection('queues').document(self.queue).collection(Queue.assigned_collection).document(self.id);
        try:
            new_ref.create(self.to_dict())
            self.ref = new_ref
        except google.api_core.exceptions.AlreadyExists:
            return False

        return True

    '''Remove the current document'''
    def complete(self, db):
        # TTL expired
        if self.ttl is not None and self.ttl < datetime.datetime.now(pytz.UTC):
            print('Task %s TTL expired' % self.id) # TODO flush local writes?
            print(self.ttl)
            print(datetime.datetime.now(pytz.UTC))
            self.error(db)
        else:
            self.ref.delete()

    def error(self, db, message=None):
        self.ref.delete()
        self.ref = db.collection('queues').document(self.queue).collection(Queue.errored_collection).document(self.id);
        dict = self.to_dict()
        if message is not None:
            dict['error_message'] = message
        self.ref.set(dict);

    def requeue(self, db):
        self.ref.delete()
        self.ref = db.collection('queues').document(self.queue).collection(Queue.unassigned_collection).document(self.id);

        # Unassign
        self.assigned_to = None

        # Refresh TTL

        ttl_seconds = self.created - self.ttl
        self.created = datetime.datetime.now(pytz.UTC)
        self.ttl = self.created + ttl_seconds
        print('Requeign with', ttl_seconds)

        # Try to requeue, but may have been beaten to it
        try:
            self.ref.create(self.to_dict());
        except google.api_core.exceptions.AlreadyExists:
            return False

        return True


    def __repr__(self):
        if self.id is None:
            return 'new task'
        else:
            return self.id

'''Blocking call for next task'''
def next_task(db, queue, worker_id, poll_interval=2, expire_interval=60, min_priority=-1, blocking=True):

    check_expiry = expire_interval # Ensure it does at begining
    while True:
        if check_expiry >= expire_interval:
            Queue(queue).expire_ttl(db)
            check_expiry = 0 # reset

        docs = db.collection('queues').document(queue).collection(Queue.unassigned_collection).where('priority', '>=', int(min_priority)).order_by('priority', direction=firestore.Query.DESCENDING).order_by('created').get()

        for task_doc in docs:
            task = Task.from_doc(queue, task_doc)

            # Try and assign to this worker
            success = task.assign(db, worker_id)
            if success:
                return task

        if not blocking:
            return None

        time.sleep(poll_interval)
        check_expiry += poll_interval

