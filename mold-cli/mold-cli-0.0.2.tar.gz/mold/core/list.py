def handle_context(ctx):
    if ctx.command != 'list':
        return ctx.NEXT_COMMAND
    for current in ['leaf', 'fold', 'exec', 'conf', 'plug']:
        content = ctx.get_command_dirlist(current) 
        if len(content) == 0:
            continue
        print(current)
        print('    '+ '\n    '.join(ctx.get_command_dirlist(current)) or 'Empty')
    return ctx.OK
