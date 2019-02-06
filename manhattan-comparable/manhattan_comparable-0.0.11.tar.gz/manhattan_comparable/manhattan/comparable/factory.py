
from mongoframes.factory.blueprints import Blueprint as BaseBlueprint

from .frames import ComparableFrame

__all__ = ['Blueprint']


class Blueprint(BaseBlueprint):
    """
    A factory blueprint for create fixture data for comparable frames.
    """

    _frame_cls = ComparableFrame

    @classmethod
    def on_fake(cls, frames):
        """Called before frames are inserted"""

        # Timestamp
        for frame in frames:
            cls._frame_cls.timestamp_insert(frame, [frame])

        super().on_fake(frames)

    @classmethod
    def on_faked(cls, frames):
        """Called after frames are inserted"""

        # Add change log entries
        for frame in frames:
            entry = cls._frame_cls._change_log_cls({
                'type': 'ADDED',
                'documents': [frame],
                'user': None
                })
            entry.insert()

        super().on_faked(frames)
