import numpy as np


class session_reporter():

    def __init__(self, session_name):
        self._session_name = session_name
        self._batch_statuses = [[]]
        self._epoch_statuses = []
        self._evaluation_statuses = []

    # Index by epoch
    def batch_report(self, epoch, batch, batch_index, total_batches, loss, time):
        status = { "epoch": epoch, "batch": batch, "loss": loss, "time": time}
        if (len(self._batch_statuses) == epoch): self._batch_statuses.append([])
        self._batch_statuses[epoch].append(status)

        print("epoch {}, batch {} (number {}) of {}, train_loss = {}, time/batch = {}"
              .format(epoch, batch_index, batch, total_batches, loss, time))

    def batch_report_add(self, epoch, batch, batch_index, total_batches, dict, time):
        status = { "epoch": epoch, "batch": batch, "time": time, "dict": dict}
        if (len(self._batch_statuses) == epoch): self._batch_statuses.append([])
        self._batch_statuses[epoch].append(status)

        print("epoch {}, batch {} (number {}) of {}, time/batch = {}, dict = {}"
              .format(epoch, batch_index, batch, total_batches, time, dict))

    def epoch_report(self, epoch):
        statuses = self._batch_statuses[epoch]
        dicts = [x["dict"] for x in statuses]
        times = [x["time"] for x in statuses]

        epoch_status = {"epoch": epoch, "total_batches": len(statuses),
                        "time_mean": np.mean(times), "time_std": np.std(times)}

        epoch_string = "epoch {}, total batches {}, time/batch = {} +/- {}".format(
            epoch, len(statuses), epoch_status["time_mean"], epoch_status["time_std"])

        if len(dicts) > 0:
            for k, v in dicts[0].items():
                vs = [dicts[i][k] for i in range(0, len(dicts))]
                epoch_status["{}_mean".format(k)] = np.mean(vs)
                epoch_status["{}_std".format(k)] = np.std(vs)
                epoch_string += ", {} = {} +/- {}".format(k, epoch_status["{}_mean".format(k)], epoch_status["{}_std".format(k)])
        self._epoch_statuses.append(epoch_status)

        print("***** {} Epoch Stats: *****").format(self._session_name)
        print(epoch_string)
        print("************************")

    def evaluation_report_add(self, epoch, number_of_evaluations, accuracy):
        self._evaluation_statuses.append({
            "number_of_evaluations": number_of_evaluations,
            "accuracy": accuracy,
            "epoch": epoch
        })

        evaluation_status = self._evaluation_statuses[-1]
        print("***** {} Evaluation Stats: *****").format(self._session_name)
        print("epoch {}, number of evaluations {}, accuracy {}"
              .format(evaluation_status["epoch"], evaluation_status["number_of_evaluations"], evaluation_status["accuracy"])
              )
        print("************************")

    def epoch_style_report(self, status_save_directory, filename, dictionary_list):
        with open(status_save_directory + filename, 'w') as f:
            text = ""
            for s in dictionary_list:
                for k, v in s.items():
                    text += "{}:{}\t".format(k, v)
                text += "\n"
            f.write('%s' % text)

    def save_report(self, status_save_directory):
        with open(status_save_directory + "tf.batch.status.txt", 'w') as f:
            text = ""
            for b in self._batch_statuses:
                for s in b:
                    for k, v in s.items():
                        text += "{}:{}\t".format(k, v)
                text += "\n"
            f.write('%s' % text)
        self.epoch_style_report(status_save_directory, "tf.epoch.status.txt", self._epoch_statuses)

        # print("Report status saved to directory: {}".format(status_save_directory))
