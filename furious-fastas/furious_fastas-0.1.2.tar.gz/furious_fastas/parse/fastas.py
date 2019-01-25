from ..fasta import Fasta

def parse(fastas):
    """Parse a big string with fastas."""
    ff = fastas.split(">")[1:]
    ff = [">"+i for i in ff]
    for f in ff:
        f = f.split("\n")
        header = f[0]
        sequence = "".join(f[1:])
        yield Fasta(header, sequence)


def test_parse():
    fasta = ">sp|P61513|RL37A_HUMAN 60S ribosomal protein L37a OS=Homo sapiens OX=9606 GN=RPL37A PE=1 SV=2\nMAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSC\nMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ\n>sp|P61513|RL37A_HUMAN 60S ribosomal protein L37a OS=Homo sapiens OX=9606 GN=RPL37A PE=1 SV=2\nMAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSC\nMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ\n"
    r = list(parse(fasta))
    assert len(r) == 2
    assert str(r[0]) == "MAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSCMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ"
    assert str(r[1]) == "MAKRTKKVGIVGKYGTRYGASLRKMVKKIEISQHAKYTCSFCGKTKMKRRAVGIWHCGSCMKTVAGGAWTYNTTSAVTVKSAIRRLKELKDQ"
