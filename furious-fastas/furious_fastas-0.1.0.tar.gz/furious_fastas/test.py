%load_ext autoreload
%autoreload 2

path2human = "/home/matteo/Projects/furious_fastas/4peaks/human.fasta"
# path2human = "/Users/matteo/Projects/furious_fastas/test/human.fasta"

## works!!!
# from furious_fastas.download import download
# url = "http://www.uniprot.org/uniprot/?query=reviewed:yes+AND+organism:9606&format=fasta"
# human = download(url)
# human.write(path2human)

# # works!!!
# from furious_fastas.fastas import Fastas
# from furious_fastas.contaminants import conts
# human = Fastas()
# human.read(path2human)
# human
# human + conts

from furious_fastas.parse.species2uniprot import parse
from furious_fastas.update.peaks import update_peaks
from furious_fastas.update.plgs import update_plgs

s2u = list(parse("/home/matteo/Projects/furious_fastas/4peaks/s2u2"))
update_plgs("/home/matteo/Projects/furious_fastas/4peaks/db2", s2u)


db_path = "/home/matteo/Projects/furious_fastas/4peaks/db2"
species2url = s2u

from furious_fastas.contaminants import conts
from furious_fastas.download import download