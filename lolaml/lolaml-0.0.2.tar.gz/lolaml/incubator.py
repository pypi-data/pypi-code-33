"""
HERE BE DRAGONS.

Everything in incubator.py is subject to breaking changes.
Use at your own risk.
"""
import altair as alt
import pandas as pd


def _esc(name: str) -> str:
    r"""
    Escape altair field names that contain a dot.

    dots "." in field names are interpreted as hierachical access,
    but quite often they are not.
    Escape the field names.

    Examples:
        >>> _esc("foo.bar") == "foo\\.bar"
        True
        >>> _esc("foo_bar") == "foo_bar"
        True

    """
    return name.replace(".", "\\.")


def plot_overview(df_overview: pd.DataFrame) -> alt.Chart:
    plot_max = (
        alt.Chart(df_overview)
        .mark_bar()
        .encode(x=alt.X("run_id:N"), y=alt.Y(_esc("metric.val_loss.max:Q")))
    )
    plot_min = (
        alt.Chart(df_overview)
        .mark_bar()
        .encode(x=alt.X("run_id:N"), y=alt.Y(_esc("metric.val_loss.min:Q")))
    )
    return plot_min | plot_max


def plot_metrics_siple(df_metrics: pd.DataFrame) -> alt.Chart:
    plot = (
        alt.Chart(df_metrics)
        .mark_line()
        .encode(x="step:Q", y="value:Q", column="name", color=alt.Color("run_id:N"))
        .interactive()
    )
    return plot
