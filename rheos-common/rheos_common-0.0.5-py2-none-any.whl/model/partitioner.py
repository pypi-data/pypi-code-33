import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Sequence, Any, Set


@dataclass
class PartitionRecord(object):
    contig: str
    left: int
    right: int
    partition: int


class Partitioner(object):
    seq_dict: Dict[str, int] = {
        "1": 249250621,
        "2": 243199373,
        "3": 198022430,
        "4": 191154276,
        "5": 180915260,
        "6": 171115067,
        "7": 159138663,
        "8": 146364022,
        "9": 141213431,
        "10": 135534747,
        "11": 135006516,
        "12": 133851895,
        "13": 115169878,
        "14": 107349540,
        "15": 102531392,
        "16": 90354753,
        "17": 81195210,
        "18": 78077248,
        "19": 59128983,
        "20": 63025520,
        "21": 48129895,
        "22": 51304566,
        "X": 155270560,
        "Y": 59373566,
        "MT": 16569
    }
    partition_width: int = 20000000
    partition_records: List[PartitionRecord] = []
    records_by_partition: Dict[int, PartitionRecord] = {}
    records_by_contig: Dict[str, List[PartitionRecord]] = {}

    def get_partition_for_rec(self, contig: str, left: int, right:int):
        partitions_for_rec: Set = []
        rec_list = self.records_by_contig[contig]

        pass

    def __init__(self):
        partition_index = 0
        for key, value in self.seq_dict.items():
            print(f"{key} {value}")
            num_partitions = math.ceil(value / self.partition_width, )

            for i in range(num_partitions):
                # print(f"{i*self.partition_width + 1} {min((i+1)*self.partition_width, value)}")
                my_record = PartitionRecord(contig=key,
                                            left=i * self.partition_width + 1,
                                            right=min((i + 1) * self.partition_width, value),
                                            partition=partition_index)
                self.partition_records.append(my_record)
                self.records_by_partition[partition_index] = my_record

                contig_recs = self.records_by_contig.get(key, [])
                contig_recs.append(my_record)
                self.records_by_contig[key] = contig_recs

                partition_index += 1


my_partitioner = Partitioner()
print(my_partitioner.partition_records)
print(my_partitioner.records_by_partition)
print(my_partitioner.records_by_contig)
