from pyparsing import ParseException, NotAny, Empty, Group, Word, CaselessKeyword, Literal, alphas, alphanums, nums, White, ZeroOrMore, OneOrMore, Optional, LineEnd
from enum import Enum
import sys
sys.path.append('../')
import globals

class HLBHintType(Enum):
    OPT_EMIT_STMT  = 0 # Statement
    REQ_EMIT_LIST  = 1 # The statement has an 'emit' keyword, but not list of emitted events.
    REQ_ACTION	   = 2 # The statement has actors, possibly a wait and/or when, but no action.
    REQ_ACTORS	   = 3 # The statement may have a wait and/or when statement, but no actors.
    REQ_WAIT_TIME  = 4 # The statement has a 'wait' keyword, but no variable for the wait.
    REQ_WHEN_LIST  = 5 # The statement has a 'when' keyword, but not a list of events.   
    NO_HINT	   = 6 # The statement is fully complete and has an emit list.
    BLANK	   = 7 # There's no text in the statement yet.
    REQ_ACTORS_HAVEWHEN = 8 # We need actors, but we have a 'when xxx' statement (and no wait), so we can suggest a 'wait' as well.
    REQ_ACTORS_HAVEWAIT = 9 # We need actors, but we have a 'wait xxx' or 'when xxx wait xxx'
    UNKNOWN_ERROR  = 10 # Catch all


class ConstraintParser():
    wsp = White().suppress()
    comma = Literal(",").suppress()
    num_keyword  = CaselessKeyword("num")
    os_keyword   = CaselessKeyword("os")
    link_keyword = CaselessKeyword("link")
    lan_keyword  = CaselessKeyword("lan")
    interfaces_keyword = CaselessKeyword("interfaces")
    location_keyword = CaselessKeyword("location")
    nodetype_keyword = CaselessKeyword("nodetype")
    not_akeyword = (NotAny(num_keyword) + NotAny(os_keyword) + NotAny(link_keyword) + NotAny(lan_keyword) + NotAny(interfaces_keyword) + NotAny(location_keyword) + NotAny(nodetype_keyword))
    
    actor = (not_akeyword + Word(alphanums))
    actors = actor + ZeroOrMore(wsp + actor)
    actor_pair = actor + wsp + actor
    strValue = (not_akeyword + Word(alphanums))
    numValue = (not_akeyword + Word(nums))
    
    single_entity_num_constraint = num_keyword
    single_entity_constraint = os_keyword | interfaces_keyword | location_keyword | nodetype_keyword
    
    single_entity_num_stmt = (single_entity_num_constraint("constraint") + wsp + actor("target") + wsp + numValue("value"))
    single_entity_str_stmt = (single_entity_constraint("constraint") + wsp + actor("target") + wsp + strValue("value"))
    link_stmt = (link_keyword("constraint") + wsp + actor_pair("target"))
    lan_stmt = (lan_keyword("constraint") + wsp + actors("target"))
    
    constraint_statement = (single_entity_num_stmt | single_entity_str_stmt | link_stmt | lan_stmt) + LineEnd()
    
    def parse_stmt(self, statement):
        """Parses an HLB statement and returns a tuple: (triggers, actors, action, e_events)
        Values are returned as "None" if they cannot be extracted.
        """
        try:
            parsed = self.constraint_statement.parseString(statement)
        except ParseException as pe:
            #print("WARNING: Could not parse HLB statement:\n\t%s" % (statement))
            return(None, None, None)
        if parsed.e_events == None:
            parsed.e_events = []
        return_tuple = (str(parsed.constraint), list(parsed.target), list(parsed.value))
        return(tuple(r if r != [] and r != "" else None for r in return_tuple))

