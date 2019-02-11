import requests
import json
from .game_result import GameResult


class RAWG:

    def __init__(self, user_agent):
        self.user_agent = user_agent

    def request(self, param: str, url="https://rawg.io/api/games"):
        headers = {
            'User-Agent': self.user_agent
        }
        response = requests.get(url + param, headers=headers)
        return json.loads(response.text)

    def search_request(self, query, num_results=1, additional_param=""):
        param = "?page_size={num}&search={query}&page=1".format(
            num=num_results, query=query)
        param = param + additional_param
        return self.request(param)

    def game_request(self, name, additional_param=""):
        param = "/{name}".format(name=name)
        param = param + additional_param
        return self.request(param)

    def search(self, query, num_results=5, additional_param=""):
        json = self.search_request(query, num_results, additional_param)
        results = [GameResult(j, self.user_agent)
                   for j in json.get("results", [])]
        return results
