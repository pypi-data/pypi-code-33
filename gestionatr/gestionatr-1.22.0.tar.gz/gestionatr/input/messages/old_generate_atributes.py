file = open("info")
out = open("out.txt", 'w')

method = "@property\n" \
         "def {0}(self):\n" \
         "    tree = {2}\n" \
         "    data = get_rec_attr(self.{1}, tree, False)\n" \
         "    if data is not None and data is not False:\n" \
         "        return data.text\n" \
         "    else:\n" \
         "        return False\n\n"

method_class = "@property\n" \
         "def {0}(self):\n" \
         "    tree = {2}\n" \
         "    data = get_rec_attr(self.{1}, tree, False)\n" \
         "    if data is not None and data is not False:\n" \
         "        return {3}(data)\n" \
         "    else:\n" \
         "        return False\n\n"

method_list = "@property\n" \
               "def {0}(self):\n" \
               "    data = []\n" \
               "    obj = get_rec_attr(self.obj, '{2}', False)\n" \
               "    if obj is not None and obj is not False:\n" \
               "        for d in obj.{0}:\n" \
               "            data.append({1}(d))\n" \
               "    return data\n\n"

method_list2 = "@property\n" \
              "def {0}(self):\n" \
              "    data = []\n" \
              "    obj = get_rec_attr(self.obj, '{3}', False)\n" \
              "    if (hasattr(obj, '{3}') and\n" \
              "            hasattr(obj.{3}, '{1}')):\n" \
              "        for d in obj.{3}.{1}:\n" \
              "            data.append({2}(d))\n" \
              "    return data\n\n"

obj = "obj"
use_alt_tree = True

from A1_44 import A1_44 as check_repeated

for line in file.readlines():
    use2, use3, use4 = False, False, False
    if line[0] == '*':
        line = line[1:]
        use2 = True
    elif line[0] == '+':
        if line[1] == '+':
            line = line[2:]
            use4 = True
        else:
            line = line[1:]
            use3 = True

    line = line[1:-2]
    cname = line.title()
    mname = line[0].lower()
    for c in line[1:]:
        if c.isupper():
            mname += "_{0}".format(c.lower())
        else:
            mname += c

    tree_str = "'{{0}}.{0}'.format(self._header)".format(line)
    if use_alt_tree:
        tree_str = "'{0}'".format(line)

    if use2:
        if check_repeated:
            if not getattr(check_repeated, mname, False):
                out.write(method_class.format(
                    mname,
                    obj,
                    tree_str,
                    cname,
                ))
        else:
            out.write(method_class.format(
                mname,
                obj,
                tree_str,
                cname,
            ))
    elif use3:
        if check_repeated:
            if not getattr(check_repeated, mname, False):
                out.write(method_list.format(
                    mname,
                    cname,
                    line
                ))
        else:
            out.write(method_list.format(
                mname,
                cname,
                line
            ))
    elif use4:
        mname_ind = mname[:-4]
        if mname_ind.endswith('es'):
            mname_ind = mname_ind[:-2]
        elif mname_ind.endswith('s'):
            mname_ind = mname_ind[:-1]
        cname = mname_ind.title()
        if check_repeated:
            if not getattr(check_repeated, mname, False):
                out.write(method_list2.format(
                    mname,
                    mname_ind,
                    cname,
                    line
                ))
        else:
            out.write(method_list2.format(
                mname,
                mname_ind,
                cname,
                line
            ))
    else:
        if check_repeated:
            if not getattr(check_repeated, mname, False):
                out.write(method.format(
                    mname,
                    obj,
                    tree_str,
                ))
        else:
            out.write(method.format(
                mname,
                obj,
                tree_str,
            ))
