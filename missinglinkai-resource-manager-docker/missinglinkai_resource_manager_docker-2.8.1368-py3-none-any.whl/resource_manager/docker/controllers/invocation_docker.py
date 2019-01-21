import asyncio
import logging
import re
import uuid

from docker.errors import APIError
from missinglink.crypto import Asymmetric

from missinglink.resource_manager.docker.config import ADMIN_VOLUME
from missinglink.resource_manager.docker.controllers.docker.async_docker_container import AsyncDockerContainer
from missinglink.resource_manager.docker.controllers.docker.docker_wrapper import DockerWrapper
from .aws.ecr import Ecr
from .crypto_helper import CryptoHelper
from .errors import PrepareDockerEnvironmentException
from .templates import build_user_command, build_root_command

logger = logging.getLogger(__name__)


class InvocationDocker:

    def get_or_create_volume(self, name, labels=None):
        cur_volume = self.docker_wrapper.volume(name)
        if cur_volume:
            return cur_volume
        labels = labels or {}
        labels.update(AsyncDockerContainer.get_container_env(self.active_config))

        return self.docker_wrapper.create_volume(name, labels=labels)

    async def run_with_callbacks_and_validate_result(self, name, **kwargs):
        execution_kwargs = dict(self.init_kwargs)
        execution_kwargs.update(kwargs)
        execution_kwargs['stage_name'] = name
        execution_kwargs['job_id'] = self.invocation_id
        try:
            container = await  AsyncDockerContainer.create_and_run(**execution_kwargs)
            return await self.validate_exit_state(name, container.exit)
        except APIError as ex:
            logger.exception(ex)
            return ex.explanation, -500

    async def validate_exit_state(self, step_name, exit_state):
        logger.debug('validate_exit_state: %s = %s', step_name, exit_state)
        exit_result = exit_state[1]
        if isinstance(exit_result, dict) and 'StatusCode' in exit_result:
            exit_state = [exit_state[0], exit_result['StatusCode'], exit_result.get('Error')]
        elif not isinstance(exit_result, int):
            raise ValueError(f'Unknown exit_state: {exit_state} in {step_name}')
        if exit_state[1] != 0:
            self.errors.append((step_name, exit_state))
            raise PrepareDockerEnvironmentException('Failed in step %s: %s' % (step_name, exit_state))
        else:
            await self.log_cb(f' ... Done {exit_state}', step_name=step_name)
            return exit_state

    ecr_repo_re = r"(.*)\.dkr\.ecr\.(.*)\.amazonaws\.com/(.*)"

    async def _docker_login(self, user, password, endpoint):
        endpoint = endpoint if endpoint is not None else 'https://index.docker.io/v1/'

        volumes = dict(ADMIN_VOLUME)
        volumes[self.root_mount[1]] = {'bind': '/root'}
        await self.run_with_callbacks_and_validate_result(
            name=f'docker Login to: `{endpoint}`',
            image="docker",
            command=f"docker login -u {user} -p {password} {endpoint}",
            volumes=volumes,
        )

    async def try_ecr_image_auth_if_needed(self, image):
        aws_repo = re.match(self.ecr_repo_re, image)

        if not aws_repo:
            return

        account, region, actual_image = aws_repo.groups()
        user, password, endpoint = Ecr.login(account, region, actual_image)

        if user is password is None:
            return

        return await self._docker_login(user, password, endpoint)

    async def decrypt_data(self):
        await self.setup_root()

        if not self.encrypted or not self.encrypted.get('data'):
            await self.log_cb('No encrypted data found', step_name='Decrypting Environment')
            return

        res = self.crypto_helper.decrypt_invocation(self)
        await self.log_cb(f'Data Decrypted. {len(res)} items decrypted', step_name='Decrypting Environment')
        try:
            self.secured_data = {'file': {}, 'env': {}, 'docker': {}}
            for item in res:
                type_ = item[b'type'].decode('utf-8')
                path_ = item[b'path'].decode('utf-8')
                data_ = item[b'data']
                if type_ not in self.secured_data:
                    await self.log_cb(f'WARNING: secure item of type {type_} is not supported', step_name='Decrypting Environment')
                    continue

                self.secured_data[type_][path_] = data_

            for k, v in self.secured_data['env'].items():
                await self.log_cb(f'Adding secured env: {k}')
                self.env[k] = v.decode('utf-8')

            for k, v in self.secured_data['docker'].items():
                await self.log_cb(f'Adding docker login for server: {k}')
                user, password = v.decode('utf-8').split(';', maxsplit=1)
                await self._docker_login(user, password, k)

        except Exception as ex:
            logger.exception(str(ex))
            raise

        return await self.setup_root()

    async def docker_login_from_config(self):
        tasks = []
        for host, data in self.active_config.general.get('docker_auth', {}).items():
            task = self._docker_login(data.get('user'), data.get('pass'), host)
            tasks.append(task)

        if tasks:
            await  asyncio.wait(tasks)

    async def pull_image(self, image, force=False):
        step_name = f'Pull Image: `{image}`'
        if not force and self.docker_wrapper.image(image):
            await self.log_cb(f'Skipping pull of {image}, already present', step_name=step_name)
            return

        volumes = dict(ADMIN_VOLUME)
        if self.root_mount:
            volumes[self.root_mount[1]] = {'bind': '/root'}

        await self.docker_login_from_config()
        await self.try_ecr_image_auth_if_needed(image)
        await self.log_cb(f'Pulling Image ... ', step_name=step_name)

        return await self.run_with_callbacks_and_validate_result(
            name=step_name,
            image="docker",
            command=f"docker pull {image}",
            volumes=volumes,
        )

    def _skip_data_clone(self):
        if self.data_query is None or self.data_volume is None:
            return True

        if self.data_use_iterator:
            return True

        return False

    async def clone_data(self):
        if self._skip_data_clone():
            await self.log_cb(f'Skipping data clone', step_name='clone_data')
            return None

        mount_path, volume_id = self.build_artifact_volume('/data', {'volume': self.data_volume, 'query': self.data_query})
        data_mount = {volume_id: {'bind': '/data'}}
        return await self.run_ml_command(data_mount, 'data', 'clone', str(self.data_volume), '--query', self.data_query, '--dest-folder', self.data_dest_folder, '--no-progressbar')

    async def run_ml_command(self, mounts, *args, update_ml=True):
        args = [str(x) for x in args]
        await self.pull_image(self.active_config.general.missinglink_image, update_ml)
        exec_args = []
        mounts[self.root_mount[1]] = {'bind': "/root"}

        if self.active_config.general.ml_prefix is not None:
            exec_args.append('-cp')
            exec_args.append(self.active_config.general.ml_prefix)

        logger.info(f"Run ml command {args}: {mounts}")
        return await  self.run_with_callbacks_and_validate_result(
            f'ml_command: {args}',
            image=self.active_config.general.missinglink_image,
            command=exec_args + list(args),
            volumes=mounts,
        )

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)

    def __init__(self, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        # Required params
        self.invocation_id = kwargs.pop('invocation_id')
        self.org = kwargs.pop('org')
        self.docker_wrapper = kwargs.pop('docker_wrapper', DockerWrapper.get())
        self.active_config = kwargs.pop('active_config')
        self.project_id = str(kwargs.pop('project_id', self.invocation_id))
        # CACHE
        self.cache_volume_name = f"{self.active_config.general.config_volume}_cache"
        self.get_or_create_volume(self.cache_volume_name)

        # encrypted data:
        self.encrypted = kwargs.pop('encrypted', None)
        self.crypto_helper = CryptoHelper(self.active_config)
        self.secured_data = {}

        # prepare command
        self.command_parts = {
            'command': kwargs.pop('command', None),
            'commands': kwargs.pop('commands', []),
            'requirements_txt_path': kwargs.pop('requirements_txt', None),
            'ssh_identity_pub_b64': self.active_config.general.default_public_key,
            'ssh_identity_b64': self.active_config.general.default_public_key,
            'ml_data_b64': self.active_config.general.ml_data,
            'ml_file_name': self.active_config.general.ml_path
        }
        # updates
        self.job_env = kwargs.pop('env', None) or {}
        self.env = dict(self.job_env)
        self.env.update(self._get_env())
        if self.active_config.general.ml_prefix is not None:
            self.env['ML_CONFIG_PREFIX'] = self.active_config.general.ml_prefix

        self.git_repo = kwargs.pop('git_repo', None)
        self.git_tag = kwargs.pop('git_tag', 'master')
        self.data_volume = kwargs.pop('data_volume', None)
        self.data_query = kwargs.pop('data_query', None)
        self.data_use_iterator = kwargs.pop('data_use_iterator', False)
        self.data_dest_folder = kwargs.pop('data_dest_folder', '/data')
        self.log_cb = kwargs.pop('log_callback')
        self.labels = kwargs.pop('labels', {})
        self.volumes = kwargs.pop('volumes', {})
        self.gpu = kwargs.pop('gpu', True) and self.active_config.general.get('gpu', True)
        if self.data_volume is not None:
            self.env['ML_DATA_VOLUME'] = self.data_volume
            self.env['ML_DATA_QUERY'] = self.data_query
            self.env['ML_DATA_USE_ITERATOR'] = self.data_use_iterator
            self.env['ML_DATA_DEST'] = self.data_dest_folder

        self.persistent_paths = {}
        for container_path, host_path in kwargs.pop('persistent_paths', {}).items():
            bind_name, src_path = self._bind_volume(src_path=host_path, bind_path=container_path)
            self.persistent_paths[src_path] = bind_name

        self.output_paths = self.build_artifact_volumes(kwargs.pop('output_paths', []))
        self.output_data_volume = kwargs.pop('output_data_volume', None)

        if self.output_data_volume is not None:
            self.env['ML_OUTPUT_DATA_VOLUME'] = self.output_data_volume
        # result placeholders
        self.errors = []
        self.stages_results = {}

        kwargs['image'] = DockerWrapper.downgrade_gpu_image_if_needed(kwargs.pop('image'), self.gpu)
        self.init_kwargs = kwargs
        self.root_mount = None

        # params for containers
        self.init_kwargs['log_callback'] = self.log_cb
        self.init_kwargs['active_config'] = self.active_config

    def build_artifact_volume(self, volume, volume_labels=None):
        volume = volume if not volume.startswith('/') else volume[1:]
        volume_name = self._get_artifact_name(volume)
        volume_labels = volume_labels or {}
        volume_labels['path'] = volume
        volume_obj = self.get_or_create_volume(volume_name, volume_labels)
        return self._bind_volume(src_path=volume_obj.id, bind_path=volume)

    def build_artifact_volumes(self, volumes):
        return [self.build_artifact_volume(volume) for volume in volumes]

    def _bind_volume(self, src_path, bind_path):
        bind_path = bind_path if bind_path[0] == '/' else '/%s' % bind_path
        bind_name = bind_path[1:]
        logger.debug("Path %s will be handled by %s", bind_path, src_path)

        self.env[f"ML_MOUNT_{bind_name}"] = src_path
        self.labels[f"ML_MOUNT_{bind_name}"] = src_path

        self.volumes.update({src_path: {'bind': bind_path}})
        return bind_name, src_path

    def _get_artifact_name(self, path):
        import re
        attempt_id = uuid.uuid4().hex[:3]
        return f"{self.invocation_id[:5]}_{attempt_id}___{re.sub(r'[^a-zA-Z0-9_.-]', '_', path)}"

    def _get_env(self):
        return {'ML_INVOCATION_ID': self.invocation_id, 'ML_PROJECT_ID': self.project_id}

    def _get_ssh_identity(self):
        explicit_identity = self.secured_data.get('file', {}).get('@identity', None)
        if explicit_identity is not None:
            cipher = Asymmetric.create_from(explicit_identity)
            self.command_parts['ssh_identity_b64'] = cipher.bytes_to_b64str(cipher.export_private_key_bytes('PEM'))
            self.command_parts['ssh_identity_pub_b64'] = cipher.bytes_to_b64str(cipher.export_public_key_bytes())
            logger.info('Using: %s', cipher.export_public_key_bytes().decode('utf-8'))
            return explicit_identity

        cipher = CryptoHelper(self.active_config).default_cipher()
        self.command_parts['ssh_identity_b64'] = cipher.bytes_to_b64str(cipher.export_private_key_bytes('PEM'))
        self.command_parts['ssh_identity_pub_b64'] = cipher.bytes_to_b64str(cipher.export_public_key_bytes())

        return cipher.export_private_key_bytes('PEM').decode('utf-8')

    async def pull_code(self):
        if self.git_repo is None:
            await self.log_cb('No git data provided. Skipping creation /code folder', step_name='pull_code')
            return None

        await self.pull_image(self.active_config.general.git_image)

        code_mount = self.build_artifact_volume('/code')
        mounts = {
            code_mount[1]: {'bind': "/code"},
            self.root_mount[1]: {'bind': "/root"},
        }

        return await  self.run_with_callbacks_and_validate_result(
            name='Pulling Code',
            image=self.active_config.general.git_image,
            command=f"clone {self.git_repo} -b {self.git_tag or 'master'} -v --depth=1 /code --recurse-submodules -j8",
            volumes=mounts)

    async def _clean_up_output_paths(self):
        for name, volume in self.output_paths:
            volume_obj = self.docker_wrapper.volume(volume)
            if volume_obj is not None:
                await self.log_cb(f'Removing  volume {name}', step_name='clean_up_output_paths')
                volume_obj.remove()

    @classmethod
    def __metadata_from_env_parts_norm_name(cls, k):
        return k if not k.startswith('ML_') else k[2:].lower()

    @classmethod
    def __metadata_from_env_parts_is_included(cls, k, v):
        if not v:
            return False

        excluded_envs = [
            'ML', 'ML_PROJECT_TOKEN', 'ML_INVOCATION_ID', 'ML_JOB_ID', 'ML_PROJECT_ID'
        ]
        return k and k not in excluded_envs and k[0] != '_'

    def _metadata_from_env_parts_filter_and_norm(self):
        return (
            (self.__metadata_from_env_parts_norm_name(k), str(v))
            for k, v in self.job_env.items()
            if self.__metadata_from_env_parts_is_included(k, v)
        )

    def _metadata_from_env_parts(self):
        ret = []
        special_mappings = {
            '_data_volume': '--metadata-num'
        }
        for meta_key, meta_val in self._metadata_from_env_parts_filter_and_norm():
            ret.extend([special_mappings.get(meta_key, '--metadata-string'), meta_key, str(meta_val)])

        return ret

    async def export_output_paths(self):
        if len(self.output_paths) == 0:
            return 'No export paths present', 0
        if self.output_data_volume is None:
            logger.error("Can't export output_path %s - there is not output data volume configured for your organization", [x[0] for x in self.output_paths])
            return 'No export Data Volume configured for this org', 0

        export_root_path = f"/export/{self.project_id}/{self.invocation_id}"
        mounts = {}
        for name, volume in self.output_paths:
            mounts[volume] = {'bind': f'{export_root_path}/{name}'}
        await self.run_ml_command(
            mounts, 'data', 'set-metadata', '--data-path', '/export',
            '--metadata-num', 'project_id', self.project_id,
            '--metadata-string', 'invocation_id', self.invocation_id,
            '--metadata-string', 'job_id', self.invocation_id,
            *self._metadata_from_env_parts())
        sync_res = await self.run_ml_command(
            mounts, 'data', 'sync', self.output_data_volume,
            '--no-progressbar', '--data-path', '/export', '--isolated',
            '--commit', f'Project ID: {self.project_id} Invocation: {self.invocation_id}',
            update_ml=False)
        await self._clean_up_output_paths()
        return sync_res

    async def cleanup_volumes(self):
        if not self.volumes:
            return

        for name, _ in self.volumes.items():
            if name in self.persistent_paths:
                await self.log_cb(f'cleanup_volumes: skipping persistent volume `{name}`. ', step_name='cleanup_volumes')
                continue

            volume_obj = self.docker_wrapper.volume(name)
            if volume_obj is not None:
                await self.log_cb(f'Removing  volume {name}', step_name='cleanup_volumes')
                volume_obj.remove()
        return 'Done', 0

    async def setup_root(self):
        await self.log_cb('Building home folder', step_name='Setup Credentials')

        if self.root_mount is None:
            self.root_mount = self.build_artifact_volume('/root')

        self._get_ssh_identity()
        command = "sh -c 'echo {} | base64 -d | sh -'".format(build_root_command(**self.command_parts))
        mounts = {self.root_mount[1]: {'bind': "/root"}}
        await  self.pull_image(self.active_config.general.shell_image, force=False)
        return await  self.run_with_callbacks_and_validate_result(
            name='Setup Credentials',
            image=self.active_config.general.shell_image,
            command=command,
            volumes=mounts
        )

    async def run_container(self):
        await self.log_cb(f'Running submitted code', step_name='Run Code')
        mounts = dict(self.volumes)
        mounts[self.cache_volume_name] = {'bind': "/cache"}
        self.env['ML_CACHE_FOLDER'] = '/cache'
        command = "sh -c 'echo {} | base64 -d | sh -'".format(build_user_command(**self.command_parts))
        self.init_kwargs['command'] = command
        return await self.run_with_callbacks_and_validate_result(
            'Run Code',
            volumes=mounts,
            labels=self.labels,
            workdir='/code',
            env=self.env,
            gpu=self.gpu

        )

    async def await_stage_tasks(self, stage_name, *args):
        await self.log_cb(f'{stage_name}: Running', step_name=stage_name)
        res = []
        errors = []
        tasks = None

        try:
            tasks = [asyncio.ensure_future(x) for x in args]
            done_tasks, pending_tasks = await asyncio.wait(tasks)
            for result in done_tasks:
                if result.exception() is not None:
                    errors.append(str(result.exception()))
                else:
                    execution_result = result.result() or ('Skipped', 0)
                    exit_state = execution_result[0]
                    exit_code = execution_result[1]
                    if exit_code == 0:
                        res.append(exit_state)
                    else:
                        errors.append(exit_state)

        except asyncio.CancelledError:
            await  self.log_cb(f'Execution cancelled at {stage_name}', step_name=stage_name)
            if tasks:
                for task in tasks:
                    task.cancel()

            return f'Execution cancelled at {stage_name}', 137

        if errors:
            return_res = '\n'.join([f'{stage_name} failed:'] + errors), -100
        else:
            return_res = '\n'.join([f'{stage_name} completed:'] + res), 0

        await self.log_cb(f'{stage_name} completed: {return_res}', step_name=stage_name)
        return return_res

    async def prepare_env(self):
        pull_code_task = self.pull_code()
        pull_image_task = self.pull_image(self.init_kwargs['image'], force=False)
        ml_clone_data_task = self.clone_data()
        return await self.await_stage_tasks('Preparing Environment', pull_code_task, pull_image_task, ml_clone_data_task)

    async def decrypt_env_step(self):
        return await self.await_stage_tasks('Decrypting Environment', self.decrypt_data())

    async def finalize_env(self):
        await self.await_stage_tasks('Finalizing Environment', self.export_output_paths())

    async def clean_up_env(self):
        return await self.await_stage_tasks('Cleanup Environment', self.cleanup_volumes())

    async def _try_stage(self, stage_name, stage):
        try:
            stage_res = await stage()
            return stage_res
        except PrepareDockerEnvironmentException as ex:
            await  self.log_cb(f'{self.invocation_id} Failed to: {str(ex)}', step_name=stage_name)
            logger.error(f'Failed to: {str(ex)}')
            stage_res = 'Failed: \n' + '\n'.join([x[0] for x in self.errors]), -200

        self.stages_results[stage_name] = stage_res
        return stage_res

    async def do_run(self):

        decrypt_env_step = self._try_stage('Decrypting Environment', self.decrypt_env_step)
        prepare_env_task = self._try_stage('prepare_env', self.prepare_env)
        finalize_env_task = self._try_stage('finalize_env', self.finalize_env)
        clean_up_env = self._try_stage('clean_up_env', self.clean_up_env)
        execute_code_task = self._try_stage('execute_code', self.run_container)

        # cascading tasks:
        for task in [decrypt_env_step, prepare_env_task, execute_code_task]:
            result = await task
            if result[1] != 0:
                break

        await finalize_env_task
        await clean_up_env

        exit_code = 0 if result[1] == 0 else result[0]
        await self.log_cb(f'Invocation {self.invocation_id} completed with state: {result}.', step_name='Invocation')
        return exit_code
