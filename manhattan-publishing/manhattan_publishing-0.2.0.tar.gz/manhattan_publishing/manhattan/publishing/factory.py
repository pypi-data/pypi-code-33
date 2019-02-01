
from manhattan.comparable.factory import Blueprint as BaseBlueprint

from .frames import PublishableFrame

__all__ = ['Blueprint']


class Blueprint(BaseBlueprint):
    """
    A factory blueprint for create fixture data for publishable frames.
    """

    _frame_cls = PublishableFrame

    @classmethod
    def on_fake(cls, frames):
        """Called before frames are inserted"""
        super().on_fake(frames)

        # Set a check sum for every frame
        for frame in frames:
            frame.last_checksum = frame.get_checksum()

    @classmethod
    def on_faked(cls, frames):
        """Called after frames are inserted"""
        super().on_faked(frames)

        # Publish every frame
        for frame in frames:
            frame.publish(None)
