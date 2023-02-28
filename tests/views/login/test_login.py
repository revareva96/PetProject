import os
from pathlib import Path
from unittest.mock import Mock

from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestLogin(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/login'
    MOCKING_VIEW: str = 'login'

    async def test_login_post_requests(self, cli: TestClient, mocking_datetime: Mock) -> None:
        resp = await cli.post(
            self.ENDPOINT, data=b'{"login_or_email": "user",\
                                      "password": "very_difficult_password"}',
        )
        status = resp.status
        resp_json = await resp.json()
        assert status == 200
        assert resp_json == self.get_data(f'login/{resp.status}.json')

        resp = await cli.post(self.ENDPOINT, data=b'{"login_or_email": "revareva96"}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')

        resp = await cli.post(
            self.ENDPOINT, data=b'{"login_or_email": "revareva96",\
                                              "password": "abracadabra"}',
        )
        status = resp.status
        resp_json = await resp.json()
        assert status == 401
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')

        # внутрення ошибка, когда отправлен не json формат
        resp = await cli.post(self.ENDPOINT, data=b'{"login_or_email": "revareva96"')
        status = resp.status
        resp_json = await resp.json()
        assert status == 500
        assert resp_json == self.get_data(f'login/{resp.status}.json')

        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')

        # тест на регистрацию, так как здесь реальное подключение к БД, а не моки
        data = b'{"mail": "test@mail.ru",' \
               b'"name": "test",' \
               b'"login": "revareva96",' \
               b'"password": "123"}'
        resp = await cli.post('/register', data=data)
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        outgoing_message = {
            'type': 'already exist',
            'message': 'Пользователь с таким логином/почтовым ящиком уже существует.',
        }
        assert resp_json == outgoing_message

    async def test_login_get_requests(self, cli: TestClient) -> None:
        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')
