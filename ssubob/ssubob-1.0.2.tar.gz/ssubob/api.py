"""
    API HERE
"""

from .parser import food_api


def refresh(date=None):
    """
    :param date:
    :return:
    """
    food_api.refresh(date)


def get(place):
    """
    :param place: 학식, 더 키친, 스넥코너, 교식, 푸드코트, 기식 중에 1가지가 온다
    :type place: str
    :return:
    """
    return food_api.get_food(place)
