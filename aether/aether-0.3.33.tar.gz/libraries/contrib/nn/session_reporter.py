from __future__ import absolute_import
import numpy as np

import logging
import six
logger = logging.getLogger(__name__)


class session_reporter():

    def __init__(self, session_name):
        self._session_name = session_name
        self._batch_statuses = {}
        self._epoch_statuses = {}

    # At the end of a batch, this is called to add the summaries (key-value pairs in summaries)
    def batch_report_add(self, epoch, batch, batch_index, total_batches, summaries, time):
        status = { "epoch": epoch, "batch": batch, "ref_to_data": batch_index, "time": time, "summaries": summaries}
        if epoch not in self._batch_statuses:
            self._batch_statuses[epoch] = {}
        self._batch_statuses[epoch][batch] = status

        logger.info("epoch {}, batch {} (number {}) of {}, time/batch = {}, summaries = {}"
                    .format(epoch, batch_index, batch, total_batches, time, summaries))

    # A generated report created at the end of each epoch.
    def epoch_report(self, epoch):
        if epoch not in self._batch_statuses:
            return

        statuses = self._batch_statuses[epoch]
        summaries = [x["summaries"] for x in statuses.values()]
        times = [x["time"] for x in statuses.values()]

        epoch_status = {"epoch": epoch, "total_batches": len(statuses),
                        "time_mean": np.mean(times), "time_std": np.std(times)}

        epoch_string = "epoch {}, total batches {}, time/batch = {} +/- {}".format(
            epoch, len(statuses), epoch_status["time_mean"], epoch_status["time_std"])

        if len(summaries) > 0:
            metrics = list(sorted(summaries[0].keys()))
            for metric in metrics:
                values = [s[metric] for s in summaries]
                epoch_status["{}_mean".format(metric)] = np.mean(values)
                epoch_status["{}_std".format(metric)] = np.std(values)
                epoch_string += ", {} = {} +/- {}".format(metric, epoch_status["{}_mean".format(metric)], epoch_status["{}_std".format(metric)])
        self._epoch_statuses[epoch] = epoch_status

        logger.info("***** {} Epoch Stats: *****".format(self._session_name))
        logger.info(epoch_string)
        logger.info("*************************************")

    def save_report(self, status_save_directory):
        # Record all the batches within epochs
        filename = status_save_directory + "tf.batch.status.txt"
        logger.info("Reporting batches within epoches; saving to : {}".format(filename))
        with open(filename, 'w') as f:
            text = ""
            ordered_epochs = list(sorted(self._batch_statuses.keys()))
            for epoch in ordered_epochs:
                ordered_batches = list(sorted(self._batch_statuses.keys()))
                for batch in ordered_batches:
                    text += "\t".join(["{}:{}".format(key, value) for key, value in six.iteritems(self._batch_statuses[epoch][batch])])
                    text += "\n"
            f.write('%s' % text)

        # Record the epoch summaries themselves.
        filename = status_save_directory + "tf.epoch.status.txt"
        logger.info("Reporting epoches; saving to : {}".format(filename))
        with open(status_save_directory + "tf.epoch.status.txt", 'w') as f:
            text = ""
            ordered_epochs = list(sorted(self._epoch_statuses.keys()))
            for epoch in ordered_epochs:
                text += "\t".join(["{}:{}".format(key, value) for key, value in six.iteritems(self._epoch_statuses[epoch])])
                text += "\n"
            f.write('%s' % text)
