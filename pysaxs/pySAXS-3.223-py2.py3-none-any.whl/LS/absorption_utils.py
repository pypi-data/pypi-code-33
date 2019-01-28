from numpy import *
ATOMS=[	"H","He","Li","Be","B","C","N","O","F","Ne","Na","Mg","Al","Si","P","S","Cl","Ar","K","Ca","Sc","Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Ga","Ge","As","Se","Br","Kr","Rb","Sr","Y","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","In","Sn","Sb","Te","I","Xe","Cs","Ba","La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg","Tl","Pb","Bi","Po","At","Rn","Fr","Ra","Ac","Th","Pa","U"]

ATOMS_NAME=["Hydrogen","Helium","Lithium","Beryllium","Boron","Carbon, Graphite","Nitrogen","Oxygen","Fluorine","Neon","Sodium","Magnesium","Aluminum","Silicon","Phosphorus","Sulfur","Chlorine","Argon","Potassium","Calcium","Scandium","Titanium","Vanadium","Chromium","Manganese","Iron","Cobalt","Nickel","Copper","Zinc","Gallium","Germanium","Arsenic","Selenium","Bromine","Krypton","Rubidium","Strontium","Yttrium","Zirconium","Niobium","Molybdenum","Technetium","Ruthenium","Rhodium","Palladium","Silver","Cadmium","Indium","Tin","Antimony","Tellurium","Iodine","Xenon","Cesium","Barium","Lanthanum","Cerium","Praseodymium","Neodymium","Promethium","Samarium","Europium","Gadolinium","Terbium","Dysprosium","Holmium","Erbium","Thulium","Ytterbium","Lutetium","Hafnium","Tantalum","Tungsten","Rhenium","Osmium","Iridium","Platinum","Gold","Mercury","Thallium","Lead","Bismuth","Polonium","Astatine","Radon","Francium","Radium","Actinium","Thorium","Protactinium","Uranium"]

COMMON_XRAY_SOURCE_MATERIALS=['Cu','Cr','Mo']
COMMON_XRAY_SOURCE_ENERGY={'Cu':8.04105057076251,'Cr':5.41159550114,'Mo':17.4432170305}

ATOMS_MASSE=array([1.0079,4.0026,6.9410,9.0122,10.8110,12.0107,14.0067,15.9994,18.9984,20.1797,22.9897,24.3050,26.9815,28.0855,30.9738,32.0650,35.4530,39.9480,39.0983,40.0780,44.9559,47.8670,50.9415,51.9961,54.9380,55.8450,58.9332,58.6934,63.5460,65.3900,69.7230,72.6400,74.9216,78.9600,79.9040,83.8000,85.4678,87.6200,88.9059,91.2240,92.9064,95.9400,98.0000,101.0700,102.9055,106.4200,107.8682,112.4110,114.8180,118.7100,121.7600,127.6000,126.9045,131.2930,132.9055,137.3270,138.9055,140.1160,140.9077,144.2400,145.0000,150.3600,151.9640,157.2500,158.9253,162.5000,164.9303,167.2590,168.9342,173.0400,174.9670,178.4900,180.9479,183.8400,186.2070,190.2300,192.2170,195.0780,196.9665,200.5900,204.3833,207.2000,208.9804,209.0000,210.0000,222.0000,223.0000,226.0000,227.0000,232.0381,231.0359,238.0289,237.0000],float)

MENDELEIEV_TABLE =[['H', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 'He'],\
            ['Li', 'Be', None, None, None, None, None, None, None, None, None, None, 'B', 'C', 'N', 'O', 'F', 'Ne'],\
             ['Na', 'Mg', None, None, None, None, None, None, None, None, None, None, 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],\
              ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],\
               ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],\
               ['Cs','Ba','La','Hf','Ta','W','Re','Os','Ir','Pt','Au','Hg','Tl','Pb','Bi','Po','At','Rn'],\
               ['Fr','Ra','Ac',None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],\
               ['Ce','Pr','Nd','Pm','Sm','Eu','Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu',None, None, None, None],\
               ['Th', 'Pa', 'U', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]]

KEV2ANGST = 12.39841875

COMPOUNDS = {'SiO2':['Si 1.0 O 2.0',2.196],\
             'Au':['Au 1.0',19.32],\
             'TiO2 powder':['Ti 1.0 O 2.0',4.23],\
             'H2O':['H 2.0 O 1.0',0.997]}