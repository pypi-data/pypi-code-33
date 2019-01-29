"""A script renames the movie file, tags it with genres, and moves
to the folder with the director’s name."""
import subprocess as sp
from argparse import ArgumentParser
from itertools import islice
from pathlib import Path

import isle


try:
    TAG = sp.check_output(["which", "tag"]).decode("utf-8").strip()
except sp.CalledProcessError:
    raise RuntimeError(
        (
            "The script requires jdberry's tag command"
            "line tool.\nSee: 'https://github.com/jdberry/tag'"
        )
    )

FORMAT = "{year} - {first_title}{second_title}"
YES_OR_NO = "(y/n, default y)"
STYLE = {
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "darkcyan": "\033[36m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "underline": "\033[4m",
    "end": "\033[0m",
}


def stylized(style, string):
    return f"{STYLE[style]}{string}{STYLE['end']}"


def add_tag_to(path, *, tag):
    sp.run([TAG, "-a", tag, str(path)])


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("path", type=str, help="the path to a movie file")
    parser.add_argument("-n", type=int, default=5, help="number of search results")
    return vars(parser.parse_args())


def ask_title():
    return input(f"\n{stylized('bold', 'Title:')} ")


def ask_year():
    return input(f"{stylized('bold', 'Year:')} ")


def _y_or_n(ask):
    while True:
        ans = input(f"\n{stylized('bold', ask)} ") or "y"
        if ans in ("y", "n"):
            return True if ans == "y" else False

def ask_rename():
    return _y_or_n("Needs to be renamed (y/n, default y):")


def ask_genres():
    return _y_or_n("Add genres (y/n, default y):")


def ask_move():
    return _y_or_n("Move to the folder with the director’s name (y/n, default y):")


def print_movies(movies):
    print(f"\n{stylized('bold', 'SEARCH RESULTS 🔎')}\n")
    for i, movie in enumerate(movies, 1):
        print(f"{i}. {movie.year or '----'} - {movie.title['original']}")


def ask_movie(movies):
    ask = 'Choose a movie (1 is by default):'
    while True:
        i = int(input(f"\n{stylized('bold', ask)} ") or "1")
        if i in range(1, len(movies) + 1):
            break
    return movies[i - 1]


def assemble_name(movie):
    frst_title = movie.title["original"]
    scnd_title = get_second_title(movie)
    name = FORMAT.format(
        year=movie.year, first_title=frst_title, second_title=scnd_title
    )
    return name


def get_second_title(movie):
    title = movie.title.get("US", movie.title["default"])
    if not title or title.lower() == movie.title["original"].lower():
        return ""
    else:
        return f" ({title})"


def get_directors_names(movie):
    names = (p.name for p, c in movie.crew if c.job == "Director")
    names = (", ".join(reversed(name.rsplit(maxsplit=1))) for name in names)
    return "; ".join(sorted(names))


def print_done():
    print(f"\n{stylized('bold', 'All done!')} 👍")


def main():
    args = parse_args()
    path, n = Path(args["path"]), args["n"]

    title = ask_title()
    year = ask_year()

    rename = ask_rename()
    genres = ask_genres()
    move = ask_move()

    movies = list(islice(isle.search_movie(title, year=year), n))
    print_movies(movies)
    movie = ask_movie(movies)

    if rename:
        name = assemble_name(movie) + path.suffix
        new_path = path.parent / name
        path.rename(new_path)
        path = new_path

    if genres:
        add_tag_to(path, tag="Movie")
        for genre in map(str, movie.genres):
            add_tag_to(path, tag=genre)

    if move:
        dirname = get_directors_names(movie)
        folder = path.parent / dirname
        folder.mkdir(exist_ok=True)
        new_path = folder / f"{path.name}"
        path.rename(new_path)

    print_done()

if __name__ == "__main__":
    main()