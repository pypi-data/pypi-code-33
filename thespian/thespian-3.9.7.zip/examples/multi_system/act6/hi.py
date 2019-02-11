from thespian.actors import *

class Hello(Actor):
    def receiveMessage(self, message, sender):
        self.send(sender, 'Hello, WORLD!')

def zipMyself():
    zipname = 'hi.zip'
    import zipfile
    zf = zipfile.ZipFile(zipname, 'w')
    zf.writestr('hi.py', open('hi.py', 'r').read())
    zf.close()
    return zipname

def say_hello():
    actorSys = ActorSystem("multiprocTCPBase")
    loadHash = actorSys.loadActorSource(zipMyself())  #(ref:loadSource)
    hello = actorSys.createActor('hi.Hello',
                                 sourceHash = loadHash)  #(ref:hashCreate)
    print(actorSys.ask(hello, 'are you there?', 1.5))
    actorSys.tell(hello, ActorExitRequest)

if __name__ == "__main__":
    say_hello()
