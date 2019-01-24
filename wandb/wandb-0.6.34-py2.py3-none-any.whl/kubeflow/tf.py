import os
os.environ["S3_ENDPOINT"] = "localhost:9000"
os.environ["AWS_DEFAULT_PROFILE"] = "wandb"
os.environ["S3_USE_HTTPS"] = "0"

import tensorflow as tf

fw = tf.summary.FileWriter("s3://wandb-production_cloudbuild/proxy")
summary = tf.Summary(value=[
    tf.Summary.Value(tag="rad", simple_value=185),
])
fw.add_summary(summary)
fw.close()
