import datetime
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from aiohttp.test_utils import TestClient

from app import make_app


class BaseTestState:
    FIXTURES_PATH: Path
    ENDPOINT: str
    MOCKING_VIEW: str

    def get_data(self, file_name: str) -> dict:
        with open(self.FIXTURES_PATH / f'{file_name}') as file:
            data = json.loads(file.read())
        return data

    @pytest.fixture()
    async def cli(self, aiohttp_client) -> TestClient:
        app = await make_app()
        return await aiohttp_client(app)

    @pytest.fixture()
    def mocking_datetime(self):
        with patch(f'app.views.{self.MOCKING_VIEW}.datetime') as mock_datetime:
            faked_data = datetime.datetime(2021, 11, 11, 0, 0, 0)
            mock_datetime.utcnow.return_value = faked_data
            mock_datetime.strptime = datetime.datetime.strptime  # todo: как мокать не все методы у объекта?
            mock_datetime.utcnow.side_effect = lambda *args, **kwargs: faked_data
            yield mock_datetime

    @pytest.fixture()
    def mocking_update(self):
        with patch(f'app.views.{self.MOCKING_VIEW}.update') as mocking_update:
            yield mocking_update

    @pytest.fixture()
    def mocking_send_msg(self):
        with patch(f'app.views.{self.MOCKING_VIEW}.send_message_in_thread') as mocking_sending:
            mocking_sending.return_value = lambda _: _
            yield mocking_sending
