#!/usr/bin/env python
import re
import sys

# the use of the dependencies minimized to reuse this script as a standalone helper

DEBYE_TO_AU = 0.393456
PROPERTY_LINE_PATTERN = re.compile(r"\s*Property number\s+(\d).*(\d+\.\d+):.*")
NDIGITS = 1
POLAR_IDX = 1
BETA_2WWW = 6
STATIC_LIMIT = "static"
HYPER_W = "hyper_w"
POLAR_2W = "polar_2w"
POLAR_W = "polar_w"


def _redo_D_to_E(inp: str) -> float:
    return float('E'.join(inp.split('D')))


def _round_half(x):
    return round(x * 2) / 2


def _ha_to_nm(en_ha: str) -> str:
    if abs(float(en_ha)) < 1e-5:
        return STATIC_LIMIT
    return str(_round_half(45.5636721 / float(en_ha)))


def _get_2w_key(key):
    if key == STATIC_LIMIT:
        return STATIC_LIMIT
    return str(_round_half(float(key) / 2))


def transform_g09_to_input(file, charged=False, file_out=None):
    with open(file) as f:
        lines = f.readlines()[-3000:]

    dipole = []
    if charged:
        dipole = [0., 0., 0.]
    else:
        for i in range(len(lines)):
            if lines[i].find('Dipole mom') > -1:
                line = lines[i + 1].split()
                dipole.extend([float(line[i]) * DEBYE_TO_AU for i in (1, 3, 5)])
                break

    polars = {}
    hypers = {}

    current_line = 0
    previous_prop_idx = 0
    while current_line < len(lines):
        if lines[current_line].find("Property number") > -1:
            match = PROPERTY_LINE_PATTERN.match(lines[current_line])
            if match is None:
                print(f"line not matched: {lines[current_line]}")
                raise AssertionError("check the PROPERTY_LINE_PATTERN as no match found...")
            prop_idx = int(match.group(1))
            wave_length = _ha_to_nm(match.group(2))
            if prop_idx < previous_prop_idx:
                # print("broken!")
                break  # inverted, properties repeated in the output file
            previous_prop_idx = prop_idx
            if prop_idx == POLAR_IDX:
                current_line += 2
                polar = [[0. for i in range(3)] for j in range(3)]
                for i in range(3):
                    tokens = lines[current_line].split()[1:4]
                    for j in range(3):
                        polar[i][j] = _redo_D_to_E(tokens[j])
                    current_line += 1
                polars[wave_length] = polar
                current_line -= 1
            elif prop_idx == BETA_2WWW:
                current_line += 2
                beta = [[[0. for i in range(3)] for j in range(3)] for k in range(3)]
                for ijk in ((0, 0, 0),
                            (0, 0, 1),
                            (0, 1, 1),
                            (0, 2, 0),
                            (0, 2, 1),
                            (0, 2, 2),
                            (1, 0, 0),
                            (1, 1, 0),
                            (1, 1, 1),
                            (1, 2, 0),
                            (1, 2, 1),
                            (1, 2, 2),
                            (2, 0, 0),
                            (2, 1, 0),
                            (2, 1, 1),
                            (2, 2, 0),
                            (2, 2, 1),
                            (2, 2, 2)):
                    beta[ijk[0]][ijk[1]][ijk[2]] = - _redo_D_to_E(lines[current_line].split()[1])
                    current_line += 1
                current_line -= 1
                for ijk in ((0, 0, 1),
                            (0, 2, 0),
                            (0, 2, 1),
                            (1, 1, 0),
                            (1, 2, 0),
                            (1, 2, 1),
                            (2, 1, 0),
                            (2, 2, 0),
                            (2, 2, 1)):
                    beta[ijk[0]][ijk[2]][ijk[1]] = beta[ijk[0]][ijk[1]][ijk[2]]
                hypers[wave_length] = beta
        current_line += 1

    raw_properties = {}
    polars_pm5_keys = _get_pm5_keys(polars.keys())
    keys = [key for key in hypers.keys() if key in polars.keys() and _get_2w_key(key) in polars_pm5_keys.keys()]
    raw_properties[STATIC_LIMIT] = {}
    raw_properties[STATIC_LIMIT][POLAR_W] = polars.get(STATIC_LIMIT)
    raw_properties[STATIC_LIMIT][POLAR_2W] = polars.get(STATIC_LIMIT)
    raw_properties[STATIC_LIMIT][HYPER_W] = hypers.get(STATIC_LIMIT)
    for key in keys:
        key2 = polars_pm5_keys.get(_get_2w_key(polars_pm5_keys.get(key)))
        raw_properties[key] = {}
        raw_properties[key][POLAR_W] = polars.get(key)
        raw_properties[key][POLAR_2W] = polars.get(key2)
        raw_properties[key][HYPER_W] = hypers.get(key)

    lines_out = [" ".join(str(u) for u in dipole[:])]
    lines_out.append(STATIC_LIMIT)
    _add_polar_lines(raw_properties[STATIC_LIMIT][POLAR_W], lines_out)
    _add_hyper_lines(raw_properties[STATIC_LIMIT][HYPER_W], lines_out)
    for key in keys:
        lines_out.append(key)
        _add_polar_lines(raw_properties[key][POLAR_W], lines_out)
        _add_polar_lines(raw_properties[key][POLAR_2W], lines_out)
        _add_hyper_lines(raw_properties[key][HYPER_W], lines_out)

    if file_out is not None:
        with open(file_out, 'w') as f:
            f.write("\n".join(lines_out))
    else:
        return dipole, raw_properties


def _add_polar_lines(polar_w, lines_out):
    for i in range(3):
        line = ""
        for j in range(3):
            line += str(polar_w[i][j]) + " "
        lines_out.append(line)
    lines_out.append("")


def _add_hyper_lines(hyper_w, lines_out):
    for i in range(3):
        for j in range(3):
            line = ""
            for k in range(3):
                line += str(hyper_w[i][j][k]) + " "
            lines_out.append(line)
    lines_out.append("")


def _get_pm5_keys(keys):
    key_mapping = {}
    for key in keys:
        if key == STATIC_LIMIT:
            continue
        key_mapping[str(float(key) + .5)] = key
        key_mapping[key] = key
        key_mapping[str(float(key) - .5)] = key
    return key_mapping


if __name__ == "__main__":
    if len(sys.argv) > 2:
        transform_g09_to_input(file=sys.argv[1], charged=bool(sys.argv[2]), file_out="tmp")
    else:
        transform_g09_to_input(file=sys.argv[1], file_out="tmp")
