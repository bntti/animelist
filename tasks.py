from invoke import task


@task
def start(ctx):
    ctx.run('gunicorn --chdir animelist "app:create_app()"', pty=True)


@task
def dev(ctx):
    ctx.run("cd animelist && flask run", pty=True)


@task
def lint(ctx):
    ctx.run("pylint animelist", pty=True)


@task
def initialize_database(ctx):
    ctx.run("cd animelist && python3 init_db.py", pty=True)
