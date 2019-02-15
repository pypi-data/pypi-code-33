import json
import subprocess

import clickclick

from zalando_kubectl.models.ingress import Ingress, RAW_WEIGHTS_ANNOTATION


def get_raw_backends(kubernetes_obj):
    """Return the names of all services of an ingress."""

    result = []
    default_backend = kubernetes_obj['spec'].get('backend')
    if default_backend:
        result.append(default_backend['serviceName'])

    rules = kubernetes_obj['spec'].get('rules', [])
    for rule in rules:
        for path in rule.get('http', {}).get('paths', []):
            for backend in path.values():
                result.append(backend['serviceName'])
    return frozenset(result)


def get_stackset_backends(kubectl, stack, namespace):
    """Returns all the stack names for a given stackset"""

    cmdline = [kubectl, "get", "stacks", "-l", "stackset={}".format(stack), "-o", "json"]

    if namespace:
        cmdline += ("-n", namespace)
    try:
        data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode(
            "utf-8")
    except subprocess.CalledProcessError:
        return []
    result = json.loads(data)
    backends = [item['metadata']['name'] for item in result['items']]
    return backends


def stackset_managed(kubernetes_obj: dict) -> bool:
    if 'ownerReferences' in kubernetes_obj['metadata']:
        for ref in kubernetes_obj['metadata']['ownerReferences']:
            if ref['kind'] == 'StackSet':
                return True
    return False


def get_ingress(kubectl, namespace, ingress):
    """Fetch the backends weights from a Kubernetes Ingress using kubectl."""

    cmdline = [kubectl, "get", "ingress", ingress, "-o", "json"]

    if namespace:
        cmdline += ("-n", namespace)

    data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")
    kubernetes_obj = json.loads(data)
    s_managed = stackset_managed(kubernetes_obj)
    if s_managed:
        stackset_backends = get_stackset_backends(kubectl, ingress, namespace)
    else:
        stackset_backends = []
    raw_backends = get_raw_backends(kubernetes_obj)
    return Ingress(json.loads(data), raw_backends=raw_backends, stackset_backends=stackset_backends,
                   stackset_managed=s_managed)


def print_weights_table(ingress):
    """Print the backends and their weights in a user-friendly way."""
    if ingress.stackset_managed:
        columns = ["name", "desired", "actual"]
        rows = []
        for backend, weight in ingress.stackset_weights.items():
            r = {
                'name': backend,
                'actual': round(ingress.raw_weights.get(backend, 0.0), 1),
                'desired': round(weight, 1)
            }
            rows.append(r)
    else:
        columns = ['name', 'weight']
        rows = [{'name': backend, 'weight': round(weight, 1)} for backend, weight in ingress.raw_weights.items()]
    clickclick.print_table(columns, rows)


def set_ingress_weights(kubectl, namespace, ingress, force):
    """Update the backend weights on a Kubernetes Ingress using kubectl."""

    cmdline = [kubectl, "annotate", "ingress", ingress.name, "--overwrite"]

    if namespace:
        cmdline += ("-n", namespace)

    cmdline.append("{}={}".format(ingress.annotation, json.dumps(ingress.weights)))
    if ingress.stackset_managed and force:
        cmdline.append("{}={}".format(RAW_WEIGHTS_ANNOTATION, json.dumps(ingress.weights)))
    subprocess.run(cmdline, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
