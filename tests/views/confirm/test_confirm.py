import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from aiohttp.test_utils import TestClient

from tests import BaseTestState


class TestConfirm(BaseTestState):
    FIXTURES_PATH: Path = Path(os.path.dirname(__file__)).parent  # + '/common_data'
    ENDPOINT: str = '/confirm'
    MOCKING_VIEW: str = 'confirm'
    uid = 'c7c09599-4043-4148-a129-1ca7885d1e88'

    async def test_confirm_post_requests(self, cli: TestClient, mocking_send_msg: Mock, mocking_update: Mock) -> None:
        with patch(f'app.views.{self.MOCKING_VIEW}.get_session') as mocking_db:
            mocking_db_session = AsyncMock(name='mocking_db_session')
            mocking_db_scalars = Mock(name='mocking_db_scalars')
            mocking_db_results = Mock(name='mocking_db_results')

            # мокаем на условие, что нет результатов в БД, recover
            mocking_db.return_value = mocking_db_session
            mocking_db_session.execute.return_value = mocking_db_scalars
            mocking_db_scalars.scalars.return_value.first.return_value = None

            resp = await cli.post(
                self.ENDPOINT, data=b'{"login_or_email": "revareva91",'
                                    b'"type": "recover"}',
            )
            status = resp.status
            resp_json = await resp.json()
            outgoing_json = self.get_data(f'{self.MOCKING_VIEW}/{status}.json')
            assert status == 400
            assert resp_json == outgoing_json

            # успешный запрос, recover
            mocking_db_scalars.scalars.return_value.first.side_effect = [mocking_db_results, False]
            mocking_db_session.add = mocking_db_scalars
            resp = await cli.post(
                self.ENDPOINT, data=b'{"login_or_email": "revareva91",'
                                    b'"type": "recover"}',
            )
            mocking_send_msg.assert_called_once()
            mocking_db_session.add.assert_called_once()
            status = resp.status
            resp_json = await resp.json()
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{status}.json')

            # пользователь уже подтвердил регистрацию, confirm
            mocking_db_results.confirm = True
            mocking_db_scalars.scalars.return_value.first.side_effect = [mocking_db_results, mocking_db_results]
            resp = await cli.post(
                self.ENDPOINT, data=b'{"login_or_email": "revareva91",'
                                    b'"type": "confirm"}',
            )
            status = resp.status
            resp_json = await resp.json()
            assert status == 400
            outgoing_json['message'] = 'Пользователь уже подтвердил регистрацию.'
            assert resp_json == outgoing_json

            # успешный вызов, confirm
            mocking_db_results.confirm = False
            mocking_db_scalars.scalars.return_value.first.side_effect = [mocking_db_results, mocking_db_results]
            resp = await cli.post(
                self.ENDPOINT, data=b'{"login_or_email": "revareva91",'
                                    b'"type": "confirm"}',
            )
            mocking_update.assert_called_once()
            assert len(mocking_send_msg.mock_calls) == 2
            status = resp.status
            resp_json = await resp.json()
            assert status == 200
            assert resp_json == self.get_data(f'common_data/{status}.json')

        # проверка на корректную валидацию входных параметров
        resp = await cli.post(
            self.ENDPOINT, data=b'{"login_or_email": "revareva91",'
                                b'"type": "test"}',
        )
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

        resp = await cli.post(self.ENDPOINT, data=b'{"type": "test"}')
        status = resp.status
        resp_json = await resp.json()
        assert status == 400
        assert resp_json == self.get_data(f'common_data/{status}.json')

    async def test_login_get_requests(self, cli: TestClient) -> None:
        resp = await cli.get(self.ENDPOINT)
        status = resp.status
        resp_json = await resp.json()
        assert status == 405
        assert resp_json == self.get_data(f'common_data/{resp.status}.json')
