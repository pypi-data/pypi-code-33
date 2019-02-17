import webbrowser
import urllib.request

from errorcalcs import calc

def check_online():
    try:
        urllib.request.urlopen('https://github.com/')
        return True
    except:
        return False

def open_usage():
    status = check_online()
    if status == True:
        webbrowser.open_new(
        'https://github.com/leonfrcom/ErroRCalcS/blob/master/README.md'
        )
    else:
        return 'no_connection'

def open_donation():
    status = check_online()
    if status == True:
        webbrowser.open_new('https://paypal.me/leonfrcom')
    else:
        return 'no_connection'

def export_formula(status, var, formel, pfad):
    part_abl = calc.part_abl(var, formel)
    gauss_raw = '∆s = sqrt((∂s/∂x)^2 * (dx)^2 + (∂s/∂y)^2 * (dy)^2)\n'
    gauss_Tex = '\Delta_{s}=\sqrt{(\\frac{\partial s}{\partial x})^{2}*(dx)^{2}+(\\frac{\partial s}{\partial y})^{2}*(dy)^{2}}\n'
    try:
        datei_part_abl = open(pfad, 'a')
    except:
        datei_part_abl = open(pfad, 'w')

    if status == 'LaTex':
        print('--------LaTex--------', file = datei_part_abl)
        print('general formula:\n', gauss_Tex, file = datei_part_abl)
        x = ''
        for i in range(len(part_abl)):
            x += '('
            x += str(part_abl[i]).replace('**', '^')
            x += ')^{2} * (d'
            x += str(var[i]).replace('**', '^')
            x += ')^{2}'
            if i+1 != len(part_abl):
                x += '+'
            
        p_d = '\Delta_{s} = \sqrt{'+ x + '}\n'  
        print(formel + ':\n', p_d, file = datei_part_abl)
        datei_part_abl.close()
        
    if status == 'raw':
        print('--------raw--------', file = datei_part_abl)
        print('general formula:', gauss_raw, file = datei_part_abl)
        for i in range(len(part_abl)):
            x = '('
            x += str(part_abl[i])
            x += ')^2 * (d'
            x += str(var[i])
            x += ')^2'
            if i+1 != len(part_abl):
                x += '+'
        p_d = '∆s = sqrt(' + x + ')\n'
        print(formel + ':', p_d, file = datei_part_abl)
        datei_part_abl.close()
        
def open_fomula(pfad):
    try:
        webbrowser.open(pfad)
    except:
        print('File not found: part_derivations.txt')
        

def get_ins():
    var = []
    value = []
    error = []
    formel = []
    
    var_datei = open('.__log__/var.txt', 'r')
    value_datei = open('.__log__/value.txt', 'r')
    error_datei = open('.__log__/error.txt', 'r')
    formel_datei = open('.__log__/formel.txt', 'r')
    
    for line in var_datei:
        var.append(line.strip())
    for line in value_datei:
        value.append(float(line.strip()))
    for line in error_datei:
        error.append(float(line.strip()))
    for line in formel_datei:
        formel.append(line.strip().replace(',', '.'))
        
    var_datei.close()
    value_datei.close()
    error_datei.close()
    formel_datei.close()
    
    return var, value, error, formel
