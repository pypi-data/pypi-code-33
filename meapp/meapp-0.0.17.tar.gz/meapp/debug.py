from django.conf import settings


def log(self, *args, sep=' ', end='\n', file=None): # known special case of print
    print(*args,sep=sep,end=end,file=file)
