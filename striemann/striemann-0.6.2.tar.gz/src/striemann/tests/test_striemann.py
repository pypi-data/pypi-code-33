from expects import expect
from icdiff_expects import equal
from unittest import mock
import striemann.metrics


class Test:
    def test_gauges(self):
        transport = striemann.metrics.InMemoryTransport()
        metrics = striemann.metrics.Metrics(transport, source="test")
        metrics.recordGauge("service_name", 2.0, tags=["spam"], ham="eggs")
        metrics.recordGauge("service_name", 4.0, tags=["spam"], ham="eggs")
        metrics.incrementCounter("service_name", value=5, tags=["foo"], bar="baz")
        metrics.flush()
        expect(transport.last_batch).to(
            equal(
                [
                    {
                        "attributes": {"ham": "eggs", "source": "test"},
                        "metric_f": 4.0,
                        "service": "service_name",
                        "tags": ["spam"],
                    },
                    {
                        "attributes": {"bar": "baz", "source": "test"},
                        "metric_f": 5,
                        "service": "service_name",
                        "tags": ["foo"],
                    },
                ]
            )
        )

    def test_ttl(self):
        transport = striemann.metrics.InMemoryTransport()
        metrics = striemann.metrics.Metrics(transport)

        metrics.incrementCounter("heartbeat", ttl=7)
        metrics.flush()

        expect(transport.last_batch).to(
            equal(
                [
                    {
                        "service": "heartbeat",
                        "ttl": 7.0,
                        "metric_f": 1,
                        "tags": [],
                        "attributes": {},
                    }
                ]
            )
        )

    @mock.patch("timeit.default_timer", side_effect=[0, 1, 0, 3])
    def test_timers(self, timer):

        transport = striemann.metrics.InMemoryTransport()
        metrics = striemann.metrics.Metrics(transport)

        with metrics.time("time"):
            pass

        with metrics.time("time"):
            pass

        metrics.flush()

        expect(transport.last_batch[0]).to(
            equal({"service": "time.min", "metric_f": 1, "tags": [], "attributes": {}})
        )
        expect(transport.last_batch[1]).to(
            equal({"service": "time.max", "metric_f": 3, "tags": [], "attributes": {}})
        )
        expect(transport.last_batch[2]).to(
            equal({"service": "time.mean", "metric_f": 2, "tags": [], "attributes": {}})
        )
        expect(transport.last_batch[3]).to(
            equal(
                {"service": "time.count", "metric_f": 2, "tags": [], "attributes": {}}
            )
        )


class FakeRiemannClientTransport:
    def __init__(self, log, send=lambda msg: None):
        self.log = log
        self._send = send

    def send(self, msg):
        self.log.append("try to send")
        self._send(msg)
        self.log.append("sent")

    def connect(self):
        self.log.append("connected")

    def disconnect(self):
        self.log.append("disconnected")


class ExplodingRiemannClientTransport(FakeRiemannClientTransport):
    def __init__(self, log):
        super().__init__(log)
        self.connected = True

    def send(self, msg):
        self.log.append("try to send")
        if self.connected:
            self.log.append("sent")
        else:
            self.log.append("connection refused")
            raise ConnectionRefusedError

    def connect(self):
        if self.connected:
            self.log.append("connected")
        else:
            self.log.append("connection refused")
            raise ConnectionRefusedError


class TestReconnect:
    def test_we_reconnect_once_on_failure_regardless(self):
        # regardless what state we think the connection is in
        t = striemann.metrics.RiemannTransport("dummy host", "dummy port")

        failed = False

        def fail_once(self_):
            nonlocal failed
            if not failed:
                failed = True
                raise Exception("bother")

        log = []
        t.transport = FakeRiemannClientTransport(log, fail_once)
        t.flush(is_closing=False)
        assert log == [
            "connected",
            "try to send",
            "disconnected",
            "connected",
            "try to send",
            "sent",
        ]

    def test_connection_refused_reconnection(self):
        t = striemann.metrics.RiemannTransport("dummy host", "dummy port")
        log = []
        t.transport = ExplodingRiemannClientTransport(log)

        t.flush(is_closing=False)
        t.transport.connected = False
        t.flush(is_closing=False)
        t.transport.connected = True
        t.flush(is_closing=False)

        assert log == [
            "connected",
            "try to send",
            "sent",
            "try to send",
            "connection refused",
            "disconnected",
            "connection refused",
            "connected",
            "try to send",
            "sent",
        ]

    def test_in_normal_case_we_just_send(self):
        t = striemann.metrics.RiemannTransport("dummy host", "dummy port")

        def succeed(self_):
            pass

        log = []
        t.transport = FakeRiemannClientTransport(log, succeed)
        t.flush(is_closing=False)
        assert log == ["connected", "try to send", "sent"]
