import singer
import tap_framework
import tap_platformpurple.client
import tap_platformpurple.streams

LOGGER = singer.get_logger()


class PlatformPurpleRunner(tap_framework.Runner):
    pass


@singer.utils.handle_top_exception(LOGGER)
def main():
    args = singer.utils.parse_args(
        required_config_keys=['api_key', 'start_date', 'environment'])

    client = tap_platformpurple.client.PlatformPurpleClient(args.config)

    runner = PlatformPurpleRunner(
        args, client, tap_platformpurple.streams.AVAILABLE_STREAMS)

    if args.discover:
        runner.do_discover()
    else:
        runner.do_sync()


if __name__ == '__main__':
    main()
