from fabric.api import task


@task()
def shell():
    from app.db import db
    from app import models
    from app.flask_app import flask_app
    context = dict(db=db, flask_app=flask_app, models=models)
    banner = "~~~ Digital Palette API Shell ~~~"
    try:
        # 0.10.x
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed(banner=banner)
        ipshell(global_ns=dict(), local_ns=context)
    except ImportError:
        # 0.12+
        from IPython import embed
        embed(banner1=banner, user_ns=context)
