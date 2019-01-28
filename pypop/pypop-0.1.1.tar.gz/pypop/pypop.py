from pychord import Chord, ChordProgression

from pypop.song import ChordTrack, ChordEvent, Time, Song


def compose():
    """ Compose a pop song

    This is currently a mock-up code.
    """
    chords = [Chord("C"), Chord("F"), Chord("G"), Chord("C")]
    chord_track = ChordTrack()
    for i, chord in enumerate(chords):
        event = ChordEvent(time_=Time(measure=i + 1), duration=Time(measure=1), chord=chord)
        chord_track.append(event)
    song = Song(chord_track=chord_track)
    return song
