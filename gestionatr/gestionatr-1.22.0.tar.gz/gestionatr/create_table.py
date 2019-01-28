table_num = 107


TLINE1 = "    ('{0}', "
TLINE2 = "u'{0}'),\n"

f = open("info", "r")
cont = f.read().strip().replace("\n\n", "\n").split("\n")
out = open("out.txt", 'w')
first_elem = True

out.write("TABLA_{0} = [\n".format(table_num))

for line in cont:
    if first_elem:
        out.write(TLINE1.format(line.strip()))
    else:
        out.write(TLINE2.format(line.strip()))
    first_elem = not first_elem

out.write("]\n")
