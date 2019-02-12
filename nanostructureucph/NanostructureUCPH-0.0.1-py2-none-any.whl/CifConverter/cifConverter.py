import string

class cifConverter:
    """
    doc string
    """
    def __init__(self, fileName):  # Define what file should be converted
        """

        :param fileName:
        """
        print 'Running cifConverter'
        self.fileName = fileName

    def readCif(self):  # Print all imported lines in cif
        """
        doc string
        """
        print 'Reading {}'.format(self.fileName)
        self.cif = open(self.fileName, 'r+')

    def getInfo(self, removeSign=True):
        """

        :param removeSign:
        :return:
        """
        print 'Retrieving information from {}'.format(self.fileName)
        try:
            self.symOps       = []
            self.aniso11Val   = []
            self.aniso22Val   = []
            self.aniso33Val   = []
            self.aniso12Val   = []
            self.aniso13Val   = []
            self.aniso23Val   = []
            self.labelVal     = []
            self.symbolVal    = []
            self.fractXVal    = []
            self.fractYVal    = []
            self.fractZVal    = []
            self.bisoVal      = []
            self.occupancyVal = []
            for line in self.cif:
                if line[0:5] == 'data_':
                    self.ICSD = line
                elif line[0:28] == '_chemical_formula_structural':
                    self.chemFormula, self.chemFormulaVal = line.split(' ', 1)
                elif line[0:14] == '_cell_length_a':
                    self.a, self.aVal = line.split(' ')
                elif line[0:14] == '_cell_length_b':
                    self.b, self.bVal = line.split(' ')
                elif line[0:14] == '_cell_length_c':
                    self.c, self.cVal = line.split(' ')
                elif line[0:17] == '_cell_angle_alpha':
                    self.alpha, self.alphaVal = line.split(' ')
                    if "." in self.alphaVal[-2]:
                        self.alphaVal = self.alphaVal[:-2]
                        self.alphaVal += '\n'
                elif line[0:16] == '_cell_angle_beta':
                    self.beta, self.betaVal = line.split(' ')
                    if "." in self.betaVal[-2]:
                        self.betaVal = self.betaVal[:-2]
                        self.betaVal += '\n'
                elif line[0:17] == '_cell_angle_gamma':
                    self.gamma, self.gammaVal = line.split(' ')
                    if "." in self.gammaVal[-2]:
                        self.gammaVal = self.gammaVal[:-2]
                        self.gammaVal += '\n'
                elif line[0:30] == '_symmetry_space_group_name_H-M':
                    self.spaceGroup, self.spaceGroupVal = line.split(' ', 1)
                elif line[0:27] == '_symmetry_Int_Tables_number':
                    _, self.symITVal = line.split(' ')
                    self.symIT = '_space_group_IT_number'
                elif line[0:26] == '_symmetry_equiv_pos_as_xyz':  # Does not give the same order
                    i = 1
                    for j in range(99999):
                        nextLine = self.cif.next()
                        if nextLine[0:len(str(i))] == str(i):
                            _, self.symOps.append(nextLine.split(' ', 1))
                            i += 1
                        else:
                            break
                elif line[0:29] == '_atom_site_attached_hydrogens':
                    for i in range(99999):
                        nextLine = self.cif.next()
                        if nextLine[0] == '_' or nextLine[0:5] == 'loop_' or nextLine[0:4] == '#End':
                            break
                        else:
                            ph0, ph1, _, _, ph4, ph5, ph6, ph7, ph8, _ = nextLine.split(' ', 10)
                            self.labelVal.append(ph0)
                            if removeSign == True:
                                if ph1[-1] == '-' or ph1[-1] == '+':
                                    ph1 = ph1[:-1]
                            self.symbolVal.append(ph1)
                            self.fractXVal.append(ph4)
                            self.fractYVal.append(ph5)
                            self.fractZVal.append(ph6)
                            self.bisoVal.append(ph7)
                            self.occupancyVal.append(ph8)
                elif line[0:21] == '_atom_site_aniso_B_23':
                    for i in range(99999):
                        nextLine = self.cif.next()
                        if nextLine[0] == '_' or nextLine[0:5] == 'loop_' or nextLine[0:4] == '#End':
                            break
                        else:
                            _, _, ph0, ph1, ph2, ph3, ph4, ph5 = nextLine.split(' ', 8)
                            self.aniso11Val.append(ph0)
                            self.aniso22Val.append(ph1)
                            self.aniso33Val.append(ph2)
                            self.aniso12Val.append(ph3)
                            self.aniso13Val.append(ph4)
                            self.aniso23Val.append(ph5[0:-1])
            if self.aniso12Val == []:
                for i in range(len(self.labelVal)):
                    self.aniso11Val.append(0.005)
                    self.aniso22Val.append(0.005)
                    self.aniso33Val.append(0.005)
                    self.aniso12Val.append(0.000)
                    self.aniso13Val.append(0.000)
                    self.aniso23Val.append(0.000)
        finally:
            self.cif.close()

    def saveCif(self, overwrite=False,):
        """

        :param overwrite:
        :return:
        """
        cifString = cifConverter.setupCif(self)
        if overwrite == False:
            f = open(str(self.fileName[:-4])+"_CC.cif", "w+")
            f.write(cifString)
            print 'Saving new cif file, {}'.format(self.fileName[:-4]+"_CC.cif")
        else:
            f = open(str(self.fileName), "w+")
            f.write(cifString)
            print "Overwriting existing file, {}".format(self.fileName)
        f.close()

    def setupCif(self):
        """
        Does not need to be called. Will automatically be called when needed.
        doc string
        """
        print 'Generating cif layout from retrieved information'
        cifString = "{}\n".format(self.ICSD)
        cifString += "{} {}".format(self.chemFormula, self.chemFormulaVal)
        cifString += "{} {}".format(self.a, self.aVal)
        cifString += "{} {}".format(self.b, self.bVal)
        cifString += "{} {}".format(self.c, self.cVal)
        cifString += "{} {}".format(self.alpha, self.alphaVal)
        cifString += "{} {}".format(self.beta, self.betaVal)
        cifString += "{} {}".format(self.gamma, self.gammaVal)
        cifString += "{} {}".format(self.spaceGroup, self.spaceGroupVal)
        cifString += "{} {}".format(self.symIT, self.symITVal)
        cifString += "\n{}\n".format('loop_')
        cifString += "{}\n".format('_symmetry_equiv_pos_site_id')
        cifString += "{}\n".format('_symmetry_equiv_pos_as_xyz')
        for i in range(len(self.symOps)):
            cifString += "{} {}".format(i+1, self.symOps[i][1])
        cifString += "\n{}\n".format('loop_')
        cifString += "{}\n".format('_atom_site_label')
        cifString += "{}\n".format('_atom_site_type_symbol')
        cifString += "{}\n".format('_atom_site_fract_x')
        cifString += "{}\n".format('_atom_site_fract_y')
        cifString += "{}\n".format('_atom_site_fract_z')
        cifString += "{}\n".format('_atom_site_B_iso_or_equiv')
        cifString += "{}\n".format('_atom_site_occupancy')
        for i in range(len(self.labelVal)):
            cifString += "{} {} {} {} {} {} {}\n".format(self.labelVal[i], self.symbolVal[i], self.fractXVal[i], self.fractYVal[i],
                                                         self.fractZVal[i], self.bisoVal[i],  self.occupancyVal[i])
        cifString += "\n{}\n".format('loop_')
        cifString += "{}\n".format('_atom_site_aniso_label')
        cifString += "{}\n".format('_atom_site_aniso_type_symbol')
        cifString += "{}\n".format('_atom_site_aniso_B_11')
        cifString += "{}\n".format('_atom_site_aniso_B_22')
        cifString += "{}\n".format('_atom_site_aniso_B_33')
        cifString += "{}\n".format('_atom_site_aniso_B_12')
        cifString += "{}\n".format('_atom_site_aniso_B_13')
        cifString += "{}\n".format('_atom_site_aniso_B_23')
        for i in range(len(self.labelVal)):
            cifString += "{} {} {} {} {} {} {} {}\n".format(self.labelVal[i], self.symbolVal[i], self.aniso11Val[i], self.aniso22Val[i], self.aniso33Val[i],
                                                            self.aniso12Val[i], self.aniso13Val[i], self.aniso23Val[i])
        return cifString

    def setBiso(self, val, param=[], atom=''):
        """
        doc string
        :param val:
        :param param:
        :param atom:
        :return:
        """
        val = float(val)
        if param == []:
            if atom == '':
                for i in range(len(self.labelVal)):
                    self.aniso11Val[i] = val
                    self.aniso22Val[i] = val
                    self.aniso33Val[i] = val
                    self.aniso12Val[i] = val
                    self.aniso13Val[i] = val
                    self.aniso23Val[i] = val
                print 'All atoms Biso have been set to {}'.format(val)
            else:
                for i in range(len(self.labelVal)):
                    if self.labelVal[i][0:len(atom)] == atom:
                        self.aniso11Val[i] = val
                        self.aniso22Val[i] = val
                        self.aniso33Val[i] = val
                        self.aniso12Val[i] = val
                        self.aniso13Val[i] = val
                        self.aniso23Val[i] = val
                print 'All {} Biso values have been set to {}'.format(atom, val)
        else:
            for iso in param:
                for i in range(len(self.labelVal)):
                    if atom == '':
                        if iso == 11:
                            self.aniso11Val[i] = val
                        if iso == 22:
                            self.aniso22Val[i] = val
                        if iso == 33:
                            self.aniso33Val[i] = val
                        if iso == 12:
                            self.aniso12Val[i] = val
                        if iso == 13:
                            self.aniso13Val[i] = val
                        if iso == 23:
                            self.aniso23Val[i] = val
                    else:
                        if self.labelVal[i][0:len(atom)] == atom:
                            if iso == 11:
                                self.aniso11Val[i] = val
                            if iso == 22:
                                self.aniso22Val[i] = val
                            if iso == 33:
                                self.aniso33Val[i] = val
                            if iso == 12:
                                self.aniso12Val[i] = val
                            if iso == 13:
                                self.aniso13Val[i] = val
                            if iso == 23:
                                self.aniso23Val[i] = val
            print 'All {} atoms have their Biso_{} values set to {}'.format(atom, param, val)

    def changeAtom(self, replaceAtom, withAtom):
        """

        :param replaceAtom:
        :param withAtom:
        :return:
        """

        words = [w.replace(replaceAtom, withAtom) for w in self.labelVal]
        self.labelVal = words
        for i in range(1,9):
            words = [w.replace(replaceAtom+str(i), withAtom) for w in self.symbolVal]
            self.symbolVal = words
        words = [w.replace(replaceAtom, withAtom) for w in self.symbolVal]
        self.symbolVal = words
        print '{} has been replaced with {}'.format(replaceAtom, withAtom)

    def __str__(self):
        ret_str = 'This should be some informative information'
        return ret_str

if __name__ == "__main__":
    WO_test = cifConverter('W_1509.cif')
    WO_test.readCif()
    WO_test.getInfo()
    #WO_test.setBiso(1, param=[11, 22], atom='W')
    #WO_test.changeAtom('W', 'Nb')
    WO_test.saveCif()
