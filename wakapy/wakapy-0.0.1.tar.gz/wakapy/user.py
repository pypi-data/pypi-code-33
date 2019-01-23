import datetime

from typing import List

from wakapy.parser import JsonDict
from wakapy.exceptions import ContainerNotFound
from wakapy.utils import order_dict
from wakapy.plot import PieChart
from wakapy.day import Day


class Slice:
    """
    Given two valid dates it'll slice and save them. It always includes the given dates.

    Parameters
    ----------
        days : List[:class:`.Day`]
            The list of Day objects to slice by dates.
        dates : Union[:class:`str`, :class:`datetime.date`]
            date_1 has to be lower than date_2 and both have to follow the YYYY-MM-DD format.

    Note
    ----
    str given dates will be converted to :class:`datetime.date`, so both dates can be given in any of those 2 formats independently.
    The slicing will be done automatically upon creating the class with two valid dates.
    This class can be iterated, yields :class:`.Day` from :meth:`days`

    So this twos are equivalent: ::

        myslice = Slice(dates_list, date1, date2)

        for day in myslice:
            print(day.date)


            for day in myslice.days:
                print(day.date)

    Attributes
    ----------
    date_1 see dates.
    date_2 see dates.
    """
    def __init__(self, days, date_1=None, date_2=None):
        if not isinstance(date_1, str) and not isinstance(date_1, str) \
                and not isinstance(date_1, datetime.date) and not isinstance(date_2, datetime.date):
            raise TypeError("Parameters given have to be either <'str'> or <'datetime.date> objects")

        for date in (date_1, date_2):  # dateutils could be used instead of this.
            if not isinstance(date, datetime.date):
                try:
                    datetime.datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(f"Incorrect data format, should be YYYY-MM-DD, not {date}")

        self.date1 = date_1
        self.date2 = date_2

        index = 0
        for _date in (self.date1, self.date2):

            if isinstance(_date, str) and index == 0:
                year, month, day = _date.split('-')
                self.date1 = datetime.date(year=int(year), month=int(month), day=int(day))

            if isinstance(_date, str) and index == 1:
                year, month, day = _date.split('-')
                self.date2 = datetime.date(year=int(year), month=int(month), day=int(day))

            index += 1

        if self.date1 > self.date2:
            raise ValueError(f'{self.date1} cannot be bigger than {self.date2}')

        self._raw_days = days

    def __len__(self):
        return len(self.days)

    def __iter__(self):
        for day in self.days:
            yield day

    def _get_sliced_days(self) -> List[Day]:
        index1 = None
        index2 = None
        for index, day in enumerate(self._raw_days):

            if int(day.year) == self.date1.year:
                if int(day.month) == self.date1.month:
                    if int(day.day) == self.date1.day:
                        index1 = index

            if int(day.year) == self.date2.year:
                if int(day.month) == self.date2.month:
                    if int(day.day) == self.date2.day:
                        index2 = index

        if None in (index1, index2):
            raise ValueError('One of your dates do not exist')
        return self._raw_days[index1: index2 + 1]

    @property
    def days(self) -> List[Day]:
        """
        :property:

        :return: List[:class:`.Day`] sliced.
        """
        return self._get_sliced_days()

    def __repr__(self):
        return f'class <{self.__class__.__name__}({self.days})>'


