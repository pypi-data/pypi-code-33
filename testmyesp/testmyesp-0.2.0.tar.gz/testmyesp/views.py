
import asyncio
import datetime

from aiohttp import web
from aiohttp_apispec import docs, use_kwargs, marshal_with

from colibris import api
from colibris.schemas import many_envelope
from colibris.shortcuts import get_object_or_404

from testmyesp import assets
from testmyesp import constants
from testmyesp import flashimages
from testmyesp import models
from testmyesp import schemas


@docs(tags=['Clients'],
      summary='Reveal details about the current client')
@marshal_with(schemas.ClientSchema())
def get_me(request):
    if request.account:
        result = schemas.ClientSchema().dump(request.account)

    else:
        result = None

    return web.json_response(result)


@docs(tags=['Jobs'],
      summary='List all jobs')
@marshal_with(many_envelope(schemas.ShowJobSchema))
def list_jobs(request):
    jobs = models.Job.select().order_by(models.Job.added_moment.asc())

    # regular users see only their jobs
    if request.account.role == constants.ROLE_REGULAR:
        jobs = jobs.where(models.Job.client == request.account)

    result = schemas.ShowJobSchema(many=True).dump(list(jobs))

    return web.json_response(result)


@docs(tags=['Jobs'],
      summary='Reveal details about a specific job')
@marshal_with(schemas.ShowJobSchema())
def get_job(request):
    job_id = request.match_info['id']
    job = get_object_or_404(models.Job, job_id, select_related=[models.Client])

    # regular users see only their jobs
    exclude = ()
    if request.account.role == constants.ROLE_REGULAR:
        exclude = ('client',)
        if job.client != request.account:
            raise api.ForbiddenException()

    result = schemas.ShowJobSchema(exclude=exclude).dump(job)

    return web.json_response(result)


@docs(tags=['Jobs'],
      summary='Add a new job')
@use_kwargs(schemas.AddJobSchema())
@use_kwargs(schemas.AddJobSchemaQuery(), locations=['query'])
@marshal_with(schemas.AddJobSchema())
async def add_job(request):
    flash_images_json = schemas.FlashImageSchema(many=True).dumps(request.data['flash_images'])
    assets_json = schemas.AssetSchema(many=True).dumps(request.data['assets'])
    test_cases_json = schemas.TestCaseSchema(many=True).dumps(request.data['test_cases'])

    job = models.Job(client=request.account,
                     state=constants.JOB_STATE_PENDING,
                     added_moment=datetime.datetime.utcnow().replace(microsecond=0),
                     timeout=request.data['timeout'],
                     continue_on_failure=request.data['continue_on_failure'],
                     flash_images_json=flash_images_json,
                     assets_json=assets_json,
                     test_cases_json=test_cases_json)
    job.save()
    job.logger.debug('added')

    query = schemas.AddJobSchemaQuery().load(dict(request.query))
    if query['wait']:
        job.logger.debug('waiting for job completion')

        while True:
            await asyncio.sleep(5)
            job = models.Job.select().where(models.Job.id == job.id).get()
            if job.state in (constants.JOB_STATE_SUCCEEDED,
                             constants.JOB_STATE_FAILED,
                             constants.JOB_STATE_CANCELLED):

                break

        job.logger.debug('completed')

    result = schemas.ShowJobSchema(exclude=('client',)).dump(job)

    return web.json_response(result, status=201)


@docs(tags=['Jobs'],
      summary='Cancels a job')
def cancel_job(request):
    job_id = request.match_info['id']
    job = get_object_or_404(models.Job, job_id, select_related=[models.Client])

    # regular users can cancel only their jobs
    if request.account.role == constants.ROLE_REGULAR:
        if job.client != request.account:
            raise api.ForbiddenException()

    if job.state != constants.JOB_STATE_PENDING:
        raise api.InvalidRequest('invalid_state', 'Invalid job state.')

    job.logger.debug('cancelled')
    job.state = constants.JOB_STATE_CANCELLED
    job.ended_moment = datetime.datetime.utcnow()
    job.save()

    return web.json_response(status=204)


@docs(tags=['Assets'],
      summary='Obtain the content of a job asset')
async def get_asset(request):
    job_id = request.match_info['id']
    asset_name = request.match_info['name']

    job = get_object_or_404(models.Job, job_id, select_related=[models.Client])

    # assets are only available while job is executing
    if job.state not in (constants.JOB_STATE_EXECUTING,
                         constants.JOB_STATE_FLASHING):
        raise api.NotFoundException(resource='asset')

    headers = {'Content-Disposition': 'Attachment;filename={}'.format(asset_name)}

    flash_images = schemas.FlashImageSchema(many=True).loads(job.flash_images_json)
    flash_images_by_name = {f['name']: f for f in flash_images}
    flash_image_dict = flash_images_by_name.get(asset_name)
    if flash_image_dict is not None:
        flash_image = flashimages.FlashImage(job, **flash_image_dict)
        await flash_image.ensure_content_async()

        return web.Response(headers=headers, body=flash_image.content)

    assets_list = schemas.AssetSchema(many=True).loads(job.assets_json)
    assets_by_name = {a['name']: a for a in assets_list}
    asset_dict = assets_by_name.get(asset_name)
    if asset_dict is not None:
        asset = assets.Asset(job, **asset_dict)

        return web.Response(headers=headers, body=asset.content)

    raise api.NotFoundException(resource='asset')
