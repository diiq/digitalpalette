from fabric.api import local, settings, hide, task

from config import config


@task
def style():
    """Runs pep8 to check python standard style"""
    with hide("running", "warnings"):
        local("flake8 %s --max-complexity 10 "
              "--ignore=E711,E712,E226 --exclude \".git,.#*\""
              % config.project_root())


@task
def setup():
    with hide("running", "stdout"):
        with settings(warn_only=True):
            local("honcho run -e .env.test fab db.drop")
        local("honcho run -e .env.test fab db.new")


@task
def unit(args=""):
    """Runs unit tests"""
    setup()
    with hide("running"):
        local("honcho run -e .env.test nosetests --rednose %s" % args)


@task(default=True)
def all():
    """Runs all tests; style, unit, and integration."""
    setup()
    with settings(warn_only=True):
        print("Testing style...")
        style()
        print("Testing units...")
        unit()


@task
def auto(args=None):
    """Runs unit tests"""
    setup()
    with hide("running"):
        if args:
            local("honcho run -e .env.test sniffer -x --rednose -x%s" % args)
        else:
            local("honcho run -e .env.test sniffer -x --rednose")
