cases = """
******** BASIC TEXT *****
** ansi = 09fac8dbfd27bd9b4d23a00eb648aa751789536d
** html = b0e305a47932b35656ee73dce111b273b529eb51
** htms = b0e305a47932b35656ee73dce111b273b529eb51 
Hello, world!


******** BASIC FORMATTING *****
** ansi = 4f7e480e94d30caa4eafc519c44f7a6ead26a07c
** html = 266c6ef1819c5a96e671e622b80682868ab2fc03
** htms = 266c6ef1819c5a96e671e622b80682868ab2fc03
one two <key>three</key> four <value>five</value> eight
one two <key>three</key> four <value>five</value> eight
one two <key>three</key> four <value>five</value> eight
the file <file>/alpha/beta/gamma.txt</file> is for this code
<warning>This is a warning</warning>
<error>This is an error</error>


******** TABLE *****
** ansi = 9b3d11bd85ece67d2b1fadcd2bdc4f1ec6ba6885
** html = 23577b63efd885a4882f962df4dca81b73615f5c
** htms = 23577b63efd885a4882f962df4dca81b73615f5c
<table>
<tr><td>one</td><td>two</td><td>three</td></tr>
<tr><td>four</td><td>five</td><td>six</td></tr>
<tr><td>seven</td><td>eight</td><td>nine</td></tr>
</table>


******** SECTIONS *****
** ansi = b90bd800bc4ef71c6b01ad252fa96f616d52f2bf
** html = 9e566f04556f13c5f7147ed8c77c1dc07efb2d90
** htms = 9e566f04556f13c5f7147ed8c77c1dc07efb2d90
section 0 text
section 0 text
<section name="section 1">
section 1 text
section 1 text
<section name="section 2">
section 2 text
section 2 text
<section name="section 3">
section 3 text
section 3 text
<section name="section 4">
section 4 text
section 4 text
<section name="section 5">
section 5 text
section 5 text
<section name="section 6">
section 6 text
section 6 text
</section>
section 5 text
section 5 text
</section>
section 4 text
section 4 text</section>section 3 text
section 3 text
</section>
section 2 text
section 2 text
</section>
section 1 text
section 1 text
</section>
section 0 text
section 0 text


******** HORIZONTAL RULE *****
** ansi = 86e093a4bf1dbc8ec99c5be89228c4c107355ced
** html = 2a57db4a8a4fb1497452cee90c9b2dc3862381d2
** htms = 2a57db4a8a4fb1497452cee90c9b2dc3862381d2
before rule
<hr></hr>
after rule


******** HORIZONTAL RULE *****
** ansi = 86e093a4bf1dbc8ec99c5be89228c4c107355ced
** html = 2a57db4a8a4fb1497452cee90c9b2dc3862381d2
** htms = 2a57db4a8a4fb1497452cee90c9b2dc3862381d2
before rule
<hr/>
after rule


******** PROGRESS BARS (BASIC) *****
** ansi = 494b20bb9503abdb15c8df5ee1f05adb1c2c0d66
** html = 2fdb4eb3855e675d63980be378f7fa957caf53c0
** htms = 2fdb4eb3855e675d63980be378f7fa957caf53c0
<action name="MASTER" max="3">
<progress value="0"></progress>
<action name="ACT1" max="100">
!REPEAT 0 100 <progress value="{}">progress text</progress>
</action>
<progress value="1"></progress>
<action name="ACT2" max="100">
!REPEAT 0 100 <progress value="{}">progress text</progress>
</action>
<progress value="2"></progress>
<action name="ACT3" max="100">
!REPEAT 0 100 <progress value="{}">progress text</progress>
</action>
</action>


******** PROGRESS BARS (WITH INTERRUPTIONS) *****
** ansi = 0a3f3b3146ceed07d90e13e3cfeaa5bf8d613250
** html = 03730090c81f84af037b2eacf12d91e40913d521
** htms = 03730090c81f84af037b2eacf12d91e40913d521
<action name="My action master" max="3">
This text at the start of the master.
This text at the start of the master.
<progress value="1"></progress>
<action name="My action 1" max="100">
This text at the start of the action.
This text at the start of the action.
!REPEAT 0 50 <progress value="{}"></progress>
* Hello, I'm interrupting things!
* REPEAT 51 100 <progress value="{}"></progress>
This text at the end of the action.
This text at the end of the action.
</action>
<progress value="2"></progress>
<action name="My action 2" max="100">
This text at the start of the action.
This text at the start of the action.
!REPEAT 0 50 <progress value="{}"></progress>
* Hello, I'm interrupting things!
#REPEAT 51 100 <progress value="{}"></progress>
This text at the end of the action.
This text at the end of the action.
</action>
<progress value="3"></progress>
<action name="My action 3" max="100">
This text at the start of the action.
This text at the start of the action.
!REPEAT 0 50 <progress value="{}"></progress>
* Hello, I'm interrupting things!
!REPEAT 51 100 <progress value="{}"></progress>
This text at the end of the action.
This text at the end of the action.
</action>
This text at the end of the master.
This text at the end of the master.
</action>


******** QUESTION *****
** ansi = f352554bbe0c928330ad22cdb46fd73e1d3640b9
** html = 0bbf188f14c874af25151f6c17cd19c3660f3803
<question>
This is the question text.
<option>Alpha</option>
<option>Beta</option>
<option>Gamma</option>
<option>Delta</option>
</question>
"""
