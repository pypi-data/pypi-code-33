import warcprox
import time
import logging

class SlowItDownEarly(warcprox.BaseStandardPostfetchProcessor):
    CHAIN_POSITION = 'early'
    def _process_url(self, recorded_url):
        time.sleep(0.5)
        logging.info('processed %s', recorded_url.url)

class SlowItDownLate(warcprox.BaseStandardPostfetchProcessor):
    CHAIN_POSITION = 'late'
    def _process_url(self, recorded_url):
        time.sleep(0.5)
        logging.info('processed %s', recorded_url.url)
