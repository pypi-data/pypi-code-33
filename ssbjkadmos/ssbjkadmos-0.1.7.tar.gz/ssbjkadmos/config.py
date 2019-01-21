root_tag = 'dataSchema'

cat1 = 'aircraft/geometry'
cat2 = 'aircraft/weight'
cat3 = 'aircraft/other'
cat4 = 'reference'
cat5 = 'scaledData'
x_root = '/' + root_tag

x_tc = '/'.join([x_root, cat1, 'tc'])
x_AR = '/'.join([x_root, cat1, 'AR'])
x_Lambda = '/'.join([x_root, cat1, 'Lambda'])
x_Sref = '/'.join([x_root, cat1, 'Sref'])
x_Theta = '/'.join([x_root, cat1, 'Theta'])
x_lambda = '/'.join([x_root, cat1, 'lambda'])
x_section = '/'.join([x_root, cat1, 'section'])

x_WT = '/'.join([x_root, cat2, 'WT'])
x_WBE = '/'.join([x_root, cat2, 'WBE'])
x_WE = '/'.join([x_root, cat2, 'WE'])
x_WF = '/'.join([x_root, cat2, 'WF'])
x_WFO = '/'.join([x_root, cat2, 'WFO'])
x_WO = '/'.join([x_root, cat2, 'WO'])

x_D = '/'.join([x_root, cat3, 'D'])
x_L = '/'.join([x_root, cat3, 'L'])
x_Cf = '/'.join([x_root, cat3, 'Cf'])
x_CDmin = '/'.join([x_root, cat3, 'CDmin'])
x_T = '/'.join([x_root, cat3, 'T'])
x_DT = '/'.join([x_root, cat3, 'DT'])
x_fin = '/'.join([x_root, cat3, 'fin'])
x_SFC = '/'.join([x_root, cat3, 'SFC'])
x_dpdx = '/'.join([x_root, cat3, 'dpdx'])
x_R = '/'.join([x_root, cat3, 'R'])
x_Nz = '/'.join([x_root, cat3, 'Nz'])
x_sigma1 = '/'.join([x_root, cat3, 'sigma1'])
x_sigma2 = '/'.join([x_root, cat3, 'sigma2'])
x_sigma3 = '/'.join([x_root, cat3, 'sigma3'])
x_sigma4 = '/'.join([x_root, cat3, 'sigma4'])
x_sigma5 = '/'.join([x_root, cat3, 'sigma5'])

x_h = '/'.join([x_root, cat4, 'h'])
x_M = '/'.join([x_root, cat4, 'M'])
x_ESF = '/'.join([x_root, cat4, 'ESF'])
x_Temp = '/'.join([x_root, cat4, 'Temp'])

x_R__scr = '/'.join([x_root, cat5, 'R', 'scaler'])
x_R__val = '/'.join([x_root, cat5, 'R', 'value'])
x_sigma1__scr = '/'.join([x_root, cat5, 'sigma1', 'scaler'])
x_sigma1__val = '/'.join([x_root, cat5, 'sigma1', 'value'])
x_sigma2__scr = '/'.join([x_root, cat5, 'sigma2', 'scaler'])
x_sigma2__val = '/'.join([x_root, cat5, 'sigma2', 'value'])
x_sigma3__scr = '/'.join([x_root, cat5, 'sigma3', 'scaler'])
x_sigma3__val = '/'.join([x_root, cat5, 'sigma3', 'value'])
x_sigma4__scr = '/'.join([x_root, cat5, 'sigma4', 'scaler'])
x_sigma4__val = '/'.join([x_root, cat5, 'sigma4', 'value'])
x_sigma5__scr = '/'.join([x_root, cat5, 'sigma5', 'scaler'])
x_sigma5__val = '/'.join([x_root, cat5, 'sigma5', 'value'])
x_Theta__scr = '/'.join([x_root, cat5, 'Theta', 'scaler'])
x_Theta__val = '/'.join([x_root, cat5, 'Theta', 'value'])
x_dpdx__scr = '/'.join([x_root, cat5, 'dpdx', 'scaler'])
x_dpdx__val = '/'.join([x_root, cat5, 'dpdx', 'value'])
x_ESF__scr = '/'.join([x_root, cat5, 'ESF', 'scaler'])
x_ESF__val = '/'.join([x_root, cat5, 'ESF', 'value'])
x_DT__scr = '/'.join([x_root, cat5, 'DT', 'scaler'])
x_DT__val = '/'.join([x_root, cat5, 'DT', 'value'])
x_Temp__scr = '/'.join([x_root, cat5, 'Temp', 'scaler'])
x_Temp__val = '/'.join([x_root, cat5, 'Temp', 'value'])

