import uuid
import pyspark.ml import PipelineModel

def predict(spark, inputDF, modelLoc, outputDir= uuid.uuid4(), baseDir='predictions',
            workDir='output',
            outputFormt='parquet',
            pipeline=True, persist=True):
    _dirName = '{}/{}'.format(baseDir, outputDir)
    _localPath = '{}/{}-{}'.format(workDir, outputDir, "prediction.csv")

    predictDF = None

    if pipeline:
        model = PipelineModel.load(modelLoc)
        predictDF = model.transform(inputDF)
        predictDF.show()

    if persist and predictDF != None:
        if outputFormt == 'parquet':
            predictDF.write.parquet(_dirName)
        elif outputFormt == 'csv':
            predictDF.toPandas().to_csv(_localPath)
        elif outputFormt == 'libsvm':
            print("Libsvm not yet supported - writing in parquet format.")
            predictDF.write.parquet(_dirName)

