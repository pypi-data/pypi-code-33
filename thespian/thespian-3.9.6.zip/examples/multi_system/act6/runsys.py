from thespian.actors import ActorSystem, Actor, ValidateSource, ValidatedSource
import sys

class SimpleSourceAuthority(Actor):
    def receiveMessage(self, msg, sender):
        if msg is True:
            self.registerSourceAuthority()
        if isinstance(msg, ValidateSource):
            self.send(sender,
                      ValidatedSource(msg.sourceHash,
                                      msg.sourceData,
                                      # Thespian pre 3.2.0 has no sourceInfo
                                      getattr(msg, 'sourceInfo', None)))


if __name__ == "__main__":
    if "shutdown" in sys.argv:
        ActorSystem('multiprocTCPBase').shutdown()
        sys.exit(0)
    asys = ActorSystem('multiprocTCPBase')
    sa = asys.createActor(SimpleSourceAuthority)
    asys.tell(sa, True)
