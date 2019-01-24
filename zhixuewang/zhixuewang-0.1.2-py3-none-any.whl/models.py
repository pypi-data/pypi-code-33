from collections import namedtuple
subjectDataModel = namedtuple("scoreDataModel", ["score", "classRank", "gradeRank"])
classDataModel = namedtuple("classDataModel", ["avgScore", "highScore", "rank"])
gradeDataModel = namedtuple("gradeDataModel", ["avgScore", "highScore"])
