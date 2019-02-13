
import re, hmac, hashlib, json, time, random, requests, datetime, os, traceback, time
from itertools import zip_longest, chain, islice
from decimal import Decimal
import __main__
BC_PUBLIC_KEY = ''
BC_SECRET_KEY = ''

def produceSignature(public_key,secret_key):
	#PRODUCE SIGNATURE FOR API CALLS
	#function sends an HMAC signature produced using both public and secret keys (this is more secure than sending secret key in the open)
	timestamp = str(int(time.time()))
	nonce = str(random.randint(1,10000))
	binary_salt = (secret_key+timestamp+nonce).encode('ascii')
	binary_pub = public_key.encode('ascii')
	newhash = hmac.new(binary_pub, binary_salt, hashlib.sha512).hexdigest()
	#recoded = base64.encodebytes(newhash)
	return newhash, timestamp, nonce

def streamLines(file):
	with open(file, "r", encoding="utf-8") as f:
		for line in f:
			yield line.rstrip()

def streamDir(dir):
	for path,dirs,files in os.walk(dir):
		for file in files:
			try:
				fullpath = os.path.join(path,file)
				filedata = open(fullpath,"r",encoding="utf-8").read()
				yield filedata
			except UnicodeDecodeError:
				print(f'File {file} could not be parsed. Must be utf-8 encoded.')

def chunks(iterable):
	iterator = iter(iterable)
	for first in iterator: 
		yield chain([first], islice(iterator, 24))
		
