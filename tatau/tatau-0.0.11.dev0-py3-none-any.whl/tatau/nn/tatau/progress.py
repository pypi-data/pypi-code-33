from logging import getLogger

logger = getLogger(__name__)


# noinspection PyMethodMayBeStatic
class TrainProgress:

    def on_epoch_start(self, epoch):
        logger.info('Progress: start epoch #{}'.format(epoch))

    def on_epoch_end(self, epoch, accuracy, loss, epoch_time, *args, **kwargs):
        logger.info('Progress: end epoch #{}, acc: {}, loss: {}, epoch time: {}'.format(
            epoch, accuracy, loss, epoch_time))
