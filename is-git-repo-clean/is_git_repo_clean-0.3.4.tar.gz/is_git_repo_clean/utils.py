from asyncio import gather


#
# I like to think the common use-case for 'gather' is to cancel all async
#   operations should any one of them fail.  This is not how 'gather' was
#   implemented though which is why I wrote this function
#
async def resolveAll(awaitables):
    gatherAll = None
    try:
        gatherAll = gather(*awaitables)
        result = await gatherAll
    finally:
        if gatherAll:
            gatherAll.cancel()

    return result


def iif(condition, whenTruthy, whenFalsey):
    if condition:
        return whenTruthy
    else:
        return whenFalsey
