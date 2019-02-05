
if __name__ == '__main__':

    from fdspy.fds_cls import ClientAgentFront
    from os import system

    system("title "+"FDS FRONT")

    CAB = ClientAgentFront(
        path_fds_queue=str(input("fds queue file path: "))
    )

    CAB.start()
