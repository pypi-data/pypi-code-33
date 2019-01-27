	
	
		
def create_pp_var_concat(ar):
	new_ar = []
	ret_ar = [PP_VAR_CONCAT,new_ar]
	s = ar[0]
	
	
	index = s.find("{&")
	while index != -1:
		if index > 0:
			new_ar.append([STRING,s[:index],NONE])
		end_index = s.find("}",index+2)
		if end_index == -1:
			print("OEIEIEIEIEIE!!!")
			print(s)
			print(ar)
			exit()
		x = s[index+2:end_index].lower().strip()
		new_ar.append([PP_VAR,x])
		s = s[end_index+1:]
		index = s.find("{&")
		
	if s:
		new_ar.append([STRING,[s,UNKNOWN]])
	return ret_ar
		
		
		
def create_string_concatx(ar):
	new_ar = []
	ret_ar = [STRING_CONCAT,new_ar]
	s = ar[0]
	
	
	index = s.find("{&")
	while index != -1:
		if index > 0:
			new_ar.append([STRING,s[:index],NONE])
		end_index = s.find("}",index+2)
		if end_index == -1:
			print("OEIEIEIEIEIE!!!")
			print(s)
			print(ar)
			exit()
		x = s[index+2:end_index].lower().strip()
		new_ar.append([PP_VAR,x])
		s = s[end_index+1:]
		index = s.find("{&")
		
	if s:
		new_ar.append([STRING,s])


	return ret_ar
		
	
	
	
def do_ppc_read_condition(ar):
	count = 0
	for i,a in enumerate(ar):
		if not isinstance(ar[i],list): continue
		x = ar[i]
		if x[0] == PP_CONDITION:
			if x[1] == pp_if:
				count += 1
				continue
			if x[1] == pp_then:
				if not count:
					return i
				continue
			if x[1] == pp_endif:
				count -= 1
				continue
	return None
	

def do_ppc_read_block(ar):
	count = 0
	for i,a in enumerate(ar):
		if not isinstance(ar[i],list): continue
		x = ar[i]
		if x[0] == PP_CONDITION:
			if x[1] == pp_if:
				count += 1
				continue
			if x[1] == pp_elseif or x[1] == pp_else:
				if not count: return i
				continue
			if x[1] == pp_endif:
				if not count: return i
				count -= 1
				continue
	if not count:
		return len(ar)
	
	return None

def do_ppc(ar):
	ori = ar[:]
	ar = ar[1:-1]
	
	condition_statements = []
	code_blocks = []
	ret_ar = [PP_CONDITIONBLOCK,[condition_statements,code_blocks]]
	
	index = do_ppc_read_condition(ar)
	if not index:
		print("do_ppc failed !" + str(ar))
		exit()

	condition_statements.append(ar[:index])
	
	ar = ar[index+1:]
	index = do_ppc_read_block(ar)
	if index is None :
		print("do_ppc do_ppc_read_block failed !" + str(ar))
		exit()
	
	code_block = ar[:index]
	code_blocks.append(code_block)
	ar = ar[index+1:]
	if ar:
		print(make_readable_ar(ar))
		print(make_readable_ar(ori))
		exit()
	return ret_ar
def do_ppc_find_stop(ar,start=0):
	started = 0
	count = 0
	for i in range(start,len(ar)):
		x = ar[i]
		if isinstance(x,list) and x[0] == PP_CONDITION:
			if x[1] == "&if":
				count +=1
			elif x[1] == "&endif":
				count -= 1
			if count and (not started): started = 1
			if started and (not count):
				return i + 1
				
