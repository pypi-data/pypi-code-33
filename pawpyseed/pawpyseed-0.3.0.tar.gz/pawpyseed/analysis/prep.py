from defect_composition import BulkCharacter
import os
import yaml

filenames = ['../bcfres__%s.yaml' % s for s in ['Bcharge_-1', 'Bcharge_0', 'Pcharge_0', 'Pcharge_1',\
		'charge_-2', 'charge_-1', 'charge_0', 'charge_1', 'charge_2']]
names = ['B substitutional -1', 'B substitutional 0', 'P substitutional 0',\
		'P substitutional +1', 'vacancy -2', 'vacancy -1', 'vacancy 0',
		'vacancy +1', 'vacancy +2']

filenames, names, dpaths = [], [], []
defects = ["vac_1_Si", "sub_1_B_on_Si", "sub_1_P_on_Si", "sub_1_Cu_on_Si", "sub_1_S_on_Si"]
mathnames = ["$\\mathrm{Vac}_{\\mathrm{Si}}$", "$\\mathrm{B}_\\{mathrm{Si}}$", "$\\mathrm{P}_{\\mathrm{Si}}$",\
"$\\rm{Cu}_{\\rm{Si}}$", "$\\rm{S}_{\\rm{Si}}$"]
charges = [[-2,-1,0,1,2], [-1,0], [0,1], [-1,0,1], [-2,-1,0,1,2,3]]
titles=[]
for i, d in enumerate(defects):
	for c in charges[i]:
		filenames.append(d+('_charge_%d' % c))
		dpaths.append(d+('/charge_%d' % c))
		names.append(d + (' Charge %d' % c))
		titles.append(mathnames[i] + (' Charge %d' % c))
my_dir = '/home/kyle/Research/projects/researchpapers/pawpyseed/thesis/results/projections'
#f = open(my_dir+'/bandedges.json', 'r')
f = open('bandedges2.json', 'r')
bandedges = yaml.load(f)
f.close()
filenames = [os.path.join(my_dir, 'bcf2res__%s.yaml' % s) for s in filenames]
print(filenames, names)

#filenames = ['testres0.yaml']
#names = ['testnew']

os.chdir('slidesres2')
for fname, name, dp, title in zip(filenames, names, dpaths, titles):
	be = bandedges[dp]
	bc = BulkCharacter.from_yaml(fname)
	bc.efermi = be['vbm']
	bc.vbm = be['vbm']
	bc.cbm = be['cbm']
	bc.plot(name, spinpol=True, title=title)
	print(fname, name, title)
