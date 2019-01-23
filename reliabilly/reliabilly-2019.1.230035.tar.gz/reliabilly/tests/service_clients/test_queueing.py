import base64
from reliabilly.tests import MagicMock, TestCase, logging, warnings, json, skipUnless
from reliabilly.components.factories.factory import Factory, Components
from reliabilly.components.services.queuing import SqsReceiver, QueueMessage
from reliabilly.settings import Settings, Constants

TEST = 'test'
DUMMY = 'dummy'
TEST_CONTENT = {'content': TEST}
TEST_MESSAGE = QueueMessage(**TEST_CONTENT)
ENCODED_TEST_MESSAGE = 'eyJtZXNzYWdlIjogeyJjb250ZW50IjogInRlc3QifSwgImlkIjogInRlc3QifQ=='
MOCK_RESPONSE = {Constants.MESSAGES_KEY: [{Constants.BODY_KEY: ENCODED_TEST_MESSAGE,
                                           Constants.RECEIPT_HANDLE_KEY: '123'}]}
DUMMY_MESSAGE = {'content': DUMMY}
ENCODED_DUMMY_MESSAGE = base64.b64encode(json.dumps(DUMMY_MESSAGE).encode())
LOCAL_SQS = 'http://localhost:9324'


class QueueingTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings(Constants.IGNORE, category=ResourceWarning)

    def test_full_queue(self):
        mock = MagicMock()
        mock.create_queue.return_value = mock
        mock.get_queue_by_name.return_value = mock
        mock.receive_message.return_value = MOCK_RESPONSE
        client = Factory.create(Components.ServiceClients.SQS, queue_name=DUMMY, client=mock)
        self.assertIsNotNone(client)
        self.assertTrue(client.send_message(TEST_MESSAGE))
        mock.send_message.assert_called()
        message = client.receive_message()
        self.assertTrue(message)
        self.assertTrue(client.complete_message(message))
        mock.send_message.side_effect = Exception
        self.assertFalse(client.send_message(TEST_MESSAGE))
        mock.receive_message.side_effect = Exception
        self.assertFalse(client.receive_message())
        mock.delete_message.side_effect = Exception
        self.assertFalse(client.complete_message(message))

    def test_purge(self):
        mock = MagicMock()
        client = Factory.create(Components.ServiceClients.SQS, queue_name=DUMMY, client=mock)
        self.assertTrue(client.purge())
        mock.purge_queue.side_effect = Exception
        self.assertFalse(client.purge())

    def test_create_queue(self):
        mock = MagicMock()
        mock.get_queue_by_name.side_effect = Exception
        client = Factory.create(Components.ServiceClients.SQS, queue_name=DUMMY, client=mock)
        self.assertTrue(client.create_queue(DUMMY))
        mock.create_queue.side_effect = Exception
        self.assertFalse(client.create_queue(DUMMY))


class QueueReceiverTests(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings(Constants.IGNORE, category=ResourceWarning)

    def test_setup(self):
        mock = MagicMock()
        queue = SqsReceiver(DUMMY, client=mock)
        queue.setup()
        self.assertIsNotNone(queue.client)
        mock.create_queue.assert_called()

    def test_run(self):
        mock = MagicMock()
        queue = SqsReceiver(DUMMY, client=mock)
        queue.exit = True
        self.assertTrue(queue.run(mock))
        self.assertTrue(queue.run())
        queue.container = mock
        queue.start()


class TestQueueMessage(TestCase):
    def test_message_encoding(self):
        message = TEST_MESSAGE
        self.assertIsNotNone(message.body)
        self.assertEqual(len(message.body), 100)  # the encoded length in bytes will always include the changing id

    def test_message_decoding(self):
        message = QueueMessage.create_from_encoded(ENCODED_TEST_MESSAGE)
        self.assertIsNotNone(TEST_MESSAGE.message_id, message.message_id)
        self.assertEqual(TEST_CONTENT, message.message)

    def test_message_construction(self):
        message = QueueMessage(test=2, test2='test', message_id='123')
        self.assertEqual(str(message), "{'test': 2, 'test2': 'test', 'message_id': '123'}")


@skipUnless(Settings.RUN_SKIPPED, Constants.RUN_SKIPPED_MSG)
class TestRealQueue(TestCase):
    def setUp(self):
        logging.disable(logging.CRITICAL)
        warnings.filterwarnings(Constants.IGNORE, category=ResourceWarning)

    def test_queue_lost_message(self):
        client = Factory.create(Components.ServiceClients.SQS, queue_name='test', endpoint_url=LOCAL_SQS)
        message = QueueMessage()
        message.product = "site.reliability"
        message.account_name = "reliabilly_ps"
        message.portfolio = "Platform Services"
        message.threshold = "5"
        message.slo_type = "error_rate"
        message.component = "reliabillyecs_cluster"
        message.query = "SELECT sum(`provider.httpCodeTarget5XXCount.Sum`) from LoadBalancerSample where " \
                        "`label.serverclass` like 'lighthouse' and `provider.awsRegion` = 'us-west-2'"
        message.query_executor = "newrelic"
        message.id = "0000000-ae7a-4896-a957-9b736128eaf3"
        message.name = "lighthouse-error_rate-uat"
        client.send_message(message)
        received_message = client.receive_message()
        self.assertEqual(message.message_id, received_message.message_id)
        client.complete_message(received_message)

    def test_actual_sqs(self):
        client = Factory.create(Components.ServiceClients.SQS, queue_name='test')
        model = QueueMessage()
        model.message = 'This is a test ___'
        model.name = 'ODB'
        model.value = 420
        self.assertTrue(client.send_message(model))
        message = client.receive_message()
        self.assertEqual(message.name, model.name)
        client.complete_message(message)

    def test_actual_queue_message(self):
        client = Factory.create(Components.ServiceClients.SQS, queue_name='qm-queue')
        self.assertTrue(client.send_message(QueueMessage(**DUMMY_MESSAGE)))
        message = client.receive_message()
        self.assertIsNotNone(message)
        client.complete_message(message)