def postStream(datasetid, items, format='array'):
	#POST ITEMS TO A STREAM
	#Format Options:
	#'array' - processes all items in a python array of any length, in batches of 25
	#'dir' - reads all files in a directory (provide a string path) and uploads the text contexts, not utf-8 encoded files are skipped
	#'file' - reads a file (provide a string path) line by line and uploads each line as an individual item
	try:
		start_time = time.time()
		exponential_wait = 1
		signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
		last_signature_time = time.time()
		parameters = {'DatasetId':datasetid}
		headers = {
			'Content-Type':'application/json',
			'Auth-Timestamp':curtime,
			'Auth-Signature':signature,
			'Auth-Nonce':curnonce,
			'x-api-key':BC_PUBLIC_KEY
			}
		
		if format =="lines":
			itemstream = chunks(streamFile(items))
		elif format == "dir":
			itemstream = chunks(streamDir(items))
		else:
			itemstream = chunks(items)	
		
		for itembatch in itemstream:
			print('getting one batch')
			item = list(itembatch)
			stringJSON = json.dumps({"items":item}, default=str)
			if int(time.time() - last_signature_time)>270:
				signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
				headers = {
					'Content-Type':'application/json',
					'Auth-Timestamp':curtime,
					'Auth-Signature':signature,
					'Auth-Nonce':curnonce,
					'x-api-key':BC_PUBLIC_KEY
					}
				last_signature_time = time.time()
				print('refreshed signature')
			
			r = requests.put('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers, data=stringJSON)

			print(r.elapsed.total_seconds())
			print(r.status_code)
			print(r.text)
			
			if r.status_code == 200:
				print('this was all good')
			elif r.status_code == 429:
				print(r.status_code)
				print(r.text)
				while r.status_code == 429:
					exponential_wait = exponential_wait + 1
					print(f"Hit rate limit, waiting {exponential_wait} seconds before retrying")
					time.sleep(exponential_wait**2)
					r = requests.put('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers, data=stringJSON)
				if r.status_code != 200:
					print(r.status_code)
					print(r.text)
					break					
			else:
				break		
		
	except Exception as e:
		print(e)
		print(traceback.format_exc())

	
def getStreamRange(datasetid, FromTime=None, ToTime=None, Order='Newest', Last=None, BatchSize=250, Limit=None, AutoPaginate=True):
	#Gets a precise time range from the stream
	#datasetid - string formatted id of the dataset
	#FromTime, ToTime - must be Epoch Timestamp as Integer - e.g. int(time.time()) for current time
	#Limit - function will stop when Limit number of items have been returned
	#AutoPaginate - function will paginate through results until there are no more available OR until Limit is reached
	#Last - if AutoPaginate is False and there are more results to paginate ('Last' will be a key in results), you can manually pass the 'Last' result to function to begin new query time range
	#BatchSize - the number of results to return per request/page (maximum of 250)
	
	try:
		start_time = time.time()
		exponential_wait = 0
		signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
		last_signature_time = time.time()
		parameters = {'DatasetId':datasetid, }
		if FromTime is not None:
			parameters['FromTime']=FromTime
		if ToTime is not None:
			parameters['ToTime']=ToTime
		if Last is not None:
			parameters['Last']=Last
		parameters['BatchSize'] = BatchSize
		parameters['Order']=Order
		
		headers = {
			'Content-Type':'application/json',
			'Auth-Timestamp':curtime,
			'Auth-Signature':signature,
			'Auth-Nonce':curnonce,
			'x-api-key':BC_PUBLIC_KEY
			}
		
		print('Connecting to Bounty Country...')
		r = requests.get('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers)

		if r.status_code == 200:
			print('Connected')
			body = r.json()
			total_count = body['Count']
			print("Retrieved ",body['Count']," items in total.")
			
			if StreamHandler is not None:
				StreamHandler(body)
			else:
				yield(body)
			
			if AutoPaginate == True:
				while ('Last' in body) and (total_count < Limit):			
					
					parameters ['Last'] = body['Last']
					print('paging...')
					
					if int(time.time() - last_signature_time)>270:
						signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
						headers = {
							'Content-Type':'application/json',
							'Auth-Timestamp':curtime,
							'Auth-Signature':signature,
							'Auth-Nonce':curnonce,
							'x-api-key':BC_PUBLIC_KEY
							}
						last_signature_time = time.time()
						print('refreshed signature')	
						
					r = requests.get('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers)

					if r.status_code == 200:
						body = r.json()
						exponential_wait = 0
						total_count = total_count + body['Count']
						if Limit:
							if total_count > Limit:
								dif = total_count-Limit
								body['Items'] = body['Items'][:-dif or None]
								body['Count'] = body['Count'] - dif
								body['Last'] = body['Items'][-1]["upload_timestamp"]
								print("Retrieved ", (total_count-dif), " items in total.")
								break
						print("Retrieved ", total_count, " items in total.")
						if StreamHandler is not None:
							StreamHandler(body)
						else:
							yield(body)				
					
					elif r.status_code == 429:
						exponential_wait = exponential_wait + 1
						waiter = exponential_wait**2
						print(r.status_code, r.text)
						print(f"Hit rate limit, waiting {waiter} seconds before retrying")
						time.sleep(waiter)
						
					else:
						print(r.status_code, r.text)
						break
			print("COMPLETE")
		else:
			print(r.status_code, r.text)
			
	except Exception as e:
		print(e)
		print(traceback.format_exc())

def getLiveStream(datasetid, BatchSize=250, StreamHandler=None):
	#continuously polls a stream and passes new batches of items to the StreamHandler function that you specify
	#datasetid - string formatted id of the dataset
	#BatchSize - the number of results to return per request/page (maximum of 250)
	#StreamHandler - any python function you wish to perform on each batch of items
	
	if StreamHandler is None:
		message = "ERROR: You must supply a stream handler function in the from getInfiniteStream(datasetid,StreamHandler=YOUR_STREAM_HANDLER)"
		print(message)
		return message
	try:
		start_time = time.time()
		exponential_wait = 0
		signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
		last_signature_time = time.time()
		parameters = {'DatasetId':datasetid,'BatchSize':BatchSize,'Order':'Newest'}
		headers = {
			'Content-Type':'application/json',
			'Auth-Timestamp':curtime,
			'Auth-Signature':signature,
			'Auth-Nonce':curnonce,
			'x-api-key':BC_PUBLIC_KEY
			}
		
		print('Connecting to Bounty Country...')
		r = requests.get('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers)

		if r.status_code == 200:
			print('Connected')
			body = r.json()
			body['Last'] = body['Items'][0]["upload_timestamp"]
			StreamHandler(body)
				
			while True:
				if ('Last' in body) and (r.status_code ==200):
					parameters['Last'] = body['Last']
					parameters['Order'] = 'Oldest'
					print('paging...')
					exponential_wait = 0
					
					if int(time.time() - last_signature_time)>270:
						signature,curtime,curnonce = produceSignature(BC_PUBLIC_KEY, BC_SECRET_KEY)
						headers = {
							'Content-Type':'application/json',
							'Auth-Timestamp':curtime,
							'Auth-Signature':signature,
							'Auth-Nonce':curnonce,
							'x-api-key':BC_PUBLIC_KEY
							}
						last_signature_time = time.time()
						print('refreshed signature')
					
					r = requests.get('https://api.bountycountry.com/stream/datasets/', params=parameters, headers=headers)
					body = r.json()		
					
				elif r.status_code == 200:
					exponential_wait = exponential_wait + 1
					waiter = exponential_wait**2
					print(f"No new results, waiting {waiter} seconds before retrying...")
					time.sleep(waiter)
					
				elif r.status_code == 429:
					exponential_wait = exponential_wait + 1
					waiter = exponential_wait**2
					print(f"Hit rate limit, waiting {waiter} seconds before retrying...")
					time.sleep(waiter)
		else:
			print(r.status_code, r.text)
			
	except Exception as e:
		print(e)
		print(traceback.format_exc())		