class User:
    """Represents a user containing all the data from source file

        .. _wakatime: https://wakatime.com

        Parameters
        -----------
        fp : :class:`str`
            The file path to the Wakatime json file

        Attributes
        -----------
        fp
            :class:`str` - File path
        file
            The :class:`.JsonDict` containing all the data.
        display_name
            :class:`str` - User's `wakatime`_ displayed name, usually @ + **username**.
        created_at
            :class:`str` - User's creation date, eg: *2018-08-02T15:40:06Z*.
        email
            :class:`str` - User's email
        is_email_public
            :class:`bool` - True if your email is set to public in `wakatime`_ settings.
        full_name
            :class:`str` - Full name if available in `wakatime`_ settings.
        has_premium_features
            :class:`bool` - True if user has premium features.
        human_readable_website
            :class:`str` - User's website
        id
            :class:`str` - User's id
        is_email_confirmed
            :class:`bool` - True if user's email is confirmed
        is_hireable
            :class:`bool` - True if user is set to hireable in `wakatime`_
        languages_used_public
            :class:`bool`
        last_heartbeat
            :class:`str` - Last time the user connected to wakatime
        last_plugin
            :class:`str` - Last plugin used by the user - Verbose
        last_plugin_name
            :class:`str` - Last plugin used by the user
        last_project
            :class:`str` - Last project the user worked on
        location
            :class:`str` - user's location if given
        logged_time_public
            :class:`bool`
        modified_at
            Optional[:class:`str`, :class:`NoneType`] - Last time user was modified
        photo
            :class:`str` - user's `wakatime`_ gravatar profile picture
        photo_public
            :class:`bool` - True if user's profile picture is public
        plan
            :class:`str` - user's `wakatime`_ paid plan, most common: basic.
        timeout
            :class:`int`
        timezone
            :class:`str` - user's timezone
        username
            :class:`str` - user's username
        website
            :class:`str` - user's website if given
        writes_only
            :class:`bool`
        slice
            default :class:`NoneType` contains a :class:`list` of days between 2 dates.
        """
    def __init__(self, fp: str):

        self.fp = fp
        self.file = JsonDict(self.fp)
        user_info = self.file.user_data

        self.display_name = user_info.get('display_name')
        self.created_at = user_info.get('created_at')
        self.email = user_info.get('email')
        self.is_email_public = user_info.get('is_email_public')
        self.full_name = user_info.get('full_name')
        self.has_premium_features = user_info.get('has_premium_features')
        self.human_readable_website = user_info.get('human_readable_website')
        self.id = user_info.get('id')
        self.is_email_confirmed = user_info.get('is_email_confirmed')
        self.is_hireable = user_info.get('is_hireable')
        self.languages_used_public = user_info.get('languages_used_public')
        self.last_heartbeat = user_info.get('last_heartbeat')
        self.last_plugin = user_info.get('last_plugin')
        self.last_plugin_name = user_info.get('last_plugin_name')
        self.last_project = user_info.get('last_project')
        self.location = user_info.get('location')
        self.logged_time_public = user_info.get('logged_time_public')
        self.modified_at = user_info.get('modified_at')
        self.photo = user_info.get('photo')
        self.photo_public = user_info.get('photo_public')
        self.plan = user_info.get('plan')
        self.timeout = user_info.get('timeout')
        self.timezone = user_info.get('timezone')
        self.username = user_info.get('username')
        self.website = user_info.get('website')
        self.writes_only = user_info.get('writes_only')

        self.slice = None
        self._raw_day_containers = self.days[0].container_dict  # Just the first one makes it.

    def _fetch_data(self, to_fetch: str, use_slice: bool) -> dict:

        if to_fetch not in self._raw_day_containers:
            raise ContainerNotFound(f"class <'Day()'> has no '{to_fetch}' container, possible containers are:"
                                    f" {list(self._raw_day_containers.keys())}")

        if use_slice and self.slice:
            data = self.slice
        elif use_slice and not self.slice:
            raise ValueError('There is no slice created and sliced is set to True')
        else:
            data = self.days

        temp_dic = {}
        for day in data:
            if not day.is_empty:
                for container in day.container_dict[to_fetch]:
                    if container.name not in temp_dic.keys():
                        temp_dic[container.name] = container.total_time
                    else:
                        temp_dic[container.name] += container.total_time

        return order_dict(temp_dic, True)

    @property
    def days(self) -> List[Day]:
        """
        :property:

        :return: List[:class:`.Day`] - list containing **every** Day class
        """
        return self.file.days

    @property
    def total_worked_days(self) -> int:
        """
        :property:

        :return: :class:`int` - The total amount of days that have activity
        """
        total = 0
        for day in self.days:
            if not day.is_empty:
                total += 1
        return total

    def get_slice(self, date1=None, date2=None) -> Slice:
        """
        :dates: Default :class:`NoneType`, can be either :class:`str` with the following format: YYYY-MM-DD or a :class:`datetime.date` object

        :return: :class:`.Slice`
        """
        _slice = Slice(self.days, date_1=date1, date_2=date2)
        self.slice = _slice.days
        return _slice

    def pie_chart(self, to_fetch: str, num: int =10, sliced=False) -> PieChart:
        """
        Creates a pie chart with the given parameters.

        :param to_fetch: :class:`str` container to search options are :class:`.Day`.container_dict.
        :param num: :class:`int` number of items
        :param sliced: :class:`bool` True if you want to use the data from the sliced object you created beforehand.
        :return: :class:`.PieChart`
        """
        if not self.slice:
            dates = self.days[0], self.days[::-1][0]
        else:
            dates = self.slice[0], self.slice[::-1][0]

        return PieChart(self._fetch_data(to_fetch, sliced), num=num, dates=dates)

    def fetch_data(self, to_fetch: str, sliced: bool) -> dict:
        """
        :param to_fetch: :class:`str` container to search options are :class:`.Day`.container_dict.
        :param sliced: :class:`bool` True if you want to use the data from the sliced object you created beforehand.
        :return: :class:`dict` containing the data.

        Note
        ----
        The fetched data is the total_time of each :class:`.Day` container.(s).


        This is an example of it: ::

            # 'lan' - language
            data = {'python': 253, 'bash': 623}
        """
        return self._fetch_data(to_fetch, sliced)

    def __repr__(self):
        """
        :return: :class:`str` self.class.name(username) (dummy)
        """
        return f'class <{self.__class__.__name__}({self.username})>'

    def __len__(self):
        """
        :return: :class:`int` number of total days, regardless of activity.
        """
        return len(self.days)
