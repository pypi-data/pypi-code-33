from me31 import Me31

def main():
    dmm = Me31('COM4')
    #print(dmm.get_range())
    #for i in range(100):
    #    try:
    #        print(dmm.get_value())
    #    except Me31OverloadError:
    #        print("overload")

    for i in range (5):
        measurment = dmm.get_measurment()
        print(measurment)
        print(measurment.value)
        print(measurment.unit)
        print(measurment.measuring_mode)
    #print(dmm.get_current_range())
    #print(dmm.get_measuring_current_mode())
    #print(dmm.get_value())
    #print(dmm.get_measuring_mode())


if __name__ == "__main__":
    main()