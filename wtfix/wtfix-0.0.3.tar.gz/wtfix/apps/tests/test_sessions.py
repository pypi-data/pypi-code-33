import aiofiles
import asyncio

import pytest

from wtfix.conf import settings
from wtfix.core import utils


class TestClientSessionApp:
    @pytest.mark.skip("TODO")
    @pytest.mark.asyncio
    async def test_listen(self):
        begin_string = b"8=" + utils.encode(settings.BEGIN_STRING)
        checksum_start = settings.SOH + b"10="

        async with aiofiles.open("sample_mdr_msg.txt", mode="rb") as f:
            contents = await f.read()

            reader = asyncio.StreamReader()
            reader.feed_data(contents)
            data = await reader.readuntil(begin_string)  # Detect beginning of message.
            data += await reader.readuntil(
                checksum_start
            )  # Detect start of checksum field.
            data += await reader.readuntil(
                settings.SOH
            )  # Detect final message delimiter.

        assert data == contents
        #     contents = await f.read()
        # print(contents)
        # 'My file contents'
