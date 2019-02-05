
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentBack
    from fdspy.func import input_path
    import os

    os.system("title "+"FDS BACK")

    CAB = ClientAgentBack(
        path_fds_queue=input_path("fds queue file path: "),
        available_cpu_cores=int(input_path("Available cpu cores: "))
    )

    CAB.start(time_wait=2)
