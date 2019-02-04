from pkg_resources import EntryPoint

from .conftest import mock_create_namespace_module_manager
import worker_detector as wd


def test_get_default_namespace():
    assert isinstance(wd.__NAMESPACE, str)
    assert wd.__NAMESPACE == "skidward.workers"


def test_get_workers_without_providing_namespace():
    all_workers = wd.get_all_workers_on_namespace()

    assert isinstance(all_workers, list)


def test_get_workers_on_fake_provided_namespace():
    all_workers = wd.get_all_workers_on_namespace("skidward.fake.name.space")

    assert isinstance(all_workers, list)
    assert len(all_workers) == 0


def test_get_workers_on_real_provided_namespace(monkeypatch):
    monkeypatch.setattr(
        wd, "create_namespace_module_manager", mock_create_namespace_module_manager
    )
    all_workers = wd.get_all_workers_on_namespace("skidward.real.name.space")

    assert isinstance(all_workers, list)
    assert len(all_workers) > 0
    assert isinstance(all_workers.pop(), str)


def test_load_fake_worker_on_default_namespace(capsys):
    wd.load_worker_on_namespace("fake_name")
    captured = capsys.readouterr()

    assert "No worker could be loaded" in captured.out
    assert "fake_name" in captured.out


def test_load_real_worker_on_fake_namespace(real_namespace, monkeypatch, capsys):
    monkeypatch.setattr(
        wd, "create_namespace_module_manager", mock_create_namespace_module_manager
    )
    all_workers = wd.get_all_workers_on_namespace(real_namespace)
    assert len(all_workers) > 0

    first_worker = all_workers.pop()
    assert isinstance(first_worker, str)

    wd.load_worker_on_namespace(first_worker, "skidward.fake.name.space")
    captured = capsys.readouterr()

    assert "No worker could be loaded" in captured.out
    assert first_worker in captured.out


def test_load_real_worker_on_real_namespace(real_namespace, monkeypatch):
    monkeypatch.setattr(
        wd, "create_namespace_module_manager", mock_create_namespace_module_manager
    )
    all_workers = wd.get_all_workers_on_namespace(real_namespace)
    assert len(all_workers) > 0

    first_worker = all_workers.pop()
    load_result = wd.load_worker_on_namespace(first_worker, real_namespace)

    assert load_result is not None
    assert isinstance(load_result, EntryPoint)
    assert load_result.module_name == first_worker
