import shutil
from smallBixTools import smallBixTools as st
import pandas as pd
import random
import os
import tempfile
import unittest
from smallBixTools import haplotype_aligned_file
# from get_fasta_for_tree_from_dist_bins2 import main as main_to_Test
# from get_fasta_for_tree_from_dist_bins2 import get_random_sample_from_bins as random_sample_method_to_test
# from get_fasta_for_tree_from_dist_bins2 import harvest_seqs_from_fasta as harvest_method_to_test


class getFastaFromCSVTests(unittest.TestCase):

    def test_in_csv_file_exists_check(self):
        """
        Checks that the main function correctly raises an IOError when a csv filepath which doesn't exist is given to it
        :return: No return
        """
        random_path_name = "".join([chr(random.randint(97, 122)) for x in range(50)])
        path_with_doesnt_exist = os.path.join(tempfile.gettempdir(), random_path_name)
        with self.assertRaises(IOError):
            main_to_Test(random_path_name, tempfile.gettempdir(), tempfile.gettempdir())

    # def test_require_headings(self):
    #     # write incorrectly formatted file to disc, to send as input
    #     bad_file_content = "poor,headings\n" \
    #                        "1,2"
    #     tmp_fn = tempfile.NamedTemporaryFile(delete=False).name
    #     with open(tmp_fn, "w") as fw:
    #         fw.write(bad_file_content)
    #     with self.assertRaises(ValueError):
    #         main_to_Test(tmp_fn, tempfile.gettempdir(), tempfile.gettempdir())
    #
    #     # clean up
    #     os.remove(tmp_fn)
    #
    # def test_fasta_path_check(self):
    #     """
    #     Checks that the main function correctly raises an IOError when an fasta path which doesn't exist is given to it
    #     :return: No return
    #     """
    #     # write file with correctly formatted headings to disc, to send as input
    #     good_file_content = "Recipient,recip_full_name,Donor,donor_full_name,hit_percent_match,hit_length\n" \
    #                        "1,2,3,4,5,6"
    #     tmp_fn = tempfile.NamedTemporaryFile(delete=False).name
    #     with open(tmp_fn, "w") as fw:
    #         fw.write(good_file_content)
    #     random_path_name = "".join([chr(random.randint(97, 122)) for x in range(50)])
    #     path_with_doesnt_exist = os.path.join(tempfile.gettempdir(), random_path_name)
    #     with self.assertRaises(IOError):
    #         main_to_Test(tmp_fn, path_with_doesnt_exist, tempfile.gettempdir())
    #
    #     # clean up
    #     os.remove(tmp_fn)
    #
    # def test_outpath_check(self):
    #     """
    #     Checks that the main function correctly raises an IOError when an output path which doesn't exist is given to it
    #     :return: No return
    #     """
    #     # write file with correctly formatted headings to disc, to send as input
    #     good_file_content = "Recipient,recip_full_name,Donor,donor_full_name,hit_percent_match,hit_length\n" \
    #                        "1,2,3,4,5,6"
    #     tmp_fn = tempfile.NamedTemporaryFile(delete=False).name
    #     with open(tmp_fn, "w") as fw:
    #         fw.write(good_file_content)
    #     random_path_name = "".join([chr(random.randint(97, 122)) for x in range(50)])
    #     path_with_doesnt_exist = os.path.join(tempfile.gettempdir(), random_path_name)
    #     random_path_name2 = "".join([chr(random.randint(97, 122)) for x in range(50)])
    #     path_with_doesnt_exist2 = os.path.join(tempfile.gettempdir(), random_path_name2)
    #     with self.assertRaises(IOError):
    #         main_to_Test(tmp_fn, path_with_doesnt_exist, path_with_doesnt_exist2)
    #
    #     # clean up
    #     os.remove(tmp_fn)
    #
    # def test_random_sampling_method(self):
    #     """
    #     Checks that the function to sample from a dataframe samples correctly from the dataframe.
    #     :return: No return
    #     """
    #     # write file with correctly formatted headings to disc, to send as input
    #     example_dataframe_dict = {'Recipient': ['KID112', 'KID112', 'KID112', 'KID112', 'KID113', 'KID113', 'KID113'],
    #                               'recip_full_name': ['KID112_a', 'KID112_b', 'KID112_c', 'KID112_d',
    #                                                   'KID113_a', 'KID113_b', 'KID113_c'],
    #                               'Donor': ['dnr1', 'dnr1', 'dnr1', 'dnr1', 'dnr2', 'dnr2', 'dnr2'],
    #                               'donor_full_name': ['dnr1', 'dnr1', 'dnr1', 'dnr1', 'dnr2', 'dnr2', 'bad_donor_name'],
    #                               'hit_percent_match': [60.1, 60.2, 60.3, 60.4, 70.1, 70.2, 70.6],  #70.6 will be removed from bad_donor_name
    #                               'hit_length': [300, 300, 300, 300, 300, 300, 300]
    #                               }
    #     example_dataframe = pd.DataFrame(example_dataframe_dict)
    #
    #     num_seqs_per_recip = 2
    #     bin_step = 0.5
    #     forbidden_donors = ['bad_donor_name']
    #     #print("before function call")
    #     result_dct = random_sample_method_to_test(example_dataframe, num_seqs_per_recip, bin_step, forbidden_donors)
    #     #print(result_dct)
    #     #print("after function call")
    #
    #     # There should be 2 sequence ids for KID112, because of the range (60.1 ~ 60.4) and the bin_step (0.5), and the
    #     # num_seqs_per_recip = 2
    #     kid112_results = result_dct["KID112"]
    #     #print(f"kid112 results: {kid112_results}")
    #     len_kid112_results = len(kid112_results)
    #
    #     kid113_results = result_dct["KID113"]
    #     #print(f"kid113 results: {kid113_results}")
    #     len_kid113_results = len(kid113_results)
    #
    #     self.assertEqual(len_kid112_results, 2)
    #     self.assertEqual(len_kid113_results, 2)
    #
    # def test_harvest_fasta_seqs_method(self):
    #     """
    #     Tests for the method to harvest sequences from fasta files.
    #     :return: No return
    #     """
    #     tmp_dir = tempfile.mkdtemp()
    #
    #     fasta_file_content_1 = {"seqid1": "ACGT", "seqid2": "ACGGT"}
    #     fasta_file_content_2 = {"seqid3": "ACGT", "seqid4": "ACGGT"}
    #     tmp_fn_1 = os.path.join(tmp_dir, "temp_file1.fasta")
    #     tmp_fn_2 = os.path.join(tmp_dir, "temp_file2.fasta")
    #
    #     st.dct_to_fasta(fasta_file_content_1, tmp_fn_1)
    #     st.dct_to_fasta(fasta_file_content_2, tmp_fn_2)
    #     print(f"Wrote to: {tmp_fn_1}")
    #     print(f"Wrote to: {tmp_fn_2}")
    #
    #     sampled_dict = {"file1": ["seqid1", "seqid2"], "file2": ["seqid3"]}
    #     search_fasta_files = [tmp_fn_1, tmp_fn_2]
    #
    #     expected_result = {}
    #     for seq_id in sampled_dict["file1"]:
    #         expected_result[seq_id] = fasta_file_content_1[seq_id]
    #     for seq_id in sampled_dict["file2"]:
    #         expected_result[seq_id] = fasta_file_content_2[seq_id]
    #
    #     harvested_entries, not_found_list = harvest_method_to_test(sampled_dict, search_fasta_files)
    #
    #     self.assertEqual(harvested_entries, expected_result)
    #     self.assertEqual(not_found_list, [])
    #
    #     # clean up
    #     shutil.rmtree(tmp_dir)
