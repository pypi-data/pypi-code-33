from enum import Enum


class DataPath(Enum):
    local_1 = 'D:/YandexDisk/Work/dna-methylation'
    local_2 = 'E:/YandexDisk/Work/dna-methylation'
    local_3 = 'C:/Users/User/YandexDisk/dna-methylation'


class DataBase(Enum):
    GSE40279 = 'GSE40279'
    GSE52588 = 'GSE52588'
    GSE30870 = 'GSE30870'
    GSE61256 = 'GSE61256'
    GSE63347 = 'GSE63347'
    GSE87571 = 'GSE87571'
    EPIC = 'EPIC'
    liver = 'liver'


class DataType(Enum):
    cpg = 'cpg'
    gene = 'gene'
    bop = 'bop'
    suppl = 'suppl'
    cache = 'cache'
    attributes = 'attributes'


__all__ = ['DataPath', 'DataBase', 'DataType']
