#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import math
import csv
import logger

# minimum and maximum surface exposition to be considered
min_surf = 10
max_surf = 55
_name = "agg3D"


class Residue:
    def __init__(self, chain, resi, resn, coords, rsa, score_matrix):
        if chain == ' ':
            self.chain = '-'
        else:
            self.chain = chain
        self.resi = resi
        self.resn = get_one_letter(resn)   # we store it in one-letter code
        self.coords = coords
        self.score_matrix = score_matrix
        self.agg_sup = self.calc_res_agg_fin(rsa=rsa)
        self.agg_fin = 0

    def __str__(self):
        return self.chain+self.resn

    def set_agg_fin(self, agg_dis_sum):
        self.agg_fin = self.agg_sup + agg_dis_sum

    def id(self):
        return self.chain+self.resn+self.resi

    def set_rsa(self, rsa):
        self.agg_sup = self.calc_res_agg_fin(rsa=rsa)

    def calc_res_agg_fin(self, rsa):
        if rsa < min_surf:
            return 0
        else:
            if rsa > max_surf:
                rsa = max_surf
            return float(self.score_matrix[self.resn]) * 0.0599 * math.exp(0.0521 * rsa)


class Protein:
    def __init__(self, pdb_code, residues, out_dir, max_dist):
        self.name = pdb_code
        self.residues = residues
        self.out_dir = out_dir
        self.max_dist = max_dist

    def __str__(self):
        return self.name

    def add_residue(self, res):
        self.residues.append(res)

    def change_res_rsa(self, res_number, res_id, rsa):
        if self.residues[res_number].id() == res_id:
            self.residues[res_number].set_rsa(rsa)
        else:
            logger.critical(module_name=_name,
                            msg="Error while parsing freeSasa output. Probably freeSasa failed quietly.")
            logger.critical(module_name=_name,
                            msg="Failed to assign rsa to %s proper id is: %s " %
                                (res_id, self.residues[res_number].id()) +
                            "(ChainID, residue's one letter code, residue's ID)")
            raise logger.AggrescanError("Failed to parse freeSasa output. Qutting.",
                                        module_name=_name)

    def calc_agg_fin(self):
        """Calculate the agg_dis_sum for every Residue in the Protein"""
        dist_correction = -2.56 / self.max_dist
        for central in self.residues:
            agg_dis_sum = 0
            if not central.agg_sup == 0:
                for peripheric in self.residues:
                    dist = get_distance(central.coords, peripheric.coords)
                    if dist < self.max_dist and not dist == 0:
                        agg_dis_sum += peripheric.agg_sup * 1.2915 * math.exp(dist_correction*dist)
            central.set_agg_fin(agg_dis_sum)

    def short_summary(self):
        """Return a short summarized output and identify it with a leading #"""
        total_sum = 0
        maximum = 0
        minimum = 0
        pos_auc = 0
        neg_auc = 0
        prev_score = 0
        res_number = len(self.residues)
        for res in self.residues:
            total_sum += res.agg_fin
            if res.agg_fin > maximum:
                maximum = res.agg_fin
            if res.agg_fin < minimum:
                minimum = res.agg_fin
            if res.agg_fin != 0:
                if prev_score != 0:
                    auc = (res.agg_fin + prev_score)/2
                    if auc > 0:
                        pos_auc += abs(auc)
                    else:
                        neg_auc += abs(auc)
                prev_score = res.agg_fin
        return '#' + self.name + " " + ' '.join(str("%.4f" % round(val, 4))
                                                for val in (total_sum,
                                                total_sum/res_number,
                                                maximum,
                                                minimum,
                                                pos_auc))

    def long_output(self):
        """Return the complete output and identify it with a leading //"""
        output = ""
        for res in self.residues:
            output += '//' + " ".join((res.chain, res.resi, res.resn)) + " %.4f\n" % round(res.agg_fin, 4)
        return output

    def out_csv(self):
        """Save the complete output in a csv file"""
        csv_file = os.path.join(self.out_dir, "A3D.csv")
        c = csv.writer(open(csv_file, "w"))
        if os.stat(csv_file).st_size == 0:
            c.writerow(["protein", "chain", "residue", "residue_name", "score"])
        for res in self.residues:
            c.writerow([self.name.split("/")[-1], res.chain, res.resi, res.resn, "%.4f" % round(res.agg_fin, 4)])

    def get_residues(self):
        return self.residues


