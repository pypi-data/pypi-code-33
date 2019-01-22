from nevolution_risk.constants.view_settings import radius


def is_inside(pos1, pos2):
    square = (pos1[0] - pos2[0]) * (pos1[0] - pos2[0]) + (pos1[1] - pos2[1]) * (pos1[1] - pos2[1])
    if square < radius * radius:
        return True
    else:
        return False
