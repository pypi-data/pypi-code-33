import spacy
from spacy.symbols import *
from spacy.lang.en.stop_words import STOP_WORDS

SUBJECTS = ["nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"]
OBJECTS = ["pobj", "dobj", "dative", "attr", "oprd"]

def getSubsFromConjunctions(subs):
    moreSubs = []
    for sub in subs:
        # rights is a generator
        rights = list(sub.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreSubs.extend([tok for tok in rights if tok.dep_ in SUBJECTS or tok.pos_ == "NOUN"])
            if len(moreSubs) > 0:
                moreSubs.extend(getSubsFromConjunctions(moreSubs))
    return moreSubs

def getObjsFromConjunctions(objs):
    moreObjs = []
    for obj in objs:
        # rights is a generator
        rights = list(obj.rights)
        rightDeps = {tok.lower_ for tok in rights}
        if "and" in rightDeps:
            moreObjs.extend([tok for tok in rights if tok.dep_ in OBJECTS or tok.pos_ == "NOUN"])
            if len(moreObjs) > 0:
                moreObjs.extend(getObjsFromConjunctions(moreObjs))
    return moreObjs

def getVerbsFromConjunctions(verbs):
    moreVerbs = []
    for verb in verbs:
        rightDeps = {tok.lower_ for tok in verb.rights}
        if "and" in rightDeps:
            moreVerbs.extend([tok for tok in verb.rights if tok.pos_ == "VERB"])
            if len(moreVerbs) > 0:
                moreVerbs.extend(getVerbsFromConjunctions(moreVerbs))
    return moreVerbs

def findSubs(tok):
    head = tok.head
    while head.pos_ != "VERB" and head.pos_ != "NOUN" and head.head != head:
        head = head.head
    if head.pos_ == "VERB":
        subs = [tok for tok in head.lefts if tok.dep_ == "SUB"]
        if len(subs) > 0:
            verbNegated = isNegated(head)
            subs.extend(getSubsFromConjunctions(subs))
            return subs, verbNegated
        elif head.head != head:
            return findSubs(head)
    elif head.pos_ == "NOUN":
        return [head], isNegated(tok)
    return [], False

def isNegated(tok):
    negations = {"no", "not", "n't", "never", "none"}
    for dep in list(tok.lefts) + list(tok.rights):
        if dep.lower_ in negations:
            return True
    return False

def findSVs(tokens):
    svs = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB"]
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        if len(subs) > 0:
            for sub in subs:
                svs.append((sub.orth_, "!" + v.orth_ if verbNegated else v.orth_))
    return svs

def getObjsFromPrepositions(deps):
    objs = []
    for dep in deps:
        if dep.pos_ == "ADP" and dep.dep_ == "prep":
            for tok in dep.rights:
                print(tok.dep_)
                print(OBJECTS)
            objs.extend([tok for tok in dep.rights if tok.dep_ in OBJECTS or (tok.pos_ == "PRON" and tok.lower_ == "me")])
    return objs

def getObjsFromAttrs(deps):
    for dep in deps:
        if dep.pos_ == "NOUN" and dep.dep_ == "attr":
            verbs = [tok for tok in dep.rights if tok.pos_ == "VERB"]
            if len(verbs) > 0:
                for v in verbs:
                    rights = list(v.rights)
                    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
                    objs.extend(getObjsFromPrepositions(rights))
                    if len(objs) > 0:
                        return v, objs
    return None, None

def getObjFromXComp(deps):
    for dep in deps:
        if dep.pos_ == "VERB" and dep.dep_ == "xcomp":
            v = dep
            rights = list(v.rights)
            objs = [tok for tok in rights if tok.dep_ in OBJECTS]
            objs.extend(getObjsFromPrepositions(rights))
            if len(objs) > 0:
                return v, objs
    return None, None

def getAllSubs(v):
    verbNegated = isNegated(v)
    subs = [tok for tok in v.lefts if tok.dep_ in SUBJECTS and tok.pos_ != "DET"]
    if len(subs) > 0:
        subs.extend(getSubsFromConjunctions(subs))
    else:
        foundSubs, verbNegated = findSubs(v)
        subs.extend(foundSubs)
    return subs, verbNegated

def getAllObjs(v):
    rights = list(v.rights)
    objs = [tok for tok in rights if tok.dep_ in OBJECTS]
    objs.extend(getObjsFromPrepositions(rights))

    #potentialNewVerb, potentialNewObjs = getObjsFromAttrs(rights)
    #if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
    #    objs.extend(potentialNewObjs)
    #    v = potentialNewVerb

    potentialNewVerb, potentialNewObjs = getObjFromXComp(rights)
    if potentialNewVerb is not None and potentialNewObjs is not None and len(potentialNewObjs) > 0:
        objs.extend(potentialNewObjs)
        v = potentialNewVerb
    if len(objs) > 0:
        objs.extend(getObjsFromConjunctions(objs))
    return v, objs

def findSVOs(tokens):
    svos = []
    verbs = [tok for tok in tokens if tok.pos_ == "VERB" and tok.dep_ != "aux"]
    print(verbs)
    for v in verbs:
        subs, verbNegated = getAllSubs(v)
        # hopefully there are subs, if not, don't examine this verb any longer
        if len(subs) > 0:
            v, objs = getAllObjs(v)
            for sub in subs:
                for obj in objs:
                    objNegated = isNegated(obj)
                    svos.append((sub.lower_, "!" + v.lower_ if verbNegated or objNegated else v.lower_, obj.lower_))
                if len(objs) == 0:
                    svos.append((sub.lower_, "!" + v.lower_ if verbNegated else v.lower_, "<<ITSELF>>"))

        else:
            print("NO SUBS FOR VERB")
    return svos

def findCondClauses(tokens):
    clauses = []
    for tok in tokens:
        #print()
        #print(tok.dep_)
        #print(''.join(t.text_with_ws for t in tok.subtree))
        if tok.dep_ in ('acomp', 'xcomp', 'ccomp', 'advcl', 'prep'):
            clause=(''.join(t.text_with_ws for t in tok.subtree))
            if any(word in clause.lower() for word in ['at', 'when', 'if', 'after', 'before', 'then', 'during']):
                condcl = (''.join(t.text_with_ws for t in tok.subtree))
                
                # Try and get the notion of dependency.
                # before
                if any(word in clause.lower() for word in ['then', 'before']):                
                    dep = "<<STARTS AFTER MAIN CLAUSE>>"
                # after
                elif any(word in clause.lower() for word in ['if', 'after']):
                    dep = "<<STARTS BEFORE MAIN CLAUSE>>"
                # during
                elif any(word in clause.lower() for word in ['at', 'when', 'during']):
                    dep = "<<SAMETIME>>"
                
                includesTime = False
                if any(word in clause.lower() for word in ['minute', 'minutes', 'second', 'seconds', 'wait']):
                    includesTime = True
                
                clauses.append((condcl, dep, includesTime))
            else:
                print("WARNING: Unhandled clause: %s" % clause)
    return clauses
        
def findEntities(toks, sub=True, obj=False):	
    entities = []
    spans = list(toks.ents) + list(toks.noun_chunks)
    for span in spans:
        is_nsubj = False
        is_obj = False
        for tok in span:
            if tok.dep in set([nsubj, nsubjpass]):
                is_nsubj = True
            if tok.dep in set([dobj, iobj, pobj]):
                is_obj = True
        if is_obj:
            try:
                print("OBJ span: %s" % str(span))
            except Exception as e:
                print(e)
        if is_nsubj:
            print("SUB span: %s" % str(span))
        if is_nsubj==sub and is_obj==obj:
            if str(span.merge()).lower() not in ['we', 'i', 'us', 'they', 'them', 'it', 'itself']:
            #ent_str = ' '.join(x for x in str(span).lower() if x not in STOP_WORDS)
            #if str(span.merge()).lower() not in STOP_WORDS:
                entities.append(span)
    return entities    
   
def actionRelation(sen):   
    #remove_list = ['will', 'has']
    remove_list = []
    sen = sen.split()
    sen = ' '.join([i for i in sen if i not in remove_list])
    tokens = nlp(sen) 
    return(findSVOs(tokens))
     
def printDeps(toks):
    for tok in toks:
        print(tok.orth_, tok.dep_, tok.pos_, tok.head.orth_, [t.orth_ for t in tok.lefts], [t.orth_ for t in tok.rights])

nlp = spacy.load('en')

def testing():
    while True:
        sen = input('Enter Sentence: ' )
        if 'quit' in sen.split():
            break
        
        tokens = nlp(sen)

        # Find and break out any conditional clauses (as best we can).
        print("Conditional Clauses:")
        cond_clauses = findCondClauses(tokens)
        main_sen = sen
        i=1
        for cond in cond_clauses:
            print("%d: %s (dep: %s)" % (i, str(cond[0]), str(cond[1])))
            main_sen = main_sen.replace(str(cond[0]), '', 1)
            i = i+1
        print("Main Sentence:")
        print(main_sen)
        
        main_action_relation = actionRelation(main_sen)
        clause_action_relation = []
        if len(cond_clauses) > 0:
            clause_action_relation = actionRelation(cond_clauses[0][0])
            clause_action_dep = str(cond_clauses[0][1])
            if len(clause_action_relation) == 0:
                clause_action_relation = cond_clauses[0][0]
        if len(cond_clauses) > 1:
            print("Warning: Mutiple conditional statements in a sentence is not handled.")
        print("Main action relation:")
        print(main_action_relation)
        if len(cond_clauses) > 0:
            print("Conditional action relation")
            print(clause_action_relation)
            print(clause_action_dep)
            #print("%s:%s" % (''.join(str(s) for s in clause_action_relation), clause_action_dep))
        
        # Identify all the entities.
        entities = findEntities(tokens)
        print("Entities to place in the topology:")
        for e in entities:
            print("\t%s" % e)

if __name__ == '__main__':
    testing()                
    