def get_one_letter(raw):
    """Return the one letter code for a residue"""
    if len(raw) > 3:
        aa = raw[-3:]
    else:
        aa = raw

    three_letters = aa.capitalize()

    conversion = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
                  "Glu": "E", "Gln": "Q", "Gly": "G", "His": "H", "Ile": "I",
                  "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P",
                  "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V"}
    try:
        one_letter = conversion[three_letters]
    except KeyError:
        logger.warning(module_name=_name,
                       msg='Could not recognize the following residue symbol: "%s"' % raw)
        one_letter = None
    return one_letter


def get_distance(a, b):
    """Return the distance between two cartesian tri dimensional points"""
    return math.sqrt((a[0] - b[0])**2 +
                     (a[1] - b[1])**2 +
                     (a[2] - b[2])**2)


def parse_matrix(filename=''):
    """Parse the matrix input into a dictionary"""
    with open(filename, 'r') as fh:
        matdict = {}
        for line in fh.readlines():
            if not line == '\n':
                pair = line.strip().split(" ")
                matdict[pair[0]] = pair[1]

    return matdict


def parse_naccess(pdb_code, work_dir, score_matrix, max_dist):
    """Parse the output of naccess into an object of class Protein"""
    with open(os.path.join(work_dir,pdb_code) + ".rsa", "r") as fh:
        rsa_dict = {line[3:8].strip() +  # resn
                    line[8] +   # chain
                    line[9:16].strip():  # resi
                    float(line[22:28].strip())  # rsa
                    for line in fh.readlines()
                    if line.startswith('RES')}

    my_protein = Protein(pdb_code=pdb_code, residues=[], out_dir=work_dir, max_dist=max_dist)
    center_atom = 'CA'  # atom to be considered the center of the residue

    with open(os.path.join(work_dir,pdb_code) + '.asa', 'r') as fh:
        for line in fh.readlines():
            # use data only from alpha carbons
            if line[12:16].strip() == center_atom:
                # extract the data according to the characteristics of the pdb format
                my_chain = line[21]
                my_resi = line[22:29].strip()
                my_resn = line[17:20].strip()
                x = float(line[30:38].strip())
                y = float(line[38:46].strip())
                z = float(line[46:54].strip())
                res_id = my_resn + my_chain + my_resi
                my_rsa = rsa_dict[res_id]
                my_protein.add_residue(Residue(chain=my_chain,
                                               resi=my_resi,
                                               resn=my_resn,
                                               coords=(x, y, z),
                                               rsa=my_rsa,
                                               score_matrix=score_matrix))
    return my_protein


def parse_freesasa(pdb_code, work_dir, filename, score_matrix, max_dist):
    my_protein = Protein(pdb_code=pdb_code, residues=[], out_dir=work_dir, max_dist=max_dist)
    residue_count = 0
    central_atom = 'CA'   # atom to be considered the center of the residue
    with open(os.path.join(work_dir, filename), 'r') as f:
        for line in f:
            if line.startswith("ATOM "):  # this is the same as naccess asa file
                if line[12:16].strip() == central_atom:
                    # extract the data according to the characteristics of the pdb format
                    my_chain = line[21]
                    my_resi = line[22:29].strip()
                    my_resn = line[17:20].strip()
                    x = float(line[30:38].strip())
                    y = float(line[38:46].strip())
                    z = float(line[46:54].strip())
                    my_protein.add_residue(Residue(chain=my_chain,
                                                   resi=my_resi,
                                                   resn=my_resn,
                                                   coords=(x, y, z),
                                                   rsa=0,
                                                   score_matrix=score_matrix))
            elif line.startswith("RES"):   # equivalent to naccess rsa file
                this_id = line[8] + get_one_letter(line[3:8].strip()) + line[9:16].strip()
                rsa = float(line[22:28].strip())
                my_protein.change_res_rsa(res_number=residue_count, res_id=this_id, rsa=rsa)
                residue_count += 1

    return my_protein


def run(pdb_file='', mat_file='', max_dist='', work_dir='', naccess=False):
    score_matrix = parse_matrix(filename=mat_file)
    pdb_code = pdb_file.split(".")[0]
    if naccess:
        my_protein = parse_naccess(pdb_code=pdb_code, work_dir=work_dir,
                                   score_matrix=score_matrix, max_dist=max_dist)
    else:
        my_protein = parse_freesasa(pdb_code=pdb_code, work_dir=work_dir,
                                    filename="sasa.out", score_matrix=score_matrix, max_dist=max_dist)
    my_protein.calc_agg_fin()
    my_protein.out_csv()
    short_summary = my_protein.short_summary()+"\n"
    long_summary = my_protein.long_output()
    return short_summary + long_summary
