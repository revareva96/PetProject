import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestRegister(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/register'
    MOCKING_VIEW: str = 'register'
    data = b'{"mail": "test@mail.ru",' \
           b'"name": "test",' \
           b'"login": "test_login",' \
           b'"password": "123"}'

    async def test_register_post_requests(self, cli: TestClient, mocking_send_msg: Mock) -> None:
        with patch(f'app.views.{self.MOCKING_VIEW}.get_session') as mocking_db:
            mocking_db_session = AsyncMock(name='mocking_db_session')
            mocking_db_scalars = Mock(name='mocking_db_scalars')
            mocking_db_results = Mock(name='mocking_db_results')

            # корректный запрос
            mocking_db.return_value = mocking_db_session
            mocking_db_session.execute.return_value = mocking_db_scalars
            mocking_db_session.add = mocking_db_scalars
            mocking_db_scalars.scalars.return_value.first.return_value = mocking_db_results
            resp = await cli.post(self.ENDPOINT, data=self.data)
            assert mocking_db_session.add.call_count == 3
            status = resp.status
            resp_json = await resp.json()
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{status}.json')

        # проверка на корректную валидацию входных параметров
        resp = await cli.post(self.ENDPOINT, data=b'{"name": "test"}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

    async def test_register_get_requests(self, cli: TestClient) -> None:
        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')
