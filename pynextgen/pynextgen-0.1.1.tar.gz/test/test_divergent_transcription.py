import os
import pytest
import subprocess
from easydev import md5
import shutil
import pynextgen.divtrans as dt
import pynextgen.basics_bam as bb

# TODO:
# Use tempdir like in test_utils.py


# Remove the log at the end of all the tests (Log file is apparently
# created at the import of the logging_config and will not be created
# again if removed at the end of each function test)
@pytest.fixture(scope="module")
def final_cleanup(request):
    def teardown():
        os.remove("common.log")
        os.remove("test/divtrans/vehicule_fos_area_nameSort.bam")

    request.addfinalizer(teardown)


TEST_DIR = "test/divtrans/"

BAM = "test/divtrans/vehicule_fos_area.bam"
OUTFOLDER = TEST_DIR + "bed_outfolder/"


def test_divergent_transcription_cli(tmpdir):
    """ Test the divergent_transcription.py script
    """

    cmd = f"python pynextgen/scripts/divergent_transcription.py {BAM} --out-folder {tmpdir}"

    subprocess.check_output(cmd, shell=True)


def test_fos(final_cleanup, tmpdir):
    """ Test detection of divergent transcription in the mini FOS dataset
    """

    # From bam fragments
    divtrans_bed = dt.get_divergent_transcription_beds(
        BAM, out_folder=tmpdir, distance=500, reuse=False
    )

    assert md5(divtrans_bed.path) == md5(TEST_DIR + "vehicule_fos_area_divtrans.bed")

    # Testing coverage filtering
    dt.filter_by_coverage(divtrans_bed, BAM, "test/divtrans/chro_sizes.txt")

    # From fragments computed with bedtools (old version)

    divtrans_from_bed = dt.DivTransFromBed(BAM)
    divtrans_from_bed.run()

    print(divtrans_from_bed.divtrans_bed.path)

    assert md5(divtrans_from_bed.divtrans_bed.path) == md5(
        TEST_DIR + "vehicule_fos_area_divtrans_from_bed.bed"
    )


def test_cases_divtrans(tmpdir):
    """Test different cases of reads positionning which should lead, or
    not to the detection of a divergent transcription event """

    bam = bb.generate_bam(
        tmpdir.join("basic.bam"),
        "test/divtrans/bam_header.sam",
        "test/divtrans/reads_for_bam.tsv",
    ).path

    # For igv session
    bb.generate_bam(
        "test/divtrans/basic.bam",
        "test/divtrans/bam_header.sam",
        "test/divtrans/reads_for_bam.tsv",
    ).path

    divtrans_bed = dt.get_divergent_transcription_beds(
        bam,
        out_folder=tmpdir,
        distance=200,
        max_template_length=400,
        reuse=False,
        no_overlap=False,
    )

    assert md5(divtrans_bed.path) == md5(TEST_DIR + "basic.bed")

    bed = divtrans_bed.merge()

    dt.filter_by_coverage(
        divtrans_bed,
        bam,
        "test/divtrans/chro_sizes.txt",
        cov_thres=3,
        cov_ratio_thres=1,
    )
