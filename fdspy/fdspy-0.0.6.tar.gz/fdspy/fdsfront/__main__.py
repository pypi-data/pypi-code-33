
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentFront
    from os import system
    from fdspy.func import input_path

    system("title "+"FDS FRONT")

    CAB = ClientAgentFront(
        path_fds_queue=input_path("fds queue file path: ")
    )

    CAB.start()
