import time

from pypop.song import Song


class Player:
    def __init__(self):
        pass

    def play(self, song: Song):
        for event in song.chord_track.chords:
            print(f"{event.time} {event.chord}")
            time.sleep(event.duration.as_seconds(tempo=song.tempo, timebase=song.timebase, beat=song.beat))
