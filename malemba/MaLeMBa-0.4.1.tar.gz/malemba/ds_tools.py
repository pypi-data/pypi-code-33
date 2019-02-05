class ArrayHandler(object):

    def __init__(self, group_lims=None):
        self.group_lims = group_lims

    def aggregate(self, array, aggr_level):
        if aggr_level < 1:
            for elm in array:
                yield elm
        if self.group_lims is None:
            self.group_lims = [list() for k in range(aggr_level)]
            i = -1
        else:
            try:
                i = self.group_lims[aggr_level - 1][-1]
            except IndexError:
                i = -1
        if aggr_level == 1:
            for array_elm in array:
                for elm in array_elm:
                    yield elm
                i += len(array_elm)
                self.group_lims[0].append(i)
        else:
            for array_elm in array:
                for elm in self.aggregate(array=array_elm, aggr_level=aggr_level-1):
                    yield elm
                i += len(array_elm)
                self.group_lims[aggr_level-1].append(i)


def group_array(aggr_array, group_lims):
    if len(group_lims) == 1:
        return _group_level(aggr_array, group_lims.pop(0))
    aggr_array = _group_level(aggr_array, group_lims.pop(0))
    return group_array(aggr_array, group_lims)


def _group_level(aggr_array, level_lims):
    grouped_array = [list()]
    for i in range(len(aggr_array)):
        grouped_array[-1].append(aggr_array[i])
        if i == level_lims[0]:
            level_lims.pop(0)
            grouped_array.append(list())
    return list(filter(None, grouped_array))
