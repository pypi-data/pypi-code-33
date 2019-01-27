def pass_tag(message):
    return '[\033[32mPASS\033[0m]%s' % message


def fail_tag(message):
    return '[\033[31mFAIL\033[0m]%s' % message


def highlight(message):
    return '\033[32m[%s]\033[0m' % message
