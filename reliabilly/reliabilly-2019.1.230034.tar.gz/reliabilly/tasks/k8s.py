from invoke import task


DEV_NAMESPACE = 'dev'
UAT_NAMESPACE = 'uat'
PROD_NAMESPACE = 'prod'
ALL_NAMESPACES = '--all-namespaces'
KUBERNETES_DELETE_CMD = 'kubectl delete -f'
KUBERNETES_APPLY_CMD = 'kubectl apply -f'
KUBERNETES_GET_CMD = 'kubectl get all'
KUBERNETES_GET_ALL_CMD = f'{KUBERNETES_GET_CMD} {ALL_NAMESPACES}'
KUBERNETES_GET_PODS_CMD = 'kubectl get pods'
KUBERNETES_GET_PODS_ALL_CMD = f'{KUBERNETES_GET_PODS_CMD} {ALL_NAMESPACES}'
KUBERNETES_GET_SERVICES_CMD = 'kubectl get services'
KUBERNETES_GET_SERVICES_ALL_CMD = f'{KUBERNETES_GET_SERVICES_CMD} {ALL_NAMESPACES}'


@task
def delete(ctx, resource_path, namespace=DEV_NAMESPACE):
    """ Deletes prior kubernetes stack for service. """
    print(f'Deleting local k8s stack for {resource_path}...')
    ctx.run(f'{KUBERNETES_DELETE_CMD} "{resource_path}" -n "{namespace}"')


@task
def apply(ctx, resource_path, namespace=DEV_NAMESPACE):
    """ Applies changes to local k8s stack for service. """
    ctx.run(f'{KUBERNETES_APPLY_CMD} "{resource_path}" -n "{namespace}"')


@task
def use_context(ctx, context):
    """Uses the specified context."""
    ctx.run(f'kubectl config use-context "{context}"')


@task
def get(ctx, namespace=DEV_NAMESPACE):
    """ Get all resources from local kubernetes. """
    ctx.run(f'{KUBERNETES_GET_CMD} -n "{namespace}"')


@task
def get_all(ctx):
    """ Get all resources from local kubernetes for all namespaces. """
    ctx.run(KUBERNETES_GET_ALL_CMD)


@task
def pods(ctx, namespace=DEV_NAMESPACE):
    """ Get all pods from local kubernetes. """
    ctx.run(f'{KUBERNETES_GET_PODS_CMD} -n "{namespace}"')


@task
def pods_all(ctx):
    """ Get all pods from local kubernetes for all namespaces. """
    ctx.run(KUBERNETES_GET_PODS_ALL_CMD)


@task
def services(ctx, namespace=DEV_NAMESPACE):
    """ Get all services from local kubernetes. """
    ctx.run(f'{KUBERNETES_GET_SERVICES_CMD} -n "{namespace}"')


@task
def services_all(ctx):
    """ Get all services from local kubernetes for all namespaces. """
    ctx.run(KUBERNETES_GET_SERVICES_ALL_CMD)
