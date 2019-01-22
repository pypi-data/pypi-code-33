from pyseas import seas

def test_seasconsumption(email,password):
    consumptionYearToDate = seas(email,password).consumptionYearToDate()
    consumptionYear2018 = seas(email,password).meteringPoints('Year','2018-1-1','2018-12-31')
    print(consumptionYearToDate)
    print(consumptionYear2018)
