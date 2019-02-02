# Copyright 2018 Jet.com 
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#  http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from collections import Mapping
from enum import Enum
from types import MappingProxyType
from typing import List


FloatVector = List[float]
IntegerVector = List[int]
StringVector = List[str]
Float2DVector = List[List[float]]


class DistanceMetric(str, Enum):
  CityBlock = 'cityblock'
  Cosine = 'cosine'
  Euclidean = 'euclidean'
  L1 = 'l1'
  L2 = 'l2'
  Manhattan = 'manhattan'
  BrayCurtis = 'braycurtis'
  Canberra = 'canberra'
  Chebyshev = 'chebyshev'
  Correlation = 'correlation'
  Dice = 'dice'
  Hamming = 'hamming'
  Jaccard = 'jaccard'
  Kulsinki = 'kulsinki'
  Mahalanobis = 'mahalanobis'
  Minkowski = 'minkowski'
  Rogerstanimoto = 'rogerstanimoto'
  Russellrao = 'russellrao'
  Seuclidean = 'seuclidean'
  Sokalmichener = 'sokalmichener'
  Sokalsneath = 'sokalsneath'
  SqEuclidean = 'sqeuclidean'
  Yule = 'yule'