# coding: utf8
import json

from enosapi.client.EnOSDefaultClient import EnOSDefaultClient
from OpenSSL import crypto
# from enosapi.request.CreateProductEnvisioncnRequest import CreateProductEnvisioncnRequest
from enosapi.request.CreateProductRequest import CreateProductRequest
from enosapi.request.ListDevicesRequest import ListDevicesRequest
from enosapi.request.ListProductsRequest import ListProductsRequest

import time

from enosapi.request.PostMeasurepointsEnOSRequest import PostMeasurepointsEnOSRequest
from enosapi.util import const

from enosapi.request.ApplyCertificateByDeviceKeyRequest import ApplyCertificateByDeviceKeyRequest

if __name__ == '__main__':
    # param = {"page": 1, "pageSize": 5}
    #
    # print (int(time.time() * 1000))
    # request = ListProductsRequest(org_id="o15425959616051", params=param)
    # client = EnOSDefaultClient("http://10.27.20.148:8080/enosapi",
    #                                  "4780b37d-1a4e-42e51e4b7458-337d-4ac4",
    #                                  "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    #
    # reponse = client.execute(request)
    # print reponse.data

    # paramCreate = {
    #     "RawImage": "aFile",
    #     "Value": 121,
    #     "ProcessedImage": "bFile",
    #     "UpperLimit": 1543399693143,
    #     "Senso": "power"
    # }
    #
    # f = {"aFile": open("114.jpg"), "bFile": open("114.jpg")}
    # createRequest = PostMeasurepointsEnOSRequest("o15425959616051", "eoMmFFRN", paramCreate, f)
    #
    # client = EnOSDefaultClient("https://beta-portal-cn4.eniot.io:8081/enosapi",
    #                                  "EEOP_TEST",
    #                                  "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    #
    # res = client.execute(createRequest)
    # if res.is_success():
    #     data = res.data
    #     print data
    #     print res
    # else:
    #     print "error"
    # print "----------------------------------"

    # res = client.execute(request)
    # if res.is_success():
    #     data = res.data
    #     print data
    #     print type(data["data"])
    #     print res
    # else:
    #     print "error"

    # createRequest = CreateProductRequest(org_id="o15425959616051", params={"teat": "test"})
    #
    # client = EnOSDefaultClient("https://beta-portal-cn4.eniot.io/enosapi/",
    #                            "4780b37d-1a4e-42e51e4b7458-337d-4ac4",
    #                            "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    #
    # response = client.execute(createRequest)
    # print response

    #f = {"aFile": open("114.jpg"), "bFile": open("114.jpg")}
   # param = {"data": '[{"measurepoints":{"Image":{"RawImage":"local://aFileg","Value":9,"ProcessedImage":"local://bFileg","UpperLimit":12,"Sensor":"test"}},"time":1541591858001,"assetId":"2l9JEao7"}]'}

    #param = {"data": "[{\"measurepoints\":{\"Image\":{\"RawImage\":\"local://aFile\",\"Value\":9,\"ProcessedImage\":\"local://bFile\",\"UpperLimit\":12,\"Sensor\":\"test\",\"AlertFlag\":1,\"AlertMessage\":\"PM10 over limit\"}},\"time\":1543492858001,\"assetId\":\"2l9JEao7\"}]"}
    # param = {
    #     "data": '[{"measurepoints":{"Image":{"RawImage":"local://aFile","Value":9,"ProcessedImage":"local://bFile","UpperLimit":12,"Sensor":"test","AlertFlag":1,"AlertMessage":"PM10 over limit"}},"time":1543492858001,"assetId":"2l9JEao7"}]'}
    #
    # #param = {"test": "test"}
    # f = {"aFile": open("114.jpg", 'rb'), "bFile": open("114.jpg", 'rb')}
    # request = PostMeasurepointsEnOSRequest(org_id="o15425959616051", product_key="6fAT4ic1",
    #                                              params=param, upload_file={})
    #
    # client = EnOSDefaultClient("https://beta-portal-cn4.eniot.io/enosapi/",
    #                                  "4780b37d-1a4e-42e51e4b7458-337d-4ac4",
    #                                  "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    #
    # response = client.execute(request)
    # jsonStr = json.dumps(response.__dict__)
    # print (jsonStr)
    # print(response)




    # csr = "\"-----BEGIN CERTIFICATE REQUEST-----\\nMIICsTCCAZkCAQAwbDELMAkGA1UEBhMCQ04xETAPBgNVBAgMCFNoYW5naGFpMREw\\nDwYDVQQHDAhTaGFuZ2hhaTENMAsGA1UECgwERW5PUzEWMBQGA1UECwwNQ2xvdWQg\\nU2VydmljZTEQMA4GA1UEAwwHaW90X2h1YjCCASIwDQYJKoZIhvcNAQEBBQADggEP\\nADCCAQoCggEBANcoly7BKWTras3QNhB2YzpZjX4ln6K0c2prhVD+otFwbfb1iEPx\\naCaKiQCmGkAjHhgzvUhjK6bNQrsxXnmO6+/d6MdReDZYNWDJySGkCnTcCAS4KQ//\\n/u0vTNkGvPlbYAaXy9sUAfKjtYTjws/iK2MUT6xE0+kbB2LyR7s7sBGGGOo7DPmb\\n/GF3MCbZWp+SKhW+2eQSUMCAFxg0RasBVfccZE+Bsib9NAqypDoazsw9Ar9wsm4O\\nQNg+dZjrorlusWZy8AoB0HmLyrP0akoXAENvXAo4L12h/2U4VFZWR6nPbOo9qC2P\\n6qqIowpeYZbaj279pYUyHJlQQ5FAJ739iGUCAwEAAaAAMA0GCSqGSIb3DQEBCwUA\\nA4IBAQCINl0uLvZn2O5/DWsgMBt7WjBD2usLgcSSGxhrdLpgWqYisOgCNKkCaTjc\\n+8UdMGd25UMbmIGoy/x0w4RfW93L/nMM3sM1pyi10C5668J7RgE35XApTBGdHJRB\\nbVL+yjiXumv6XfiXIRZmTcOvVitjD/myQxt07ebe3shNt/NNkoWdMfqkCxmDZPK1\\nqfteBwKCHi45NC+cjXrYoB9M1WERcWqs4cjBFLEtOw6QeePLa86Qu8D5qdSkeopq\\n08+yAw7qaGOm+fFQUuvinRtdTYVoVsyvHPeRyPkLyH0KqMEosfAVzevtaDQowBP0\\nGDPhODlUXgAZIOEb+HAjKCNqiTTP\\n-----END CERTIFICATE REQUEST-----\""
    # request = ApplyCertificateByDeviceKeyEnvisioncnRequest(org_id="o15425959616051", product_key="LEO3S55B",
    #                                                        device_key="NMgFPQJ8KM", csr=csr)
    #
    # client = DefaultEnvisioncnClient("http://10.27.20.148:8080/enosapi",
    #                                  "EEOP_TEST",
    #                                  "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    # reponse = client.execute(request)
    # print reponse
    # print reponse.data
    # print reponse.data['cert']
