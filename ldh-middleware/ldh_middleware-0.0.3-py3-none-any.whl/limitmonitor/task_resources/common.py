import pathlib

import django.contrib.auth
import paramiko
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from woocommerce import API as WOO_API

from ..models import ExternalCredit, ExternalBundle, Limit

logger = get_task_logger(__name__)


def get_woo_connection():
    return WOO_API(
        url=settings.WOO_URL,
        consumer_key=settings.WOO_CONSUMER_KEY,
        consumer_secret=settings.WOO_CONSUMER_SECRET,
        wp_api=settings.WOO_WP_API,
        version=settings.WOO_VERSION,
        query_string_auth=settings.WOO_QUERY_STRING_AUTH,
    )


def get_username_from_woo_customer_id(customer_id, woo=None):
    if woo is None:
        woo = get_woo_connection()

    try:
        query = "customers/" + str(customer_id)
        result = woo.get(query).json()
        return result["username"] + "@" + settings.SITE_DOMAIN
    except Exception as e:
        logger.exception("Could not retrieve username for customer_id " + str(customer_id))
        return "invalid"

    return account


def get_openvpn_ssh_connection():
    # make ssh connection to OpenVPN server
    # (uses system host keys, warns if host is not recognised)
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.WarningPolicy())  # TODO: where is this logged?
    ssh.connect(
        hostname=settings.OVPN_HOSTNAME,
        port=settings.OVPN_PORT,
        username=settings.OVPN_USERNAME,
    )

    return ssh


def managed_exec(ssh, command, close=True):
    stdin, stdout, stderr = ssh.exec_command(command)

    if close:
        ssh.close()

    output = "".join(stdout.readlines()).strip()
    if output == "":
        output = "None."

    error = "".join(stderr.readlines()).strip()

    message = "Executed: %s Output: %s" % (command, output,)

    # on sucess, log output, otherwise raise exception
    if stdout.channel.recv_exit_status() == 0:
        logger.info(message)
    else:
        message += " Error: " + error
        raise Exception(message)


def is_existing_credit(credit):
    matching_credits = ExternalCredit.objects.filter(
        parser=credit.parser,
        external_key=credit.external_key,
    )

    is_existing = len(matching_credits) > 0

    return is_existing


def get_external_bundle(parser, external_key):
    return ExternalBundle.objects.get(
        parser=parser,
        external_key=external_key,
    )


def activate_single_limit(ssh, limit, credit_timedelta=None, renewal_date=None):

    is_credit = credit_timedelta is not None
    is_renewal = renewal_date is not None

    if is_credit == is_renewal:
        raise Exception("Invalid activation attempt. Need strictly one of credit or renewal data.")

    if is_credit and limit.is_active:
        limit.expiry_date += credit_timedelta
    elif is_credit and not limit.is_active:
        limit.expiry_date = timezone.now() + credit_timedelta
        limit.is_active = True
    elif is_renewal:
        limit.renewal_date = renewal_date
        limit.is_active = True
    else:
        raise Exception("Invalid activation attempt. Unknown condition.")

    # skip activation command if we are debugging
    if settings.DEBUG_SKIP_ACTIVATION_COMMAND:
        limit.save()
        return

    # otherwise, activate the limit before saving

    if limit.service == settings.LM_SERVICES.TUNNEL:
        user_identity = limit.user.get_identity()
        filepath = settings.OVPN_FILEPATH.replace("{USER_IDENTITY}", user_identity)
        is_file = pathlib.Path(filepath).is_file()

        # only create certificate if it doesn't exist
        if not is_file:
            command = "./create_new_ovpn_config --generate %s" % (user_identity,)
            managed_exec(ssh, command, close=False)
    else:
        # skip unsupported limits
        limit.is_active = False

    limit.save()


def deactivate_single_limit(ssh, limit):
    if limit.service == settings.LM_SERVICES.TUNNEL:
        command = "./create_new_ovpn_config --revoke %s" % (limit.user.get_identity(),)
        managed_exec(ssh, command, close=False)

    limit.is_active = False
    limit.save()


def get_limit_objects(credit):

    # get and validate local username

    suffix = "@" + settings.SITE_DOMAIN
    if credit.account_name is None or not str.endswith(credit.account_name, suffix):
        raise Exception("Invalid account name: " + str(credit.account_name))
    else:
        suffix_len = 0 - len(suffix)
        username = credit.account_name[:suffix_len]

    # get objects (implicit validation that they exist)

    external_bundle = get_external_bundle(credit.parser, credit.bundle_key)

    limit = Limit.objects.get(
        user__username=username,
        service=external_bundle.service,
    )

    user = django.contrib.auth.get_user_model().objects.get(
        username=username,
    )

    return user, limit, external_bundle

@transaction.atomic
def store_credit_and_update_limit(ssh, credit, next_renewal=None):
    try:
        if credit.parser == "WOO1":
            from .tunnel_credit import update_limit_woo1
            update_limit_woo1(ssh, credit)
        elif credit.parser == 2:  # FIXME: this is WOO_SUBSCRIPTION_V1 from purist.limitmonitor
            from .tunnel_subscription import update_limit_woosub1
            update_limit_woosub1(ssh, credit, next_renewal)
        else:
            raise Exception("Unrecognised Parser " + str(credit.parser))

        credit.is_converted = True
        credit.error_message = ""
    except Exception as e:
        message = "Skipped adding credit Parser " + str(credit.parser) + ": " + credit.external_key + ". "
        logger.exception(message)
        credit.error_message = message + repr(e)
    finally:
        credit.save()
        state = "converted" if credit.is_converted else "skipped"
        logger.info("Stored " + state + " credit Parser " + str(credit.parser) + ": " + credit.external_key)


def deactivate_all_expired_limits():
    # make connection objects
    ssh = get_openvpn_ssh_connection()

    # get overdue objects and deactivate them
    now = timezone.now()
    overdue_list = Limit.objects.filter(expiry_date__lte=now, is_active=True)

    for limit in overdue_list:
        deactivate_single_limit(ssh, limit)

    ssh.close()


def debug_connection_task():
    # make connection objects
    woo_connection = get_woo_connection()
    ssh = get_openvpn_ssh_connection()
    managed_exec(ssh, "whoami", close=True)

    logger.info("Debug task with " + repr(woo_connection) + " and " + repr(ssh) + " completed successfully.")
