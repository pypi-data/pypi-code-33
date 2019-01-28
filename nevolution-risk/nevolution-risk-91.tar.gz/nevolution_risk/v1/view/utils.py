from nevolution_risk.constants.view_settings import coordinates, radius


def find_node(position):
    for n in range(1, 11):
        if is_inside(coordinates[n], position):
            return n
    return 0


def is_inside(pos1, pos2):
    square = (pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + (pos1[1] - pos2[1]) * (pos1[1] - pos2[1])
    if square < radius * radius:
        return True
    else:
        return False
