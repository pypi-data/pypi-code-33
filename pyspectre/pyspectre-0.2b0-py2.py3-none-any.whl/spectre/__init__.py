

def get_REPLWrapper_in_this_process(
        cmd_or_spawn,
        orig_prompt,
        prompt_change=None):

    from pexpect.replwrap import REPLWrapper

    try:
        a = REPLWrapper(
                cmd_or_spawn,
                orig_prompt,
                prompt_change)

        a.child.delayafterclose = 0.0
        a.child.delaybeforesend = 0.0
        a.child.delayafterread = 0.0
        a.child.delayafterterminate = 0.0

        return a

    except Exception as e:
        if 'a' in locals() and a is not None:
            print(a.child.before)
        raise e


def get_REPLWrapper_in_another_process(
        cmd_or_spawn,
        orig_prompt,
        prompt_change=None):

    from .replwrap_server import REPLWrapper_client

    return REPLWrapper_client(
        cmd_or_spawn,
        orig_prompt,
        prompt_change)


# try:
#     # self.spectre = REPLWrapper(
#     #     cmd_or_spawn=full_cmd,
#     #     orig_prompt=u'\n> ',
#     #     prompt_change=None,
#     # )
#     self.spectre = REPLWrapper_client(
#         cmd_or_spawn=full_cmd,
#         orig_prompt=u'\n> ',
#         prompt_change=None, )
#
# except BaseException as e:
#     if self.spectre is not None:
#         print(self.spectre.child.before)
#     self._cleanup()
#     raise e