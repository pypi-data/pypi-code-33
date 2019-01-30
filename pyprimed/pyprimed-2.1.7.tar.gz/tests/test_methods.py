# -*- coding: utf-8 -*-
"""
TestMethods
"""
import json
import pytest
import pyprimed


@pytest.mark.unit
class TestResourceRequest:
    def test_delete(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "DELETE"
            assert kwargs["path"] == "models/xyz"
            assert kwargs["params"] == None
            assert kwargs["data"] == None
            assert kwargs["headers"] == None

        monkeypatch.setattr(pio, "_push_operation", mockrequest)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        model.delete


@pytest.mark.unit
class TestCollectionRequest:
    def test_create(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "CREATE"
            assert kwargs["path"] == "models"
            assert kwargs["data"] == {"name": "mymodel"}
            return pyprimed.util.Dictionary.merge(kwargs["data"], {"uid": 1234})

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        pio.models.create(name="mymodel")

    def test_get(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "GET"
            assert kwargs["path"] == "models"
            assert kwargs["params"] == {"filter": '{"name__exact": "mymodel"}'}
            return {"name": "mymodel", "uid": 1234}

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        pio.models.get(name="mymodel")

    def test_all(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "ALL"
            assert kwargs["path"] == "models"
            return ({}, "models 0-0/0")

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        pio.models.all()

    def test_filter(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "FILTER"
            assert kwargs["path"] == "models"
            assert kwargs["params"] == {
                "filter": '{"name__exact": "mymodel"}',
                "range": "[0, 100]",
                "sort": '["name", "ASC"]',
            }
            return ({}, "models 0-0/0")

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        pio.models.filter(name="mymodel")

    def test_upsert(self, monkeypatch, pio):
        def mock_mark_done(*args, **kwargs):
            # TODO: verify args, kwargs
            pass

        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "UPSERT"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "UPSERT":
                assert kwargs["path"] == "signals?model.uid=xyz"
                assert len(kwargs["data"]) == 100

                assert kwargs["headers"]["Content-Type"] == "application/json"
                assert kwargs["headers"]["TX-OPNAME"] == "UpsertSignals"

                return ({"guuid": "someguuid", "fillratio": 0.3}, 200)
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)
        monkeypatch.setattr(pio, "_mark_done", mock_mark_done)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        signals = [{"key": "signal-{i}".format(i=i)} for i in range(1000)]
        guuid, _ = model.signals.upsert(signals, chunk_size=100)

        assert guuid == "someguuid"

    def test_delsert(self, monkeypatch, pio):
        def mock_mark_done(*args, **kwargs):
            # TODO: verify args, kwargs
            pass

        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "DELSERT"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "DELSERT":
                assert kwargs["path"] == "signals?model.uid=xyz"
                assert len(kwargs["data"]) == 100

                assert kwargs["headers"]["Content-Type"] == "application/json"
                assert kwargs["headers"]["TX-OPNAME"] == "DelsertSignals"

                return ({"guuid": "someguuid", "fillratio": 0.3}, 200)
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)
        monkeypatch.setattr(pio, "_mark_done", mock_mark_done)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        signals = [{"key": "signal-{i}".format(i=i)} for i in range(1000)]
        guuid, _ = model.signals.delsert(signals, chunk_size=100)

        assert guuid == "someguuid"

    def test_delete(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "DELETE"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "DELETE":
                assert kwargs["path"] == "models"
                assert kwargs["params"] == {"filter": '{"name__exact": "mymodel"}'}
                assert kwargs["headers"] == {"X-FORCE-DELETE": "FALSE"}
                return {"guuid": "123"}
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        pio.models.delete(name="mymodel")

    def test_async_false(self, monkeypatch, pio):
        self.ops_done = 0

        def mock_mark_done(*args, **kwargs):
            # TODO: verify args, kwargs
            pass

        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "UPSERT"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "UPSERT":
                return ({"guuid": "someguuid", "fillratio": 0.3, "started_at": 27}, 200)
            if kwargs["operation"] == "TRANSACTION_STATUS":
                if self.ops_done <= 2:
                    retval = (
                        {
                            "current_state": "OPERATION:STARTED",
                            "num_states": 10,
                            "current_state_idx": self.ops_done,
                            "errmsg": None
                        },
                        200,
                    )
                else:
                    retval = ({
                        "current_state": "OPERATION:ENDED",
                        "num_states": 10,
                        "current_state_idx": self.ops_done,
                        "errmsg": None
                    }, 200)

                self.ops_done += 1
                return retval

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)
        monkeypatch.setattr(pio, "_mark_done", mock_mark_done)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        signals = [{"key": "signal-{i}".format(i=i)} for i in range(1000)]
        guuid, _ = model.signals.upsert(signals, chunk_size=100, async=False)


@pytest.mark.unit
class TestRelationshipCollectionRequest:
    def test_create(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "CREATE"
            assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
            assert kwargs["data"] == {"sk": "A", "tk": "1", "score": 0.75}
            return pyprimed.util.Dictionary.merge(
                kwargs["data"], {"from_uid": 1234, "to_uid": 5678}
            )

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).create(
            sk="A", tk="1", score=0.75
        )

    def test_all(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "ALL"
            assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
            return ({}, "models 0-0/0")

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).all()

    def test_filter(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert kwargs["operation"] == "FILTER"
            assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
            assert kwargs["params"] == {
                "filter": '{"sk__exact": "A"}',
                "range": "[0, 100]",
                "sort": '["score", "DESC"]',
            }
            return ({}, "models 0-100/100")

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).filter(sk="A")

    def test_upsert(self, monkeypatch, pio):
        def mock_mark_done(*args, **kwargs):
            # TODO: verify args, kwargs
            pass

        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "UPSERT"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "UPSERT":
                assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
                assert kwargs["data"] == [
                    {"sk": "A", "tk": "1", "score": 0.75},
                    {"sk": "B", "tk": "1", "score": 0.1},
                ]

                return ({"guuid": "someguuid", "fillratio": 0.3, "started_at": 27}, 200)
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)
        monkeypatch.setattr(pio, "_mark_done", mock_mark_done)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).upsert(
            [
                {"sk": "A", "tk": "1", "score": 0.75},
                {"sk": "B", "tk": "1", "score": 0.1},
            ]
        )

    def test_delsert(self, monkeypatch, pio):
        def mock_mark_done(*args, **kwargs):
            # TODO: verify args, kwargs
            pass

        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "DELSERT"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "DELSERT":
                assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
                assert kwargs["data"] == [
                    {"sk": "A", "tk": "1", "score": 0.75},
                    {"sk": "B", "tk": "1", "score": 0.1},
                ]

                return ({"guuid": "someguuid", "fillratio": 0.3, "started_at": 27}, 200)
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)
        monkeypatch.setattr(pio, "_mark_done", mock_mark_done)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).delsert(
            [
                {"sk": "A", "tk": "1", "score": 0.75},
                {"sk": "B", "tk": "1", "score": 0.1},
            ]
        )

    # def test_delsert(self, monkeypatch, pio):
    #     def mock_upsert(path, data, headers):
    #         assert path == "predictions?model.uid=xyz&universe.uid=123"
    #         assert data == [
    #             {"sk": "A", "tk": "1", "score": 0.75},
    #             {"sk": "B", "tk": "1", "score": 0.1},
    #         ]
    #         return ({"guuid": "abc", "started_at": 27, "fillratio": 0.3}, 200)

    #     def mock_delete(path, params, headers):
    #         assert path == "predictions?model.uid=xyz&universe.uid=123"

    #         filter = json.loads(params["filter"])
    #         assert filter["created_at__lt"]
    #         assert filter["guuid__ne"]

    #         return {"guuid": "123"}

    #     def mock_transaction_status(path):
    #         return {"STATUS": "FINISHED"}, 200

    #     monkeypatch.setattr(pio._client, "upsert", mock_upsert)
    #     monkeypatch.setattr(pio._client, "delete", mock_delete)
    #     monkeypatch.setattr(pio._client, "transaction_status", mock_transaction_status)

    #     model = pyprimed.models.model.Model(parent=pio, uid="xyz")
    #     universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

    #     pio.predictions.on(model=model, universe=universe).delsert(
    #         [
    #             {"sk": "A", "tk": "1", "score": 0.75},
    #             {"sk": "B", "tk": "1", "score": 0.1},
    #         ]
    #     )

    def test_delete(self, monkeypatch, pio):
        def mockrequest(*args, **kwargs):
            assert (
                kwargs["operation"] == "DELETE"
                or kwargs["operation"] == "TRANSACTION_STATUS"
            )

            if kwargs["operation"] == "DELETE":
                assert kwargs["path"] == "predictions?model.uid=xyz&universe.uid=123"
                assert kwargs["params"] == {"filter": '{"sk__exact": "A"}'}
                assert kwargs["headers"] == {"X-FORCE-DELETE": "FALSE"}
                return {"guuid": "123"}
            else:
                return {"STATUS": "FINISHED"}, 200

        monkeypatch.setattr(pio, "_dispatch_request", mockrequest)

        model = pyprimed.models.model.Model(parent=pio, uid="xyz")
        universe = pyprimed.models.universe.Universe(parent=pio, uid="123")

        pio.predictions.on(model=model, universe=universe).delete(sk="A")
