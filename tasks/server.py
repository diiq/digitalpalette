from flask_failsafe import failsafe
from fabric.api import task, local


@failsafe
def server_app():
    from api import app
    return app


@task(default="true")
def server(port=5000):
    """Runs a development server."""
    server_app().run()
