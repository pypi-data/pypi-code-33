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
atr_names_list = [classname]
names_list = [classname]

for line in file.readlines():
    aname = line[1:-2]
    atr_names_list.append(aname)
    names_list.append(line[1:-2])

out.write(init_i.format(classname, str(atr_names_list)[1:-1], atr_names_list[0]))

for i in range(1, len(atr_names_list)):
    out.write(satr_line.format(atr_names_list[i], names_list[i]))

out.write(final_line.format(classname, classname, atr_names_list[0]))
