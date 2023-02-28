import os
from pathlib import Path
from unittest.mock import Mock

from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestCheckToken(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/check_token'
    MOCKING_VIEW: str = 'check_token'

    async def test_check_token_get_requests(self, cli: TestClient, mocking_datetime: Mock) -> None:
        # передан корректный токен
        resp = await cli.get(
            self.ENDPOINT, headers={
                'Authorization': 'Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                                 'eyJ1c2VybmFtZSI6InZsYWRpbWlyIiwiZXhwaXJlZCI6IjIwMjEtMTEtMTEgMDA6MDA6MDAifQ.'
                                 '_rIOuCARfMj3w8HDP8I7cnWLquCvBKja5RwtoLtoAXA',
            },
        )

        status = resp.status
        resp_json = await resp.json()
        assert status == 200
        assert resp_json == self.get_data(f'common_data/{status}.json')

        # проверка на несоответствие сигнатур
        resp = await cli.get(self.ENDPOINT, headers={'Authorization': 'Basic 123'})
        status = resp.status
        resp_json = await resp.json()
        assert status == 401
        assert resp_json == self.get_data(f'common_data/{status}.json')

        # проверка на просрочку токена
        resp = await cli.get(
            self.ENDPOINT,
            headers={
                'Authorization':
                    'Basic eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
                    'eyJ1c2VybmFtZSI6InZsYWRpbWlyIiwiZXhwaXJlZCI6IjIwMjEtMDEtMTEgMDA6MDA6MDAifQ.'
                    'jRRebPjYdCEqNJqEUumkBTpnsccKVv_pvxLxheN2T1k',
            },
        )
        status = resp.status
        resp_json = await resp.json()
        assert status == 401
        assert resp_json == self.get_data(f'common_data/{status}.json')
        # токен не передан
        resp = await cli.get(self.ENDPOINT, headers={'Authorization': 'Basic undefined'})
        status = resp.status
        resp_json = await resp.json()
        assert status == 401
        assert resp_json == self.get_data(f'common_data/{status}.json')

    async def test_check_token_post_requests(self, cli: TestClient) -> None:
        resp = await cli.post(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{status}.json')
