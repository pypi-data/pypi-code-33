from pynextgen.divtrans import get_divergent_transcription_beds
import fire

# FIXME A little clumsy way to avoid calling
# fire.Fire(get_divergent_transcription_beds) and avoiding the
# formating of the returned object (Bed object here)
def divtrans_alias(
    bam,
    out_folder="bed_outfolder",
    distance=100,
    no_overlap=False,
    remove_GL_contigs=True,
):
    get_divergent_transcription_beds(
        bam,
        out_folder=out_folder,
        distance=distance,
        no_overlap=no_overlap,
        remove_GL_contigs=remove_GL_contigs,
    )


def main():
    fire.Fire(divtrans_alias)


if __name__ == "__main__":
    main()
