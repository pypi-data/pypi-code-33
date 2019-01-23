from invoke import task
from reliabilly.settings import Constants

TF_VERSION = '0.11.8'
TERRAFORM_UPDATE_CMD = 'rm -rf ~/terraform' \
                        f'&& terraform_url=https://releases.hashicorp.com/' \
                       f'terraform/{TF_VERSION}/' \
                       f'terraform_{TF_VERSION}_linux_amd64.zip' \
                       ' && curl -o ~/terraform.zip $terraform_url ' \
                       '&& sudo unzip -o ~/terraform.zip -d /usr/bin'

TERRAFORM_INIT_CMD = 'cd terraform && rm -rf .terraform && terraform init ' \
                     '-backend-config=backend_{environment}.tfvars ' \
                     '-reconfigure'

TERRAFORM_PLAN_CMD = 'cd terraform && terraform plan'

TERRAFORM_APPLY_CMD = "cd terraform && " \
                      "terraform apply -var " \
                      "'environment=\"{environment}\"' " \
                        "-var 'release_number=\"{version}\"' " \
                        "-var 'build_number=\"{build_number}\"' -auto-approve"

PACKAGE_BUILD_CMD = 'python setup.py bdist_wheel'
PACKAGE_UPLOAD_CMD = f"twine upload dist/* --repository-url {Constants.PYTHON_PACKAGE_REPO}"


@task
def update_terraform(ctx):
    ctx.run(TERRAFORM_UPDATE_CMD)


@task
def terraform_deploy(ctx, environment, version, build_number):
    if environment == 'uat' or 'prod':
        update_terraform(ctx)
    ctx.run(TERRAFORM_INIT_CMD.format(environment=environment))
    ctx.run(TERRAFORM_APPLY_CMD.format(environment=environment, version=version, build_number=build_number))


@task
def terraform_plan(ctx, environment):
    update_terraform(ctx)
    ctx.run(TERRAFORM_INIT_CMD.format(environment=environment))
    ctx.run(TERRAFORM_PLAN_CMD)


@task
def publish_module(ctx):
    ctx.run('pip freeze')
    ctx.run(PACKAGE_BUILD_CMD)
    ctx.run(PACKAGE_UPLOAD_CMD)
