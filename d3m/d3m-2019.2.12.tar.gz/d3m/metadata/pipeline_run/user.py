import typing


class User:
    def __init__(self, id_: str, chosen_by_user: bool = False, rationale: str = None) -> None:
        self.id_: str = id_
        self.chosen_by_user: bool = chosen_by_user
        self.rationale: str = rationale

    def to_json_structure(self) -> typing.Dict:
        return {
            'id': self.id_,
            'chosen': self.chosen_by_user,
            'rationale': self.rationale
        }

    @staticmethod
    def get_from_user_description(user_description: typing.Dict) -> 'User':
        user = User(user_description['id'])
        if 'rationale' in user_description:
            user.rationale = user_description['rationale']
        if 'chosen' in user_description:
            user.chosen_by_user = user_description['chosen']
        return user
