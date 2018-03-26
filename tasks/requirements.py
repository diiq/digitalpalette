from fabric.api import task, local


@task
def requirements():
    """Installs python packages from requirements.txt"""
    local("pipenv install")
