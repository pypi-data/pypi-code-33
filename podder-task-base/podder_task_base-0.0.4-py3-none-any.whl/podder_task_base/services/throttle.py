from typing import Any, List


class ThrottleService(object):
    @staticmethod
    def throttling(resources: List[Any], throttling_max: int) -> List[Any]:
        return resources[:throttling_max]
