from invoke import task


@task
def publish(ctx):
    print('Building python package...')
    ctx.run('python3 setup.py sdist')
    print('Pushing package to pypi...')
    ctx.run('twine upload dist/*')
