
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentBack
    import os

    os.system("title "+"FDS BACK")

    CAB = ClientAgentBack(
        path_fds_queue=os.path.realpath(input("fds queue file path: ")),
        available_cpu_cores=int(input("Available cpu cores: "))
    )

    CAB.start(time_wait=2)
