import datetime

import marketo
url = "https://004-QSK-624.mktoapi.com/soap/mktows/3_1"
user_id = 'everbridge1_270743914C2A3009E80DB7'
token = '902428592713004544CC22AA330000ABEE886ADC1D66'.encode()

client = marketo.Client(soap_endpoint=url,
                        user_id=user_id,
                        encryption_key=token)
file_stream = open("test_file.json", "w")
res = client.get_multiple_leads_last_update_selector(datetime.datetime(2018, 12, 20, 0), datetime.datetime(2018, 12, 20, 1),
                                                     file_stream)
file_stream.close()
rr = [x.to_dict() for x in res]
print(len(rr))