import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from example.simplestate import SimpleState
from tantamount.machine import Machine
from tantamount.fsm2dot import GetDotNotation
import time


machine = Machine()

machine.addstate("A", SimpleState("AState A"), "abc")
machine.addstate("B", SimpleState("AState B"), "abc")
machine.addstate("C", SimpleState("AState C"), "abc")
machine.addstate("D", SimpleState("AState D"), "d")
machine.setstartstate("A")

machine.addtransition("A", 1, "B")
machine.addtransition("A", 2, "C")
machine.addtransition("A", 3, "D")

machine.addtransition("B", 1, "C")
machine.addtransition("B", 2, "A")
machine.addtransition("B", 3, "D")

machine.addtransition("C", 1, "A")
machine.addtransition("C", 2, "B")
machine.addtransition("C", 3, "D")

machine.addtransition("D", 1, "A")
machine.addtransition("D", 2, "B")
machine.addtransition("D", 3, "C")

machine.addtimeoutevent("A", 3, 0.5)
machine.addtimeoutevent("B", 3, 0.5)
machine.addtimeoutevent("C", 3, 0.5)
machine.addtimeoutevent("D", 1, 0.5)

with open("example.dot", "w") as f:
    gdn = GetDotNotation(machine)
    f.write(gdn.getdotnotation())

print(" - start machine")
machine.firststart()

print(" - loop back and forth")
for eventid in range(1, 3):
    print(" - eventid: {}".format(eventid))
    for loop in range(6):
        print(" -- counter: {}".format(loop+1))
        machine.operate(eventid)

print(" - first timeout")
time.sleep(0.6)
machine.operate(2)

print(" - second timeout")
time.sleep(0.6)
machine.operate(3)

print(" - third timeout")
time.sleep(0.6)
machine.operate(3)

print(" - timeout loop")
time.sleep(1.1)

print(" - done")

