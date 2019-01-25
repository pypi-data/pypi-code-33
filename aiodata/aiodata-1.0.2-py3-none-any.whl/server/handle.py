import peewee


__all__ = ('Handle',)


class Handle:

    __slots__ = ('_seed', '_authorize', '_error')

    def __init__(self, seed, authorize, error):

        self._seed = seed

        self._authorize = authorize

        self._error = error

    _low = 0

    async def _execute(self, accept, action, request):

        self._authorize(request)

        try:

            payload = await request.json()

        except:

            raise self._error('invalid data')

        try:

            (keys, *others) = payload

        except (TypeError, ValueError):

            raise self._error('invalid payload')

        if not isinstance(keys, list):

            raise self._error('invalid keys')

        if accept and len(others) > self._low:

            data = others[self._low]

            if not isinstance(data, dict):

                raise self._error('invalid data', index)

            act = action(keys, **data)

        else:

            act = action(keys)

        try:

            data = await act

        except peewee.DatabaseError as error:

            raise self._error('database error', str(error))

        return data

    _get = False

    def get(self, request):

        return self._execute(self._get, self._seed.get, request)

    _create = True

    def create(self, request):

        return self._execute(self._create, self._seed.create, request)

    _update = True

    def update(self, request):

        return self._execute(self._update, self._seed.update, request)

    _delete = False

    def delete(self, request):


        return self._execute(self._delete, self._seed.delete, request)