#     cert = crypto.load_certificate(crypto.FILETYPE_PEM, """-----BEGIN CERTIFICATE-----
# MIID2TCCAsGgAwIBAgIJAIxUqZFXyO8oMA0GCSqGSIb3DQEBCwUAMIGCMQswCQYD
# VQQGEwJDTjERMA8GA1UECAwIU2hhbmdoYWkxETAPBgNVBAcMCFNoYW5naGFpMQ0w
# CwYDVQQKDARFbk9TMRAwDgYDVQQLDAdFbk9TIENBMRAwDgYDVQQDDAdFbk9TIENB
# MRowGAYJKoZIhvcNAQkBFgtjYUBlbmlvdC5pbzAeFw0xODExMTkxMDIwMjdaFw0y
# ODExMTYxMDIwMjdaMIGCMQswCQYDVQQGEwJDTjERMA8GA1UECAwIU2hhbmdoYWkx
# ETAPBgNVBAcMCFNoYW5naGFpMQ0wCwYDVQQKDARFbk9TMRAwDgYDVQQLDAdFbk9T
# IENBMRAwDgYDVQQDDAdFbk9TIENBMRowGAYJKoZIhvcNAQkBFgtjYUBlbmlvdC5p
# bzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANtdO01M5QHAwqalr79b
# WQEn3rpYeby6vVM92TUmurhL+XsTjVGi0n9LVpW30yaOQ7eACtMwwEqs79shWkis
# JXVsjhT7OtZ8Ct1Nvc846MDfQXyi8VytlGIdGAGtJfWl36wlLiYYlTm5sOoAHNZz
# mPwBS3T+17w24AqWx8YQrjVo2vNFyVY6NxDPj1FbaJK8HWR/EhDql9g6Vd8RmBil
# JytFzEJLCopm+lc8Pcwv1KNmIBy9cLZzGt6CkVgHgobsHBTMabZwjbW7c7xjV5Jt
# aeQSdabTrk+ZpDIQniK0mHQojUxlPNyLb00mSHo56VoxcVGgDPbAp68PxxIgtTfE
# cJsCAwEAAaNQME4wHQYDVR0OBBYEFK5P96+nGXsLri55D7R75a6M9FQNMB8GA1Ud
# IwQYMBaAFK5P96+nGXsLri55D7R75a6M9FQNMAwGA1UdEwQFMAMBAf8wDQYJKoZI
# hvcNAQELBQADggEBAKu8p3lRlT71SkSrCLFandOesgWWFA40ioIzY1bKggLjEoGw
# o079UpNEL21BgojkCXVNkFx63nna5DSBkopmHUNwTLYgUvUpPIBrEtt42XyWvanw
# 4XvOcT5dvB2SDgyxDxVJLKZaEuKXTKmZp9OcFV7jB4mgaq6YYbx4oau7Yrpy1G1P
# HJY1y1ubZPQT2AKZVaKIPO6BUZkaZ7G4F4dm5cuCCQ8KURPQkXJ1S1AGH1Tgu1l9
# 7Arxz1A2NDpsi0GzFIuBiPWyMlxI0TFi2X3bDk6iCwS7B5PGI9CyRgiZUK50QnAF
# F3Pog8oYk7jZIJdWwieklVukwD41YI/vNKaJ59E=
# -----END CERTIFICATE-----""")
#     print cert
#     sub = cert.get_subject()
#     print sub
#     print sub.C
#     print sub.ST
#     print sub.O
#     print sub.L
#     print sub.OU
#     print sub.CN
#     issuer = cert.get_issuer()
#     print issuer
#     issued_by = issuer.CN
#     print issued_by
#     sub.CN = "WTRSSFS"
#     print sub
#
#     pkey = crypto.PKey()
#     pkey.generate_key(crypto.TYPE_RSA, 2048)
#     req = crypto.X509Req()
#     subject = req.get_subject()
#     subject.C = sub.C
#     subject.ST = sub.ST
#     subject.O = sub.O
#
#     subject.L = sub.L
#     subject.OU = sub.OU
#     subject.CN = sub.CN
#
#     req.set_pubkey(pkey)
#     req.sign(pkey, "sha256")
#
#     passphrase = "foo"
#     called = []
#
#
#     def cb(writing):
#         called.append(writing)
#         return passphrase

    # print crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey, "CAST", passphrase=cb)

    # req_str = crypto.dump_certificate_request(crypto.FILETYPE_PEM, req)
    #
    # csr = '\"' + req_str.replace("\n", "\\n") + '\"'
    #
    # client = EnOSDefaultClient("http://10.27.20.148:8080/enosapi",
    #                                  "EEOP_TEST",
    #                                  "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    # request = ApplyCertificateByDeviceKeyRequest(org_id="o15425959616051", product_key="iWtG6XAV",
    #                                              device_key="uDECfGXrOx", csr=csr)
    # reponse = client.execute(request)
    #
    # print reponse
    client = EnOSDefaultClient("http://10.27.20.148:8080/enosapi",
                                      "4780b37d-1a4e-42e51e4b7458-337d-4ac4",
                                      "1e4b7458-337d-4ac4-8f20-af3426ea4e7b")
    listdevice = ListDevicesRequest(org_id="o15425959616051", product_key="BRNqK1XL", page_size=10, page_token=0)

    response = client.execute(listdevice)
    print response
    param = {"page": 1, "pageSize": 5}

    request = ListProductsRequest(org_id="o15425959616051", params=param)
    response1 = client.execute(request);

    print response1
