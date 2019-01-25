import enum


class EventType(enum.Enum):
    """
    Enum of existing/available ts3 event types.
    """
    UNKNOWN = 0

    TEXTMESSAGE = 1
    TALKSTATUSCHANGE = 2
    MESSAGE = 3
    MESSAGELIST = 4
    COMPLAINLIST = 5
    BANLIST = 6
    CLIENTMOVED = 7
    CLIENTLEFTVIEW = 8
    CLIENTENTERVIEW = 9
    CLIENTPOKE = 10
    CLIENTCHATCLOSED = 11
    CLIENTCHATCOMPOSING = 12
    CLIENTUPDATED = 13
    CLIENTIDS = 15
    CONNECTIONINFO = 16
    CHANNELCREATED = 17
    CHANNELEDITED = 18
    CHANNELDELETED = 19
    CHANNELMOVED = 20
    SERVEREDITED = 21
    SERVERUPDATED = 22
    CURRENTSERVERCONNECTIONCHANGED = 23
    CONNECTSTATUSCHANGE = 24
    SERVERGROUPLIST = 25

    @classmethod
    def get_type(cls, ts3event):
        if ts3event.event == 'notifytextmessage':
            return EventType.TEXTMESSAGE
        elif ts3event.event == 'notifytalkstatuschange':
            return EventType.TALKSTATUSCHANGE
        elif ts3event.event == 'notifymessage':
            return EventType.MESSAGE
        elif ts3event.event == 'notifymessagelist':
            return EventType.MESSAGELIST
        elif ts3event.event == 'notifycomplainlist':
            return EventType.COMPLAINLIST
        elif ts3event.event == 'notifybanlist':
            return EventType.BANLIST
        elif ts3event.event == 'notifyclientmoved':
            return EventType.CLIENTMOVED
        elif ts3event.event == 'notifyclientleftview':
            return EventType.CLIENTLEFTVIEW
        elif ts3event.event == 'notifycliententerview':
            return EventType.CLIENTENTERVIEW
        elif ts3event.event == 'notifyclientpoke':
            return EventType.CLIENTPOKE
        elif ts3event.event == 'notifyclientchatclosed':
            return EventType.CLIENTCHATCLOSED
        elif ts3event.event == 'notifyclientchatcomposing':
            return EventType.CLIENTCHATCOMPOSING
        elif ts3event.event == 'notifyclientupdated':
            return EventType.CLIENTUPDATED
        elif ts3event.event == 'notifyconnectioninfo':
            return EventType.CONNECTIONINFO
        elif ts3event.event == 'notifychannelcreated':
            return EventType.CHANNELCREATED
        elif ts3event.event == 'notifychanneledited':
            return EventType.CHANNELEDITED
        elif ts3event.event == 'notifychanneldeleted':
            return EventType.CHANNELDELETED
        elif ts3event.event == 'notifychannelmoved':
            return EventType.CHANNELMOVED
        elif ts3event.event == 'notifyserveredited':
            return EventType.SERVEREDITED
        elif ts3event.event == 'notifyserverupdated':
            return EventType.SERVERUPDATED
        elif ts3event.event == 'notifycurrentserverconnectionchanged':
            return EventType.CURRENTSERVERCONNECTIONCHANGED
        elif ts3event.event == 'notifyconnectstatuschange':
            return EventType.CONNECTSTATUSCHANGE
        elif ts3event.event == 'notifyservergrouplist':
            return EventType.SERVERGROUPLIST
        else:
            return EventType.UNKNOWN

