from typing import List

from attr import attrs, attrib
from pychord import Chord


@attrs
class Time:
    measure = attrib(type=int)
    beat = attrib(type=int, default=0)
    tick = attrib(type=int, default=0)

    def __str__(self):
        return f"{self.measure}:{self.beat}:{self.tick}"

    def as_seconds(self, tempo, timebase, beat):
        return (self.tick / timebase + self.beat + self.measure * beat) / tempo * 60


class ChordEvent:
    def __init__(self, time_: Time, duration: Time, chord: Chord):
        self.time = time_
        self.duration = duration
        self.chord = chord


class ChordTrack:
    def __init__(self):
        self.chords: List[ChordEvent] = []

    def append(self, chord: ChordEvent):
        self.chords.append(chord)


class Song:
    def __init__(self, tempo=120, timebase=240, beat=4, chord_track=None):
        if chord_track is None:
            chord_track = ChordTrack()
        self.tempo = tempo
        self.timebase = timebase
        self.beat = beat
        self.chord_track: ChordTrack = chord_track
