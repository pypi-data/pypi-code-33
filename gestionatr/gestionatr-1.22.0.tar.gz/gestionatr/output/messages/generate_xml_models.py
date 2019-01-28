file = open("info")
out = open("out.txt", 'w')

init_i = "\nclass {0}(XmlModel):\n\n" \
         "    _sort_order = ({1})\n\n" \
         "    def __init__(self):\n" \
         "        self.{2} = XmlField('{0}')\n"

satr_line = "        self.{0} = XmlField('{1}')\n"
aatr_line = "        self.{0} = {1}()\n"
latr_line = "        self.{0} = []\n"
final_line = "        super({0}, self).__init__('{1}', '{2}')\n\n\n"


classname = file.readline()[1:-2]
aclassname = classname[0].lower()
for c in classname[1:]:
    if c == '+':
        pass
    elif c == '*':
        pass
    elif c.isupper():
        aclassname += "_{0}".format(c.lower())
    else:
        aclassname += c
atr_names_list = [aclassname]
names_list = [classname]

for line in file.readlines():
    line = line[1:-2]
    aname = line[0].lower()
    for c in line[1:]:
        if c == '+':
            pass
        elif c == '*':
            aname += '_list'
        elif c.isupper():
            aname += "_{0}".format(c.lower())
        else:
            aname += c
    atr_names_list.append(aname)
    names_list.append(line)

out.write(init_i.format(classname, str(atr_names_list)[1:-1], atr_names_list[0]))

for i in range(1, len(atr_names_list)):
    if names_list[i][-1] == '+':
        out.write(aatr_line.format(atr_names_list[i], names_list[i][0:-1]))
    elif names_list[i][-1] == '*':
        out.write(latr_line.format(atr_names_list[i]))
    else:
        out.write(satr_line.format(atr_names_list[i], names_list[i]))

out.write(final_line.format(classname, classname, atr_names_list[0]))
