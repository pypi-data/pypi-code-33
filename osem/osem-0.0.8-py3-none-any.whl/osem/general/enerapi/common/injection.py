from business.Base.Base import Base
from data.InMemoryFileCache import InMemoryFileCache

from Ener.common import FeatureBroker

# Tell the IoC container that whenever someone needs a cache system, he'll get the InMemoryFileCache
Base.features = FeatureBroker()
Base.features.Provide('Cache', InMemoryFileCache)
