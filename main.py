from aiohttp import web

from app import make_app
from app.config.config import get_settings

settings = get_settings()

app_port = settings.app_port

if __name__ == '__main__':
    web.run_app(make_app(), port=app_port)