class HLBParser():
    when_keyword = CaselessKeyword("when").suppress()
    wait_keyword = CaselessKeyword("wait").suppress() 
    emit_keyword = CaselessKeyword("emit").suppress()
    not_akeyword = (NotAny(emit_keyword) + NotAny(wait_keyword) + NotAny(when_keyword))
    comma = Literal(",").suppress()
    newline = Literal("\n")
    wsp = White().suppress()
    actor = (not_akeyword + Word(alphanums))
    actors = actor + ZeroOrMore((comma + wsp + actor | comma + actor))
    #action = (Optional(CaselessKeyword("start") | CaselessKeyword("stop") | CaselessKeyword("restart") | CaselessKeyword("check")) + (not_akeyword + Word(alphanums)))	
    action = (not_akeyword + Word(alphanums))
    event = (not_akeyword + Word(alphanums))
    events = event + ZeroOrMore((comma + wsp + event | comma + event))
    when_trigger = when_keyword + events("t_events")
    wait_time = (not_akeyword + Word(alphanums))
    wait_trigger = (wait_keyword + wait_time("wait_time"))
    trigger = (when_trigger + wsp + wait_trigger | when_trigger | wait_trigger)
    
    # Full complete statment.
    hlb_statement = (trigger + wsp + actors("actors") + wsp + action("action") + emit_keyword + events("e_events") 
                    |trigger + wsp + actors("actors") + wsp + action("action") 
                    | actors("actors") + wsp + action("action") + emit_keyword + events("e_events")
                    | actors("actors") + wsp + action("action")) + LineEnd()
    
    parts_of_when = (CaselessKeyword("w").suppress() | CaselessKeyword("wh").suppress() | CaselessKeyword("whe").suppress()) + LineEnd()
    parts_of_wait = (CaselessKeyword("w").suppress() | CaselessKeyword("wa").suppress() | CaselessKeyword("wai").suppress()) + LineEnd()
    
    # Partial statements (not incorrect, but not complete either.)
    hlb_partial_trigger_word = (when_trigger + wsp + parts_of_wait) | parts_of_when | parts_of_wait
    hlb_missing_when_list = (when_keyword) + LineEnd()
    hlb_missing_wait_time = (when_trigger + wsp + wait_keyword + LineEnd() | wait_keyword + LineEnd())
    hlb_missing_actors = (trigger("trigger") | trigger("trigger") + actors("actors") + comma + LineEnd())
    hlb_missing_actors_whenstmt = when_trigger + LineEnd()
    hlb_missing_actors_waitstmt = wait_trigger + LineEnd() | when_trigger + wsp + wait_trigger + LineEnd()
    hlb_missing_action = (trigger("trigger") + wsp + actors("actors") + LineEnd() |  actors("actors") + LineEnd())
    hlb_missing_emit_list = (trigger("trigger") + wsp + actors("actors") | actors("actors")) + wsp + action("action") + emit_keyword + LineEnd()
    
    #hlb = hlb_statement + newline + hlb
    def new_return_dict(self, t_events=None, actors=None, action=None, e_events=None, wait_time=None):
        # Initializes all the vars we may have to report.
        # parsed.t_events, parsed.actors, parsed.action, parsed.e_events, parsed.wait_time
        v = {}
        # Should be None or list
        v['t_events'] = self.if_not_none_return_list(t_events)
        # Should be None or list
        v['actors'] = self.if_not_none_return_list(actors)
        # Should be None or str
        try:	
            v['action'] = ''.join(action)
        except TypeError:
            v['action'] = str(action)
        # Should be None or list
        v['e_events'] =  self.if_not_none_return_list(e_events)
        # Should be None or str
        try:
            v['wait_time'] = ''.join(wait_time)
        except TypeError:
            v['wait_time'] = str(wait_time)
        return v
    
    def if_not_none_return_list(self, item):
        if item != None:
            return list(item)
        else:
            return None
    
    def parse_stmt(self, statement):
        """Parses an HLB statement and returns a tuple: (triggers, actors, action, e_events)
        Values are returned as "None" if they cannot be extracted.
        """
        try:
            parsed = self.hlb_statement.parseString(statement)
        except ParseException as pe:
            #print("WARNING: Could not parse HLB statement:\n\t%s" % (statement))
            return(None, None, None, None, None)
        if parsed.e_events == None:
            parsed.e_events = []
        return_tuple = (list(parsed.t_events), list(parsed.actors), list(parsed.action), list(parsed.e_events), str(parsed.wait_time))
        return(tuple(r if r != [] and r != "" else None for r in return_tuple))

    def transitionBstate2(self, ll):
        type, vals, hints = self.extract_partial(ll)
        translate = {}
        translate[HLBHintType.OPT_EMIT_STMT]  = "no hint"
        translate[HLBHintType.REQ_EMIT_LIST]  = "emit"
        translate[HLBHintType.REQ_ACTION]     = "action"
        translate[HLBHintType.REQ_ACTORS]     = "nactor"
        translate[HLBHintType.REQ_WAIT_TIME]  = "waitd"
        translate[HLBHintType.REQ_WHEN_LIST]  = "whene" 
        translate[HLBHintType.REQ_ACTORS_HAVEWHEN] = "when"
        translate[HLBHintType.REQ_ACTORS_HAVEWAIT] = "wait"
        translate[HLBHintType.NO_HINT]        = "no hint"
        translate[HLBHintType.BLANK]          = "start"
        translate[HLBHintType.UNKNOWN_ERROR]  = "no hint"
        
        #print("Stmt: \"%s\"\n\ttransitionBstate2: %s\tReturn: %s" % (ll, type.name, translate[type]))
        rval = translate[type]
        if (type == HLBHintType.REQ_ACTORS or type == HLBHintType.REQ_ACTION) and vals['actors'] != None and all(a.strip() in globals.actors for a in vals['actors']):
            if type == HLBHintType.REQ_ACTORS: 
                return "actor"
            else:
                return "action"
        else:
            return rval

    def extract_partial(self, partial):
        #print("Parsing \'%s\'" % partial)
        if len(partial.strip().split()) == 0:
            return(HLBHintType.BLANK,  self.new_return_dict(), ['WHEN', 'WAIT', '<ACTOR>'])
        t_events, actors, action, e_events, wait_time = self.parse_stmt(partial)
        # In case we have a 2 word action with a <keyword string> pattern:
        try:
            action = ''.join(action)
        except TypeError:
            action = str(action)
        if actors != None and e_events != None:
            #print("Complete statement with emit.")
            return(HLBHintType.NO_HINT, self.new_return_dict(t_events=t_events, actors=actors, action=action, e_events=e_events, wait_time=wait_time), []) 
        elif actors != None and e_events == None:
            #print("Complete statement, with no emit.")
            hint_list = ['EMIT ' + action +'Signal', 'EMIT'] 
            return(HLBHintType.OPT_EMIT_STMT, self.new_return_dict(t_events=t_events, actors=actors, action=action, wait_time=wait_time), hint_list) 
        
        
        # Our statement isn't complete or correct:
        if actors == None:
            #print("Statement is not complete as is.")
            
            ## WARNING: The following is a longest match first:
            ## For the below to work, the order must be kept 
            ## (along with the break out of conditional statements 
            ## via return or some other mechanism).
            
            # Do we have an emit, but missing emit event list?
            try:
                parsed = self.hlb_missing_emit_list.parseString(partial)
                #print("Missing emit list.")
                hint_list = [action+'Signal', '<LIST, OF, TRIGGERS>']
                return(HLBHintType.REQ_EMIT_LIST, self.new_return_dict(t_events=parsed.t_events, actors=parsed.actors, action=parsed.action, wait_time=parsed.wait_time), hint_list)
            except ParseException as pe:
                pass
            # Do we have a wait? but missing the wait time?
            try:
                parsed = self.hlb_missing_wait_time.parseString(partial)
                #print("Missing wait time")
                hint_list = ['<VARNAME_FOR_WAIT_TIME>']
                return(HLBHintType.REQ_WAIT_TIME, self.new_return_dict(t_events=parsed.t_events), hint_list)
            except ParseException as pe:
                pass
            # Do we have a when? but missing the when event triggers?
            try:
                parsed = self.hlb_missing_when_list.parseString(partial)
                #print("Missing when list.")
                hint_list = ['<TRIGGER_NAME>']
                return(HLBHintType.REQ_WHEN_LIST, self.new_return_dict(), hint_list)
            except ParseException as pe:
                pass
            # Do we just have a start of a keyword?
            if " " not in partial:
                hint_list = []
                return(HLBHintType.BLANK, self.new_return_dict(), hint_list)
            try:
                parsed = self.hlb_partial_trigger_word.parseString(partial)
                hint_list = []
                return(HLBHintType.BLANK, self.new_return_dict(), hint_list)
            except ParseException as pe:
                pass
            # Are we missing an action?
            try:
                # Maybe we don't have an actor, but a partial wait or when
            
                parsed = self.hlb_missing_action.parseString(partial)
                #print("Missing action.")
                hint_list = ['<METHOD_NAME>']
                for a in globals.actors:
                    if a != "":
                        hint_list.append(', ' + a.strip())
                return(HLBHintType.REQ_ACTION, self.new_return_dict(t_events=parsed.t_events, actors=parsed.actors, wait_time=parsed.wait_time), hint_list)
            except ParseException as pe:
                pass
            # Do we have a trigger, but no actors?
            try:
                parsed = self.hlb_missing_actors.parseString(partial)
                #print("Missing actors")
                hint_list = []
                for a in globals.actors:
                    if a != "":
                        hint_list.append(a.strip())
                try:
                    # We may have a 'when xxx' statement, in which case we should also suggest a 'wait' as a hint.
                    parsed_for_when = self.hlb_missing_actors_whenstmt.parseString(partial)
                    hint_list.append('WAIT')
                    return(HLBHintType.REQ_ACTORS_HAVEWHEN, self.new_return_dict(t_events=parsed.t_events), hint_list)
                except ParseException as pe:
                    # We don't just have a 'when xxxx'. We either have a 'wait xxx' or a 'when xxx wait xxx'
                    try:
                        parsed_for_wait = self.hlb_missing_actors_waitstmt.parseString(partial)
                        return(HLBHintType.REQ_ACTORS_HAVEWAIT, self.new_return_dict(t_events=parsed.t_events, wait_time=parsed.wait_time), hint_list)
                    except ParseException as pe:
                        return(HLBHintType.REQ_ACTORS,  self.new_return_dict(t_events=parsed.t_events, wait_time=parsed.wait_time), hint_list)
            except ParseException as pe:
                return(HLBHintType.UNKNOWN_ERROR, self.new_return_dict(), [])
            
                
def testParser():
    parser = HLBParser()
    while True:
        line = raw_input("Input statement: ")
        print(line)
        (t_events, actors, action, e_events, wait_time) = parser.parse_stmt(line)
        if actors != None:
            print("Actors: %s" %  actors)        
        if t_events != None:
            print("Trigger(s): %s" % t_events)
        if action != None:
            print("Action: %s" %  action)        
        if e_events != None:
            print("Emit events: %s" % e_events)
        if wait_time != None:
            print("Wait time: %s" % wait_time)
        parser.extract_partial(line)
    
if __name__ == "__main__":
    testParser()
    
    
