import os
import shutil
import time

#dependencies
import nltk


def clean_dir(dir_path, just_files=True):
    """
    Clean up a directory.
    :param dir_path:
    :param just_files: If just_files=False, also remove all directory trees in that directory.
    :return:
    """
    for name in os.listdir(dir_path):
        name_path = os.path.join(dir_path, name)
        if os.path.isfile(name_path):
            os.remove(name_path)
        elif not just_files:
            if os.path.isdir(name_path):
                shutil.rmtree(name_path)



def documents_segementor_on_word_length(documents_dir, store_dir, max_length, language='english'):
    """
    segment a long document to several small documents based on the word length. sentence structure will be kept.
    :param documents_dir: where all documents located.
    :param store_dir: where to store segmented documents.
    :param max_length: document segments' max length.
    :param language: for the use of nltk, default english
    :return:
    """


# ------------------helper funcs-----------------------------