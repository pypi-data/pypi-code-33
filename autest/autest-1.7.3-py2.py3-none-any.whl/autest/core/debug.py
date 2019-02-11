

import hosts.output


def get_user_frame(start_depth=0):

    def is_user_frame(info):
        frame, filename, lineno, function, code_context, index = info
        if filename.endswith(".test") or filename.endswith(".test.py") or filename.endswith(".ext"):
            return True
        return False

    return hosts.output.getCurrentStack(start_depth,is_user_frame)

