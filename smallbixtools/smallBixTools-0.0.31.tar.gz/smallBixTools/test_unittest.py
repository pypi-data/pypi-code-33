import unittest
from smallBixTools import smallBixTools as st
import os
import tempfile


class MyTestCase(unittest.TestCase):
    def test_compare_seqs_of_fasta_files(self):
        f1_content = ">a\nTTT"
        f2_content = ">b\nTTT"
        f1_fn = os.path.join(tempfile.gettempdir(), "f1.fasta")
        f2_fn = os.path.join(tempfile.gettempdir(), "f2.fasta")
        with open(f1_fn, "w") as fw:
            fw.write(f1_content)
        with open(f2_fn, "w") as fw:
            fw.write(f2_content)
        # returns a tuple of lists. ([ in fn1 and not in fn2], [ in fn2 and not in fn1], [ in both])
        x = st.compare_fasta_files(f1_fn, f2_fn)

        # So, if they are the same, there should be nothing in teh first two, and only 1 item in the last.
        assert len(x[0]) == 0
        assert len(x[1]) == 0
        assert len(x[2]) == 1

if __name__ == '__main__':
    unittest.main()

