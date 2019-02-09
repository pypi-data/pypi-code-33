def response(total_candidates,bidding_sequence=[],relation_list=[],alpha=[]):
  # total_candidates : total number of participants
  # bidding_sequence: arrary containing timeseries data in format [[candidate_id,candidate_offer],[candidate_id,candidate_offer] ....]
  # relation_list: array containing relationship in form of [[looser,winner],..] here 1 represents the person who won the bidding, 2 repreents the second last bidding candidate etc.
  # alpha: it determine the discount ratio for each relationship present in the relation_list
  candidate_sequence=[]
  price_sequence=[]
  receive_money=[0]*total_candidates
  for bseq in bidding_sequence:
    candidate_sequence.append(bseq[0])
    price_sequence.append(bseq[1])
  index=-1
  for rel in relation_list:
    index=index+1
    if rel[0] <= len(candidate_sequence) and rel[1] <= len(candidate_sequence):
      receive_money[candidate_sequence[-rel[0]] -1 ]=receive_money[candidate_sequence[-rel[0]] -1 ] - float(alpha[index]*price_sequence[-rel[0]])
      receive_money[candidate_sequence[-rel[1]] -1 ]=receive_money[candidate_sequence[-rel[1]] -1 ] + float(alpha[index]*price_sequence[-rel[0]])
  money_dict={}
  index=0
  for e in range(len(receive_money)):
    index=index+1
    if receive_money[e] !=0:
      money_dict[index]=receive_money[e]
  return [receive_money,money_dict]
