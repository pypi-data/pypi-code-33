import click
import enum


class Note(enum.Enum):
    A = 0
    ASharp = 1
    B = 2
    C = 3
    CSharp = 4
    D = 5
    DSharp = 6
    E = 7
    F = 8
    FSharp = 9
    G = 10
    GSharp = 11


class ChordType(enum.Enum):
    Major = [4, 7]
    Major7 = [4, 7, 11]
    Minor = [3, 7]
    Minor7 = [3, 7, 10]
    Sus2 = [2, 7]
    Sus4 = [5, 7]


class Instrument(enum.Enum):
    Guitar = [Note.E, Note.A, Note.D, Note.G, Note.B, Note.E]
    UkeBar = [Note.D, Note.G, Note.B, Note.E]
    Ukulele = [Note.G, Note.C, Note.E, Note.A]


def buildChord(note, chordType):
    chord = []

    chord.append(note)

    for interval in chordType.value:
        chord.append(Note((note.value + interval) % 12))

    return chord


def genTab(chord, instrument):
    tab = []

    for string in instrument.value:
        if (string not in chord):
            nearest = 1000

            for note in chord:
                noteValue = note.value

                if (noteValue < string.value):
                    noteValue = noteValue + 12

                difference = abs(noteValue - string.value)

                if (difference < nearest):
                    nearest = difference

            tab.append(nearest)

        else:
            tab.append(0)

    return tab


def notesInTab(tab, instrument):
    notes = []

    for index, diff in enumerate(tab):
        notes.append(Note((instrument.value[index].value + diff) % 12))

    return notes


noteNames = [name for name, member in Note.__members__.items()]
chordNames = [name for name, member in ChordType.__members__.items()]
instrumentNames = [name for name, member in Instrument.__members__.items()]


@click.command()
@click.option('--root', '-r', type=click.Choice(noteNames), prompt="Root note",
              help='The root note of the chord.')
@click.option(
    '--chord', '-c',
    type=click.Choice(chordNames), prompt="Chord Type",
    help='Which chord to calculate.')
@click.option(
    '--instrument', '-i',
    type=click.Choice(instrumentNames), prompt="Instrument",
    help='The instrument to calculate the chord for.')
def cli(root, chord, instrument):
    root = Note[root]
    chordType = ChordType[chord]
    instrument = Instrument[instrument]

    chord = buildChord(root, chordType)
    tab = genTab(chord, instrument)

    click.echo("Chord:")
    click.echo([name.name for name in chord])
    click.echo("Chart:")
    click.echo(tab)
    click.echo("Notes in chart:")
    click.echo([note.name for note in notesInTab(tab, instrument)])
