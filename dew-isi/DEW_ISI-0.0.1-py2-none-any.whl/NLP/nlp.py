import spacy
import sys
sys.path.append('../')
import globals
from spacy.lang.en.stop_words import STOP_WORDS
from HighLevelBehaviorLanguage.hlb import *
from NLP.nlplib import findEntities, findCondClauses, actionRelation

class nlpHandler():
    sentences = []
    dict = spacy.load('en')
    splitchars = ['!', '.', '\n', '?']
    submittedTriggers = []
    submittedActors = []
    timeindex = 0

    def __init__(self):
        for s in self.splitText(globals.nlp_help_str):
            self.sentences.append(s)

    def splitText(self, text):
        # Split the text up based on whatever delimeters we picked above.
        t = text
        for d in self.splitchars:
            t = t.replace(d, '|')
        return(t.split('|'))

    def nlpChanged(self, widget):
        current_text = globals.app.getTextArea("NLP Input")
        split_text = self.splitText(current_text)
        if len(split_text) != len(self.sentences) and len(split_text) > 1:
            if len(split_text) > len(self.sentences):
                # We have a new sentence.
                for sentence in split_text:
                    if sentence.strip() not in  self.sentences and sentence.strip() != "":
                        print("New to process: %s" % sentence)
                        
                        tokens = self.dict(sentence)
                        
                        # Entities.
                        entities = findEntities(tokens, sub=True, obj=False)
                        actors = []
                        for ent in entities:
                            ent_phrase = str(ent).split()
                            print(ent_phrase)
                            ent_phrase = [x for x in ent_phrase if x.lower() not in STOP_WORDS]
                            ent_str = ' '.join(ent_phrase)
                            ent_str = ''.join(x for x in ent_str.title() if not x.isspace())
                            print(ent_str)
                            if ent_str not in actors:
                                actors.append(ent_str)
                        
                        # Generate Behavior Suggestions
                        suggested_hlb = self.generate_behavior(sentence, tokens, actors=actors)
                        if suggested_hlb != None:
                            removetable = str.maketrans('', '', "'@#%")
                            suggested_hlb = suggested_hlb.translate(removetable)
                            print(suggested_hlb)
                            globals.app.setTextArea("behavior", suggested_hlb, callFunction=behaviorentered)
                        
                        # We don't add actors ourselves. The code that extracts actors from behavior will 
                        # end up doing what we want there.    
                        #for ent_str in actors:
                        #    if ent_str not in self.submittedActors and ent_str not in globals.actors:
                        #        globals.app.setTextArea("actor",ent_str+'\n', callFunction=actorentered)
                        #        self.submittedActors.append(ent_str)

                        
            elif len(split_text) < len(self.sentences):
                print("Do not handle erasures yet.")
                # We have lost a sentence.
            self.sentences = [s.strip() for s in split_text]
    
    def generate_behavior(self, sentence, tokens, actors=[]):
        
        # Pull out any conditional clauses.
        cond_clauses = findCondClauses(tokens)    
        
        # Pull out each of these clauses to simplify the main sentence.
        main_sen = sentence
        for cond in cond_clauses:
            main_sen = main_sen.replace(str(cond[0]), '', 1)
        
        # Get the main action relation
        print("Main sentence part: %s" % main_sen)
        main_action_relation = actionRelation(main_sen)
    
        # Try and parse the main conditional clause (if we have one)
        # We only handle one clause. Others are ignored.
        clause_action_relation = ()
        clause_includes_time = False
        if len(cond_clauses) > 0:
            clause_action_relation = actionRelation(cond_clauses[0][0])
            clause_action_dep = str(cond_clauses[0][1]) 
            clause_inclues_time = cond_clauses[0][2]
            #print(clause_action_relation)
        if len(cond_clauses) > 1:
            for cond in cond_clauses:
                if cond_clauses[cond][2]:
                    clause_inclues_time = True
            print("WARNING: We do not handle multiple conditional clauses in a sentence.")
        
        # Get the main action.
        try:
            actor, action, object = main_action_relation[0]
        except(ValueError, IndexError):
            # We didn't have enough values to unpack, skip everything else and return.
            print("WARNING: Did not extract any behavior from:\n\t%s"%(sentence))
            print(main_action_relation)
            return None
        
        for objents in findEntities(self.dict(main_sen),sub=False, obj=True):
            try:
                print("OBJECT ENT: %s" % str(objents))
            except Exception as e:
                print(e)
        main_hlb, main_trigger = self.hlbify(actor, action, object, actors=findEntities(self.dict(main_sen)), objects=findEntities(self.dict(main_sen),sub=False, obj=True))
        #print("MAIN HLB: %s. TRIGGER: %s" % (main_hlb, main_trigger))
        
        try:
            #print("Have below for clause action relation:\n\t"),
            #print(clause_action_relation)
            cond_actor, cond_action, cond_object = clause_action_relation[0]
        except(ValueError, IndexError):
            stmt = "%s EMIT %s\n" % (main_hlb, main_trigger)
            return(stmt)
        
        cond_hlb, cond_trigger = self.hlbify(cond_actor, cond_action, cond_object, actors=findEntities(self.dict(cond_clauses[0][0])), objects=findEntities(self.dict(cond_clauses[0][0]),sub=False, obj=True))
        
        if clause_action_dep == "<<STARTS BEFORE MAIN CLAUSE>>":
            if clause_inclues_time:
                 main_hlb = "WHEN %s WAIT %d %s EMIT %s" % (cond_trigger,self.timeindex,main_hlb,main_trigger)
            else:
                main_hlb = "WHEN %s %s EMIT %s" % (cond_trigger,main_hlb,main_trigger)
            cond_hlb = "%s EMIT %s" %(cond_hlb, cond_trigger)
        elif clause_action_dep == "<<STARTS AFTER MAIN CLAUSE>>":
            main_hlb = "%s EMIT %s" %(main_hlb, main_trigger)
            if clause_inclues_time:
                cond_hlb = "WHEN %s WAIT %d %s EMIT %s" % (main_trigger, self.timeindex, cond_hlb, cond_trigger)
            else:
                cond_hlb = "WHEN %s %s EMIT %s" % (main_trigger, cond_hlb, cond_trigger)
        else:
            # We want to start these at the same time??
            cond_hlb = "WAIT X%d %s EMIT %s" % (self.timeindex, cond_hlb, cond_trigger)
            main_hlb = "WAIT X%d %s EMIT %s" % (self.timeindex, main_hlb, main_trigger)
            self.timeindex = self.timeindex + 1
        
        return_stmt = ""
        if cond_trigger not in self.submittedTriggers:
            # We already have submitted the conditional action statement.
            self.submittedTriggers.append(cond_trigger)
            return_stmt = cond_hlb+'\n'
        if main_trigger not in self.submittedTriggers:
            self.submittedTriggers.append(main_trigger)
            return_stmt = return_stmt + main_hlb+'\n'
        if return_stmt != "":
            return(return_stmt)
        else:
            return None

    def hlbify(self, actor, action, object, actors=[], objects=[]):
        action_type = self.expActionType(action)
        shortest_actor_match = -1
        shortest_object_match = -1
        for act in actors:
            a = ' '.join(x for x in str(act).split() if x.lower() not in STOP_WORDS)
            a = ''.join(x for x in a.title() if not x.isspace())
            # This isn't a good match - we need to figure out the modifiers from the text.
            if actor.lower() in a.lower():
                if shortest_actor_match < 0:
                    shortest_actor_match = len(a) 
                    actor = a
                elif shortest_actor_match <= len(a):
                    shortest_actor_match = len(a) 
                    actor = a
        for act in objects:
            a = ' '.join(x for x in str(act).split() if x.lower() not in STOP_WORDS)
            a = ''.join(x for x in a.title() if not x.isspace())
            if object.lower() in a.lower():
                if shortest_object_match < 0:
                    shortest_object_match = len(a)
                    object = a
                elif shortest_object_match <= len(a):
                    shortest_object_match = len(a)
                    object = a
        if object not in ["<<ITSELF>>"]:
            script = action_type + object.title()
        else:
            script = action_type + actor.title()
        return("%s %s" % (actor, script), "%sSig" %(script))

    def baseForm(self, word):
        tokens = self.dict(word)
        for t in tokens:
            return str(t.lemma_).lower().strip()

    def expActionType(self, word):
        base = self.baseForm(word)
        if base in ['start', 'begin', 'boot', 'commence', 'deploy', 'kick', 'trigger', 'launch', 'run']:
            return 'start'
        if base in ['end', 'stop', 'finish', 'quit', 'die', 'close', 'exit', 'halt', 'destroy']:
            return 'end'
        if base in ['if', 'be', 'will', 'can', 'have']:
            return 'check'
        return base
        