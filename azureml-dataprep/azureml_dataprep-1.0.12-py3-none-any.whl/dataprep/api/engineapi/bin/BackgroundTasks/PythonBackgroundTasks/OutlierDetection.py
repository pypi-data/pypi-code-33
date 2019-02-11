def run_outlier_detection(df, args):

    numericColumns = args.columnIds
    outlierColumnIds = []
    df = df.apply(pandas.to_numeric, errors='coerce')
    for columnId in numericColumns:
        column = df[columnId]
        mean = column.mean()
        std = column.std()
        for cell in column:
            if pandas.DataFrame.abs(cell-mean) > (3*std):
               outlierColumnIds.append(columnId)
               break
    index = numpy.arange(1)
    return pandas.DataFrame(columns=outlierColumnIds, index = index)