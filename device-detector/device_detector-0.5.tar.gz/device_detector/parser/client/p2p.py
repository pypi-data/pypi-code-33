from . import BaseClientParser


class P2P(BaseClientParser):

    fixture_files = [
        'local/client/p2p.yml',
    ]

    def dtype(self):
        return 'p2p'



__all__ = (
    'P2P',
)
