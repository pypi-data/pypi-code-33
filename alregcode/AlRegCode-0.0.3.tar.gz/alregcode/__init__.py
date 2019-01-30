name = "alregcode"

import datetime


def regGenerate(str_code, int_code, len_code):

    str_code = str_code
    now = datetime.date.today()
    tahun = str(now.year)
    bulan = str(now.month)
    if len(bulan) < 2:
        bulan = "0" + str(now.month)

    tanggal = tahun + bulan

    kode = int_code

    if isinstance(kode, type(None)):
        nomor = ""
        for x in range(len_code):
            nomor = nomor + "0"
        
        regGenerate.inc = "0"

    else:
        nomorr = str(int(kode) + 1)
        nomors = "0"
        for x in range((len_code-1)-len(nomorr)):
            nomors = nomors + "0"

        nomor = nomors + nomorr 

        regGenerate.inc = nomorr


    kode = str_code+tahun+bulan+nomor

    return kode
