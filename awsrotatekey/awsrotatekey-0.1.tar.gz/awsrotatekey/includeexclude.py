class IE:

    def excludeuser(self, user):
        with open('excludeuser.txt', 'r') as file:
            for exuser in file.readlines():
                exuser = exuser.strip()
                if user == exuser:
                    return True
            return False


    def includeuser(self, user):
        with open('includeuser.txt', 'r') as file:
            for inuser in file.readlines():
                inuser = inuser.strip()
                if user == inuser:
                    return True
            return False


obj4=IE()