import json
from dataclasses import asdict
from pathlib import Path
from typing import Callable, Tuple, Union

import log
import pandas as pd

from .data import RunData


class Storage:
    @staticmethod
    def write(data: RunData) -> None:
        raise NotADirectoryError()

    @staticmethod
    def read(path: str) -> RunData:
        raise NotADirectoryError()


class JSONStorage(Storage):
    """
    JSONStorage stores a json representation of the `RunData`.

    The destination is `path / f"lola_run_{data.run_id}.json"`.
    """

    @staticmethod
    def log_file_path(path, run_id) -> Path:
        return Path(path) / f"lola_run_{run_id}.json"

    @staticmethod
    def write(data: RunData) -> None:
        dst = JSONStorage.log_file_path(data.path, data.run_id)
        dst.parent.mkdir(parents=True, exist_ok=True)
        log.info(f"# Storing run under '{dst}'")

        with dst.open("w") as f:
            f.write(json.dumps(asdict(data)))

    @staticmethod
    def read(path: str) -> RunData:
        with open(path, "r") as f:
            return RunData(**json.loads(f.read()))

    # @staticmethod
    # def _date_handler(obj):
    #     return obj.isoformat() if isinstance(obj, (datetime, date)) else None


def read_json_runs(glob_pattern: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Glob for the pattern and read the json runs."""
    lola_jsons = sorted(list(Path().glob(glob_pattern)))
    lola_runs = [json.load(file.open()) for file in lola_jsons]
    log.info(f"# Loading {len(lola_runs)} lola runs...")

    # df_metrics is a table of metrics
    df_metrics = pd.io.json.json_normalize(
        lola_runs, record_path="metrics", meta="run_id"
    )[["run_id", "name", "value", "step", "ts"]]

    # df_overview will contain one row for each run with all relevant overview information
    df_overview = pd.io.json.json_normalize(lola_runs)
    col_order = [
        "project",
        "run_id",
        "path",
        "status",
        "start_time",
        "end_time",
        "git_sha",
        # "git_diff",
        # "git_status",
        # "metrics",
        *sorted(
            [col for col in df_overview.columns.tolist() if col.startswith("params.")]
        ),
    ]
    df_overview = df_overview[col_order]

    def _aggregate_metrics(
        df_metrics: pd.DataFrame,
        agg_fn: Union[Callable, str] = "max",
        agg_name: str = "max",
    ) -> pd.DataFrame:
        """Aggregate and reshape."""
        # get the min values per group, ...
        df_agg = (
            df_metrics.groupby(["run_id", "name"])
            .agg({"value": agg_fn})
            .reset_index()
            .pivot_table(values="value", index="run_id", columns="name")
            .reset_index()
        )
        columns = df_agg.columns.to_list()
        df_agg = df_agg.rename(
            columns={
                col: f"metric.{col}.{agg_name}" for col in columns if col != "run_id"
            }
        )
        return df_agg

    metrics_max = _aggregate_metrics(df_metrics, agg_fn="max", agg_name="max")
    df_overview = df_overview.merge(metrics_max, on="run_id")

    metrics_min = _aggregate_metrics(df_metrics, agg_fn="min", agg_name="min")
    df_overview = df_overview.merge(metrics_min, on="run_id")

    return df_overview, df_metrics
