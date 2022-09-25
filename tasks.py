from invoke import task


@task
def start(ctx):
    ctx.run("cd src && flask run", pty=True)


@task
def lint(ctx):
    ctx.run("pylint src", pty=True)


@task
def initialize_database(ctx):
    ctx.run("cd src && python3 init_db.py", pty=True)
