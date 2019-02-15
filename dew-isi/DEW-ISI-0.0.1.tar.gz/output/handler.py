import sys
sys.path.append('../')
import globals

def removeEndDigit(name):
    return name.strip("0123456789")

class outputHandler():
    constraints = {}
    mergedConstraints = {}
    message = ""
    heading = """#NS Output
set ns [new Simulator]
source tb_compat.tcl
     
     """

    footer = """$ns rtproto Session
$ns run"""
        
    def __init__(self):
        pass

    def produceOutput(self):
        print("Called output handler!")
        self.produceNSOutput()
        try:
            globals.app.clearMessage("output")
            globals.app.setMessage("output", self.message)
            print(self.message)
        except Exception as e:
            print(e)
            pass
    
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

    
    def produceNSOutput(self):
        self.message = self.heading + '\n' 
        self.expandConstraints()
        self.mergeConstraints()
        
        default_os = "Ubuntu1404-64-STD"
        default_type = "pc3000"
        
        # Define our nodes. 
        print(self.mergedConstraints)
        for n in self.mergedConstraints:
            if 'count' in self.mergedConstraints[n] and int(self.mergedConstraints[n]['count']) > 1:
                name = "[format \"%s%%03d\" $i]"% (removeEndDigit(n))
                # Make a loop.
                self.message = self.message + "for {set i 1} {$i <= %d} {incr i} {"%int(self.mergedConstraints[n]['count'])+'\n'
                space = "  "
            else:
                space = ""
                name = str(n)
            self.message = self.message + space + "set %s [$ns node]\n" % name
            if 'os' in self.mergedConstraints[n]:
                self.message = self.message + space + "set tb-set-node-os %s %s\n" %(name, self.mergedConstraints[n]['os'])
            else:
                self.message = self.message + space + "set tb-set-node-os %s %s\n" %(name, default_os)
            if 'type' in self.mergedConstraints[n]:
                self.message = self.message + space + "set tb-set-hardware %s %s\n" %(name, self.mergedConstraints[n]['type'])
            else:	
                self.message = self.message + space + "set tb-set-hardware %s %s\n" %(name, default_type)
            
            # Close the loop if we need to.
            if 'count' in self.mergedConstraints[n] and int(self.mergedConstraints[n]['count']) > 1:
                self.message = self.message + "}\n"
                
        #else:
            # Defaults.
        #    self.message = self.message + "set %s [$ns node]\n" % str(n)
        #    self.message = self.message + "set tb-set-node-os %s %s\n" %(str(n), default_os)    
        #    self.message = self.message + "set tb-set-hardware %s %s\n" %(str(n), default_type)
                

        # Handle links        
        for a in globals.links:
            for b in globals.links[a]:
                self.message = self.message + "set link%s-%s [$ns duplex-link $%s $%s 1000Mb 0.0ms DropTail]" % (a, b, a, b)
                
            
        # Handle lan
        for l in globals.lans:
            self.message = self.message + "set %s [$ns make-lan " % l            
            for i in globals.lans[l]:
                self.message = self.message + "$" + i + " "
            self.message = self.message + "1Mb 0ms]\n"
        
        self.message = self.message + self.footer
