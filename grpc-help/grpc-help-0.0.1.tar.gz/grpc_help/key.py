def read_private_key(private_key_path):
    with open(private_key_path, 'rb') as f:
        private_key = f.read()
    return private_key


def read_public_key(public_key_path):
    with open(public_key_path, 'rb') as f:
        certificate_chain = f.read()
    return certificate_chain

