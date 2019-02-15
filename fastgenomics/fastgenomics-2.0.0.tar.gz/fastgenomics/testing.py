def cleanoutput(fg):
    """Deletes all the output files.  Useful for cleanup before tests."""
    for file in fg.output.keys():
        path = fg.output[file].path
        if path.exists():
            path.unlink()
