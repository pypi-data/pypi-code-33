import mold

def handle_context(ctx):
    if ctx.command == '--version':
        print('v' + mold.__version__)
        return ctx.OK
    return ctx.NEXT_COMMAND
