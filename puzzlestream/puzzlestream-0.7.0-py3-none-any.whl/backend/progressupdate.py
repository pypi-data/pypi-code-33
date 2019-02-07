queue = None


def progressUpdate(finished, total=None):
    """Update module progress.

    There are three ways of specifying the progress:

    - finished as float between 0 and 1

    - finished as integer between 0 and 100

    - finished as arbitrary integer with total the total amount of items to be
      finished.

    Args:
        finished (float/int): Either between 0 and 1 or integer.
        total (int): Total number of items to be finished.
    """
    if total is None and isinstance(finished, float):
        if finished < 0:
            finished = 0
        elif finished > 1:
            finished = 1
        queue.put(finished)
    elif total is None and isinstance(finished, int):
        if finished < 0:
            finished = 0
        elif finished > 100:
            finished = 100
        finished /= 100.
        queue.put(finished)
    else:
        finished = finished / total
        progressUpdate(finished)
