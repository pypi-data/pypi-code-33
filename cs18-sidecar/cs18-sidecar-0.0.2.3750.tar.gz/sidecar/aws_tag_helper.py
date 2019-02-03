from logging import Logger

from sidecar.const import Const


class AwsTagHelper:
    SpotFleetIdTag = "aws:ec2spot:fleet-request-id"
    AutoScalingGroupNameTag = "aws:autoscaling:groupName"

    @staticmethod
    def get_tags(resource, logger: Logger) -> {}:
        import time
        for counter in range(60):
            tags = resource.tags
            if not tags:
                resource.reload()
            if not tags:
                logger.warning("Could not get tags retrying - retry {retry} of 60".format(retry=counter))
                time.sleep(5)
                continue
            else:
                break

        if not tags:
            logger.exception("couldn't get tags from resource")

        return dict((tag['Key'], tag['Value']) for tag in tags)

    @staticmethod
    def safely_get_tag(resource, tag_name: str, logger: Logger, value_if_missing: str = None) -> str:
        return AwsTagHelper.get_tags(resource=resource, logger=logger).get(tag_name, value_if_missing)

    @staticmethod
    def create_tag(key, value):
        return {'Key': key, 'Value': value}

    @staticmethod
    def get_apps_status_map(instance, logger: Logger) -> {}:
        apps_status_tag_value = AwsTagHelper.safely_get_tag(instance, Const.APP_STATUS_TAG, logger)
        return AwsTagHelper.parse_apps_status_tag_value(apps_status_tag_value)

    @staticmethod
    def parse_apps_status_tag_value(apps_status_value: str) -> {}:
        app_to_status_map = dict()
        if apps_status_value:
            all_statuses = apps_status_value.split(Const.CSV_TAG_VALUE_SEPARATE)
            app_to_status_map = dict(state.split(Const.APP_STATE_KEY_VALUE_SEPARATOR) for state in all_statuses)
        return app_to_status_map

    @staticmethod
    def format_apps_status_tag_value(app_to_status_map: {}) -> str:
        return Const.CSV_TAG_VALUE_SEPARATE.join(
            ["{KEY}{SEP}{VALUE}".format(KEY=app_name, SEP=Const.APP_STATE_KEY_VALUE_SEPARATOR, VALUE=app_status)
             for app_name, app_status in app_to_status_map.items()])
