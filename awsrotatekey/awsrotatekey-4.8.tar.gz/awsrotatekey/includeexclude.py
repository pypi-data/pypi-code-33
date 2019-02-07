class IE:

    dir1=raw_input("Enter the path for list of Blacklisting users: ")
    dir2=raw_input("Enter the path for list of Whitelisting users: ")

    def excludeuser(self, user):
        with open(IE.dir1, 'r') as file:
            for exuser in file.readlines():
                exuser = exuser.strip()
                if user == exuser:
                    return True
            return False


    def includeuser(self, user):
        with open(IE.dir2, 'r') as file:
            for inuser in file.readlines():
                inuser = inuser.strip()
                if user == inuser:
                    return True
            return False


obj4=IE()