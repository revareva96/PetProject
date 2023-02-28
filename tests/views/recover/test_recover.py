import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestRecover(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/recover'
    MOCKING_VIEW: str = 'recover'
    data = b'{"uuid": "c7c09599-4043-4148-a129-1ca7885d1e88",' \
           b'"password": "123"}'

    async def test_recover_post_requests(self, cli: TestClient) -> None:
        with patch(f'app.views.{self.MOCKING_VIEW}.get_session') as mocking_db:
            mocking_db_session = AsyncMock(name='mocking_db_session')
            mocking_db_scalars = Mock(name='mocking_db_scalars')
            mocking_db_results = Mock(name='mocking_db_results')

            mocking_db.return_value = mocking_db_session
            mocking_db_session.execute.return_value = mocking_db_scalars
            mocking_db_scalars.scalars.return_value.first.return_value = mocking_db_results
            resp = await cli.post(self.ENDPOINT, data=self.data)
            status = resp.status
            resp_json = await resp.json()
            assert mocking_db_session.execute.call_count == 3
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{status}.json')

            mocking_db_scalars.scalars.return_value.first.return_value = None
            resp = await cli.post(self.ENDPOINT, data=self.data)
            status = resp.status
            resp_json = await resp.json()
            assert status == 500
            outgoing_json = self.get_data(f'common_data/{status}.json')
            outgoing_json['message'] = "'NoneType' object has no attribute 'id'"
            assert resp_json == outgoing_json

        # проверка на корректную валидацию входных параметров
        resp = await cli.post(self.ENDPOINT, data=b'{"uuid": "c7c09599-4043-4148-a129-1ca7885d1e88"}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

        resp = await cli.post(self.ENDPOINT, data=b'{"password": "123"}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

    async def test_recover_get_requests(self, cli: TestClient) -> None:
        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')
