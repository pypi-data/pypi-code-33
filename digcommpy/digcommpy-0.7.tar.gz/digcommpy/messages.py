import numpy as np

_SEED = np.random.randint(0, 1000)


def unpack_to_bits(messages, num_bits):
    """This function converts an array of dec numbers into their binary
    representation.

    Parameters
    ----------
    messages : list
        List of messages (numbers)

    num_bits : int
        Number of output bits

    Returns
    -------
    binary_messages : array (N x num_bits)
        Converted messages as bits
    """
    #messages_bits = np.ones((np.shape(messages)[0], num_bits))
    #for idx, _mess in enumerate(messages):
    #    messages_bits[idx] = list(np.binary_repr(_mess, width=num_bits))
    num_bits = int(num_bits)
    messages_bits = [list(format(x, "0>{}b".format(num_bits))) for x in messages]
    messages_bits = np.array(messages_bits, dtype=float)
    return messages_bits


def pack_to_dec(messages):
    """This function converts an array of binary numbers into their decimal
    representation.

    Parameters
    ----------
    messages : array (N x num_bits)
        Array where each row contains one number and each column one bit

    Returns
    -------
    dec_messages : array (N x 1)
        Converted messages as decimal numbers
    """
    _powers = np.arange(np.shape(messages)[1], 0, -1) - 1
    coeff = np.power(2, _powers).reshape((-1, 1))
    return np.dot(messages, coeff).astype(int)


def generate_data(info_length, number=None, binary=False):
    """Generate random messages.

    Parameters
    ----------
    info_length : int
        Number of information bits (message length)

    number : int, optional
        Number of random messages to generate (if int given) or all possible
        messages (if None given)

    binary : bool, optional
        If True, the messages will be returned in binary representation

    Returns
    -------
    messages : array
        Array of generated messages. Shape is (number, info_bits) if unpacked,
        (numer, 1) else.
    """
    info_length = int(info_length)
    if number is None:
        number = 2**info_length
        messages = np.arange(number)
    else:
        number = int(number)
        messages = np.random.randint(2**info_length, size=number)

    if binary:
        messages = unpack_to_bits(messages, info_length)
    return messages


def _generate_data_generator(batch_size=50000, number=None, seed=None, **kwargs):
    """Generator for random messages."""
    if seed is None:
        seed = _SEED
    np.random.seed(seed)
    if number is None:
        yield generate_data(number=None, **kwargs)
    else:
        size = int(number)
        batch_size = int(batch_size)
        num_batches, last_batch = divmod(size, batch_size)
        for batch in range(num_batches):
            yield generate_data(number=batch_size, **kwargs)
        if last_batch:
            yield generate_data(number=last_batch, **kwargs)
