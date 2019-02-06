from messaging_middleware.avro_communication_layer.Consumer import Consumer as AvroConsumer


if __name__ == "__main__":
    c = AvroConsumer(
        bootstrap_servers="edc2kafkabk1.eu.trendnet.org:9093,edc2kafkabk2.eu.trendnet.org:9093,edc2kafkabk3.eu.trendnet.org:9093,edc2kafkabk4.eu.trendnet.org:9093,edc2kafkabk5.eu.trendnet.org:9093",
        security_protocoll='ssl', consumer_topic='tc-vapps-available')
