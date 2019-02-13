from data import SortData

def BubbleSort(sv):
    assert isinstance(sv, SortData), "Type Error"

    Length = sv.length
    for i in range(Length-1, -1, -1):
        for j in range(0, i, 1):
            if sv.data[j] > sv.data[j+1]:
                sv.Swap(j, j+1)

if __name__ == "__main__":
    sv=SortData(64)
    sv.Visualize()
    sv.StartTimer()
    BubbleSort(sv)
    sv.StopTimer()
    sv.SetTimeInterval(0)
    sv.Visualize()