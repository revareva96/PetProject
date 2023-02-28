from aiohttp.web import Application, get, json_response
from aiohttp_middlewares import cors_middleware
from aiohttp_swagger import setup_swagger

from app.config.config import get_settings
from app.middlewares.middlewares import CustomMiddleware
from app.views import check_token, check_uuid, confirm, login, recover, register, store

settings = get_settings()

cors_host = settings.cors_host
app_port = settings.app_port


def setup_views(app: Application) -> None:
    login.LoginView.create_documentation()
    app.router.add_view('/login', login.LoginView)

    store.StoreView.create_documentation()
    app.router.add_view('/store', store.StoreView)

    register.RegisterView.create_documentation()
    app.router.add_view('/register', register.RegisterView)

    check_token.CheckTokenView.create_documentation()
    app.router.add_view('/check_token', check_token.CheckTokenView)

    check_uuid.CheckUUIDView.create_documentation()
    app.router.add_view('/check_uuid', check_uuid.CheckUUIDView)

    confirm.ConfirmView.create_documentation()
    app.router.add_view('/confirm', confirm.ConfirmView)

    recover.RecoverView.create_documentation()
    app.router.add_view('/recover', recover.RecoverView)


async def make_app() -> Application:
    middleware_handler = CustomMiddleware()
    app = Application(
        middlewares=[
            cors_middleware(
                origins=[cors_host], allow_headers='*', expose_headers=(
                    'Authorization',
                ),
            ),
            middleware_handler.middleware,
        ],
    )
    setup_views(app)
    app.add_routes([
        get(
            '/', lambda _: json_response({
                'status': 'up',
            }),
        ),
    ])
    setup_swagger(app, swagger_url='swagger', ui_version=3)
    return app
