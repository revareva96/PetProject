import datetime
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytz
from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestCheckUUID(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/check_uuid'
    MOCKING_VIEW: str = 'check_uuid'
    uid = 'c7c09599-4043-4148-a129-1ca7885d1e88'

    async def test_check_uuid_get_requests(self, cli: TestClient) -> None:
        # мокаются все запросы в БД и результаты
        with patch(f'app.views.{self.MOCKING_VIEW}.get_session') as mocking_db, \
                patch(f'app.views.{self.MOCKING_VIEW}.update') as mocking_update:
            mocking_db_session = AsyncMock(name='mocking_db_session')
            mocking_db_scalars = Mock(name='mocking_db_scalars')
            mocking_db_results = Mock(name='mocking_db_results')

            # мокаем на условие, что нет результатов в БД
            mocking_db.return_value = mocking_db_session
            mocking_db_session.execute.return_value = mocking_db_scalars
            mocking_db_scalars.scalars.return_value.first.return_value = None
            resp = await cli.get(self.ENDPOINT + f'?confirm={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json = self.get_data(f'check_uuid/{status}.json')
            assert resp_json == outgoing_json

            resp = await cli.get(self.ENDPOINT + f'?recover={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json = self.get_data(f'check_uuid/{status}.json')
            assert resp_json == outgoing_json

            # мокаем на условие, что подтверждение уже было
            mocking_db_results.confirm = True
            mocking_db_scalars.scalars.return_value.first.return_value = mocking_db_results

            resp = await cli.get(self.ENDPOINT + f'?confirm={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json['type'] = 'was verified'
            outgoing_json['message'] = 'Регистрация уже была подтверждена.'
            assert resp_json == outgoing_json

            resp = await cli.get(self.ENDPOINT + f'?recover={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json['type'] = 'was verified'
            outgoing_json['message'] = 'Ссылка недействительна.'
            assert resp_json == outgoing_json

            # мокаем на условие, что просрочено время подтверждения
            utc = pytz.UTC
            mocking_db_results.confirm = False
            mocking_db_results.confirm_time = utc.localize(datetime.datetime(2021, 11, 11, 0, 0, 0))

            resp = await cli.get(self.ENDPOINT + f'?confirm={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json = self.get_data(f'check_uuid/{status}.json')
            assert resp_json == outgoing_json

            resp = await cli.get(self.ENDPOINT + f'?recover={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            assert resp_json == outgoing_json

            # корректный запрос

            mocking_db_results.confirm_time = utc.localize(datetime.datetime(2031, 11, 11, 0, 0, 0))

            resp = await cli.get(self.ENDPOINT + f'?confirm={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{200}.json')
            # дополнительно проверяем, что был вызван update для confirm
            mocking_update.assert_called_once()

            resp = await cli.get(self.ENDPOINT + f'?recover={self.uid}')
            status = resp.status
            resp_json = await resp.json()
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{status}.json')

        # проверка на корректную валидацию входных параметров
        resp = await cli.get(self.ENDPOINT + f'?confirm={self.uid}&?confirm={self.uid}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

        resp = await cli.get(self.ENDPOINT + '?recover=not_uuid')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

    async def test_check_uuid_post_requests(self, cli: TestClient) -> None:
        resp = await cli.post(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{status}.json')
