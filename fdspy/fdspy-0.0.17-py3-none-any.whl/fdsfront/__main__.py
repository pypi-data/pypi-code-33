
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentFront
    import os
    from fdspy.bginfo import bginfo
    import threading

    os. system("title "+"FDS FRONT")

    CAB = ClientAgentFront(
        path_fds_queue=os.path.join('C:', os.sep, 'APP', 'fdspy', 'fds_queue.json')
    )

    CAB.start()
