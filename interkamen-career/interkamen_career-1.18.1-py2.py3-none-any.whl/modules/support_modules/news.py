#!/usr/bin/env python3
"""
News module. Show news for users.

.show_new_news() - show new news

.show_actual_news() - showing all existance news.
"""

import os
from .standart_functions import (
    BasicFunctionsS
    as BasF_S
)


class News(BasF_S):
    """Show news to users."""

    __slots__ = [
        'news_path',
        'news_memory',
        'news_memory_file',
        'user',
    ]

    def __init__(self, user):
        self.user = user
        # Path for news files.
        self.news_path = super().get_root_path() / 'news'
        # Path for information of showing to users.
        self.news_memory = super().get_root_path() / 'data' / 'news_memory'
        if (not os.listdir(self.news_path) or
                not self.news_memory.exists()):
            self.news_memory_file = {}
            super().dump_data(
                data_path=self.news_memory,
                base_to_dump=self.news_memory_file,
                user=user,
            )
        else:
            self.news_memory_file = super().load_data(
                data_path=self.news_memory,
                user=user,
            )

    @classmethod
    def _print_news(cls, new_news):
        """Print news to screen."""
        print("\033[93m[НОВОСТИ]\033[0m\n")
        while True:
            print('\n', '-' * 80)
            if not new_news:
                break
            print(new_news[0])
            new_news = new_news[1:]
            choose = input("\n[E] - выход"
                           "\n[ENTER] - дальше: ")
            if choose.lower() in ['e', 'е']:
                break

    def _add_news_to_user(self, user_login, news):
        """Add information about showing news to user."""
        self.news_memory_file[user_login].append(news)

    def _check_if_user_in_file(self, user_login):
        """Check if user in memory file."""
        user_news = []
        if user_login in self.news_memory_file:
            user_news = self.news_memory_file[user_login]
        else:
            self.news_memory_file[user_login] = []
        return user_news

    def show_new_news(self, user_login):
        """Show news to user if it hasn't allredy shown."""
        new_news = []
        user_news = self._check_if_user_in_file(user_login)
        for news in sorted(os.listdir(self.news_path)):
            if news not in user_news:
                new = self.news_path.joinpath(news).read_text(encoding='utf-8')
                new_news.append(new)
                self._add_news_to_user(user_login, news)
                super().dump_data(
                    data_path=self.news_memory,
                    base_to_dump=self.news_memory_file,
                    user=self.user,
                )
        if new_news:
            self._print_news(new_news)

    def show_actual_news(self):
        """Show all news that actual."""
        new_news = []
        if os.listdir(self.news_path):
            for news in sorted(os.listdir(self.news_path)):
                with open(os.path.join(self.news_path, news), 'r',
                          encoding='utf-8') as file:
                    new_news.append(file.read())
        if new_news:
            self._print_news(new_news)
        else:
            print("Новых новостей нет.")
