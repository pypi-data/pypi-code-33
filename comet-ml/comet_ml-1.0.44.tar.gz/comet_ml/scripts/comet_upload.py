#!/usr/bin/env python
import logging
import sys

from comet_ml.comet import get_api_key
from comet_ml.config import get_config
from comet_ml.offline import OfflineSender, unzip_offline_archive

LOGGER = logging.getLogger("comet_ml")


def upload(offline_archive_path):
    unzipped_directory = unzip_offline_archive(offline_archive_path)
    config = get_config()
    api_key = get_api_key(None, config)
    sender = OfflineSender(api_key, unzipped_directory)
    sender.send()
    sender.close()


def main():
    upload_count = 0
    fail_count = 0
    for filename in sys.argv[1:]:
        LOGGER.info("Attempting to upload '%s'...", filename)
        try:
            upload(filename)
        except KeyboardInterrupt:
            break
        except Exception:
            LOGGER.error(
                "    Upload failed", exc_info=True, extra={"show_traceback": True}
            )
            fail_count += 1
        else:
            LOGGER.info("    done!")
            upload_count += 1
    LOGGER.info("Number of uploaded experiments: %s", upload_count)
    if fail_count > 0:
        LOGGER.info("Number of failed experiment uploads: %s", fail_count)


if __name__ == "__main__":
    main()
