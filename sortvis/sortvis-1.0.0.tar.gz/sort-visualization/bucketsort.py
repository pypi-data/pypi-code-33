import copy

from data import SortData

def BucketSort(sv):
    assert isinstance(sv, SortData), "Type Error"
    assert isinstance(sv.data[0], int), "Type Error"

    Length = sv.length
    bucket = [0 for _ in range(Length)]
    for i in range(Length):
        bucket[sv.data[i]] += 1
    j=0
    for i in range(Length):
        tmp = bucket[i]
        while tmp>0:
            sv.SetVal(j, i)
            tmp-=1
            j+=1


if __name__ == "__main__":
    sv=SortData(64)
    sv.Visualize()
    sv.StartTimer()
    BucketSort(sv)
    sv.StopTimer()
    sv.SetTimeInterval(0)
    sv.Visualize()