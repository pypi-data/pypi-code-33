
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentFront, ClientAgentBack
    import os
    import threading
    from fdspy.bginfo import bginfo

    os. system("title "+"FDS FRONT")

    path_fds_queue = os.path.join('C:', os.sep, 'APP', 'fdspy', 'fds_queue.json')
    available_cpu_cores = int(input("Available CPU cores: "))

    thread_bginfo = threading.Thread(target=bginfo)
    thread_bginfo.start()

    thread_back = threading.Thread(target=ClientAgentBack, args=(path_fds_queue, available_cpu_cores,))
    thread_back.start()

    CAB = ClientAgentFront(path_fds_queue=path_fds_queue)
