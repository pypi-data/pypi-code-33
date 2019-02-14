def extract_groups(groups):
    if groups and groups != "":
        return list(map(str.strip, groups.split(',')))
    return []
