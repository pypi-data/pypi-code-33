class Key:
    def __init__(self, primitive, native=None, is_required=True):
        self.primitive = primitive
        self.native = primitive if native is None else native
        self.is_required = is_required
