# -*- coding: utf-8 -*-


def to_text(path):
    """Wraps Tesseract OCR.

    Parameters
    ----------
    path : str
        path of electronic invoice in JPG or PNG format

    Returns
    -------
    extracted_str : str
        returns extracted text any out file

    """
    import subprocess
    from distutils import spawn

    # Check for dependencies. Needs Tesseract and Imagemagick installed.
    if not spawn.find_executable('tesseract'):
        raise EnvironmentError('tesseract not installed.')
    if not spawn.find_executable('convert'):
        raise EnvironmentError('imagemagick not installed.')

    # convert = "convert -density 350 %s -depth 8 tiff:-" % (path)
    cat = ['cat', path]
    p1 = subprocess.Popen(cat, stdout=subprocess.PIPE, shell=True)

    out, err = p1.communicate()

    extracted_str = out

    return extracted_str
