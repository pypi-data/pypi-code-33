from flask import Flask, render_template

from lolaml.incubator import plot_metrics_siple, plot_overview
from lolaml.storage import read_json_runs


app = Flask(__name__)


@app.route("/")
def index():
    return """<h1>helLOLA</h1>

    Check out <a href="/testdata">testdata</a>
    """


@app.route("/<string:prefix>")
def glob(prefix):
    pattern = f"{prefix}/**/lola_run_*.json"
    df_overview, df_metrics = read_json_runs(pattern)

    return render_template(
        "index.html",
        table_data=df_overview.as_matrix().tolist(),
        table_column_names=[{"title": col} for col in df_overview.columns.to_list()],
        vega_specs=[
            plot_overview(df_overview).to_dict(),
            plot_metrics_siple(df_metrics).to_dict(),
        ],
    )
