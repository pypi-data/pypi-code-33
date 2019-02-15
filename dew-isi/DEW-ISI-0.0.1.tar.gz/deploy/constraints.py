import json
import requests
import sys
sys.path.append('../')
import globals

import appJar

try:
    import xir
    from xir import eq, choice, gt, ge, select
    NOXIR=False
except ImportError:
    NOXIR=True

mainUrl = 'http://127.0.0.1:5000/'

def removeEndDigit(name):
    return name.strip("0123456789")


class deployHandler():

    def __init__(self):
        self.constraintButtons = []
        self.constraints = {}
        self.mergedConstraints = {}

    def expandConstraints(self):
        self.constraints = {}
        # XXX This is a lot of extra work to redo the globals constraint dictionary
        # to include only the types we deal with for constraints right now and
        # to expand cases where the main node name (e.g. 'fred') has a constraint of 'num'
        # and deal with cases when there are specific constraints of some of these (e.g. an 'os' for 'fred1')
        for n in globals.nodes:
            self.constraints[n] = {}
            for type in ['os', 'nodetype', 'num']:
                if n in globals.constraints and type in globals.constraints[n]:
                        self.constraints[n][type] = globals.constraints[n][type]
                elif removeEndDigit(n) in globals.constraints and type in globals.constraints[removeEndDigit(n)]:
                        self.constraints[n][type] = globals.constraints[removeEndDigit(n)][type]
    
    def mergeConstraints(self):
        # After we've expanded constraints, we can merge ones that are the same.
        self.mergedConstraints = {}
        covered = []
        for n in self.constraints:
            #if 'num' in self.constraints[n]:
            #    numWSame = int(self.constraints[n]['num'])
            #else:
            numWSame = 1
            if n in covered:
                continue
            for x in self.constraints:
                if x in covered:
                    continue
                # Don't compare our self to our self (no point), and don't compare two things with different base names.
                if n != x and removeEndDigit(n) == removeEndDigit(x):
                    # If we find the same name-start + all the same constraints are the same, we can merge these.
                    sameConstraints = True
                    for type in self.constraints[n]:
                        if type not in self.constraints[x] or self.constraints[x][type] != self.constraints[n][type]:
                            sameConstraints = False
                    if sameConstraints:
                        #if 'num' in  self.constraints[x]:
                        #    numWSame = numWSame + int(self.constraints[x]['num'])
                        #else:
                        #    numWSame = int(numWSame) + 1
                        numWSame = int(numWSame) + 1
                        covered.append(x)
            self.mergedConstraints[n] = {}
            self.mergedConstraints[n]['count'] = int(numWSame)
            for type in self.constraints[n]:
                if type != 'num':
                    self.mergedConstraints[n][type]  = self.constraints[n][type]
            covered.append(n)
            
                
    def process_constraints(self):
        
        checkBoxesToAdd = []
        
        for c in self.constraintButtons:
            try:
                globals.app.removeCheckBox(c)
            except:	
                pass
        self.constraintButtons = []
        self.expandConstraints()
        self.mergeConstraints()

        print("CONSTRAINTS")
        print(globals.constraints)
        print("Our merged ones:")
        print(self.mergedConstraints)
                
        for name in self.mergedConstraints:
            constraintStr = removeEndDigit(name)
            if int(self.mergedConstraints[name]['count']) > 1:
                constraintStr + '*'
            constraintStr + ': '
            for type in self.mergedConstraints[name]:
                constraintStr = constraintStr + " " + type + '(' + str(self.mergedConstraints[name][type]) + ')'
            checkBoxesToAdd.append(constraintStr)
            self.constraintButtons.append(constraintStr)

        return checkBoxesToAdd
    
    def satisfyConstraintCombo(self):
        pass
    
    @staticmethod
    def checkConstraints(button):
        globals.app.clearListBox("solution list", callFunction=False)
        json_constraints = deployHandler.specifyCheckedConstraintsInXIR()
        
        if json_constraints == None:
            if NOXIR:
                globals.app.addListItem("solution list","Need Xir support to process constraints.")
            else:
                globals.app.addListItem("solution list","Unable to process constraints.")
            return

        print(json.dumps(json_constraints, sort_keys=False))
    
        mainUrl = 'http://127.0.0.1:5000/'        
        s = requests.Session()
        try:
            r = s.post(mainUrl + 'site_solutions', json=json_constraints, timeout=1)
            possibleSolutions = False
            if 'results' in json.loads(r.json()):
                for result in json.loads(r.json())['results']:
                    if result['result'] == 'solution':
                        print("Solution from %s" % " ".join(result['site_combo']))
                        globals.app.addListItem("solution list"," ".join(result['site_combo']))
                        possibleSolutions = True
            if not possibleSolutions:
                globals.app.addListItem("solution list","NO SOLUTIONS")
        except requests.exceptions.ReadTimeout:
            globals.app.addListItem("solution list","Solution not calculated yet.")
            return
        except requests.exceptions.RequestException as e:
            globals.app.addListItem("solution list","Constraint server unreachable (assumed to be at %s)." % (mainUrl))
            return
        except Exception as e:
            print(e)
            return

    @staticmethod
    def specifyCheckedConstraintsInXIR():
        if NOXIR:
            return None
            
        top = xir.Xir()
        nodes = {}
    
        # Get a list of the checkboxed constraints we want to investigate.
        # XXX HACK: This will give us all checkboxes in the app. 
        # So far we are only using these for constraints.
        n = 0
        for constraint in globals.app.getAllCheckBoxes():
            if not globals.app.getCheckBox(constraint):
                continue
            print("%s to xir" % constraint)
            count = 0
            os = None
            nodetype = None
            # XXX right now we're assuming OS names and such won't have spaces!
            for item in constraint.split():
                # XXX again, hacky, we assume a '(' indicates a constraint.
                if '(' in item:
                    try:
                        (type, value) = item.split('(')
                        value = value.strip(')')
                        if type == 'os':
                            os = value    
                        elif type == 'nodetype':
                            nodetype = value
                        elif type == 'count':
                            count = int(value)
                    except Exception as e:
                        print("Problem parsing constraint: %s. %s" % (constraint,e))
                
            # For now, we're skipping trying to get multiples of any one type
            # because the constraint solver can get overwhelmed.
            #for i in range(0,count):
            for i in range(0, 1):
                props = {'name': str(n)}
                if nodetype != None:
                    props['platform'] = xir.select(value.strip())   
                if os != None:
                    props['image'] = xir.select(value.strip())
                node = top.structure.node(props)
                nodes[n] = node
                n = n+1
                
        return top.structure.xir_dict()
            
            
    def checkConstraintServer(self):
        return True
    
    
    def getSuggestions(self, type='os'):
        suggestions = []
        try:
            s = requests.Session()
            r = s.post(mainUrl + 'getResourceList', data={'type':type})
            data = json.loads(r.content)
            for item in data:
                if item not in suggestions:
                    suggestions.append(item)
        except Exception as e:
            print(e)
            pass
            
        print("SUGGESTIONS:")
        print(suggestions)
        
        return suggestions
        
            
            