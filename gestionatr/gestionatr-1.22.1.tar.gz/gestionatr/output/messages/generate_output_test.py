

new_field = "{0} = {1}.{2}()\n"

fields_dict_cap = "{0}_fields = {{\n"
fields_dict_atr = "\t'{0}': {0},\n"
fields_dict_atr_simple = "\t'{0}': '',\n"
fields_dict_fi = "}\n"

feed_str = "{0}.feed({0}_fields)\n"


def generar(act_obj, misatge_name):
    out.write("\n# {0}\n".format(misatge_name))
    out.write(new_field.format(act_obj, proces, misatge_name))
    misatge = getattr(mdata, misatge_name)
    atributs = misatge._sort_order[1:]

    for atr in atributs:
        try:
            getattr(mdata, transform_string(atr, cap=False))
            generar(atr, transform_string(atr, cap=False))
            out.write("\n")
        except:
            try:
                getattr(mdata, transform_string(atr, cap=True))
                generar(atr, transform_string(atr, cap=True))
                out.write("\n")
            except:
                pass
    out.write(fields_dict_cap.format(act_obj))
    for atr in atributs:
        try:
            getattr(mdata, transform_string(atr))
            out.write(fields_dict_atr.format(atr))
        except:
            try:
                getattr(mdata, transform_string(atr, cap=True))
                out.write(fields_dict_atr.format(atr))
            except:
                out.write(fields_dict_atr_simple.format(atr))

    out.write(fields_dict_fi)
    out.write(feed_str.format(act_obj))


def transform_string(string, cap=False):
    nam_obj = ''
    for s in string.split('_'):
        if cap and len(s) < 4 and s != 'de':
            nam_obj += s.upper()
        elif cap:
            nam_obj += s.capitalize()
        else:
            nam_obj = s.strip()
    return nam_obj

from gestionatr.output.messages import sw_a1_48 as mdata
out = open("out.txt", 'w')
proces = 'a1_48'
mensaje = 'variableinf'
try:
    getattr(mdata, transform_string(mensaje, cap=False))
    generar(mensaje,transform_string(mensaje, cap=False))
except:
    getattr(mdata, transform_string(mensaje, cap=True))
    generar(mensaje,transform_string(mensaje, cap=True))

out.write("{0}.build_tree()\n".format(mensaje))
out.write("xml = str({0})\n".format(mensaje))
out.write("assertXmlEqual(xml, self.xml_{0}.read())\n\n".format(mensaje))
