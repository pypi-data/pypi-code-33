import pandas as pd
from . import utils


class Trade:
    def __init__(self, ds, fills_df, t0=None):
        self.ds = ds
        self.fills_df = fills_df
        work_df = fills_df.copy()
        work_df.index = work_df.index.floor(freq="1min")

        if len(ds["t0"].values) == 0:
            work_ds = ds
        else:
            if t0:
                work_ds = ds.sel(t0=t0)
            else:
                work_ds = ds.sel(t0=ds["t0"].values[-1])

        if t0:
            work_df = work_df.loc[:t0]

        work_df[["maturity", "type", "strike"]] = work_df[
            ["maturity", "type", "strike"]
        ].fillna("")
        work_df["symbol"] = work_df[["maturity", "type", "strike"]].apply(
            lambda x: "".join(map(str, x)), axis=1
        )
        work_df["turnover"] = work_df["qty"] * work_df["price"]
        grouped_by_symbol = work_df.groupby("symbol")
        qty = grouped_by_symbol["qty"].sum()
        turnover = grouped_by_symbol["turnover"].sum()

        summary_df = pd.DataFrame(
            [], index=qty.index.values, columns=["maturity", "type", "strike", "price"]
        )
        for col in ["maturity", "type", "strike"]:
            summary_df[col] = summary_df.index.map(
                lambda x: utils.take_one_data(work_df.loc[work_df["symbol"] == x, col])
            )
        summary_df["price"] = summary_df.apply(
            lambda x: self.get_price_from_ds(
                work_ds, t0, str(x["maturity"]), x["type"], x["strike"]
            ),
            axis=1,
        )
        summary_df["qty"] = qty
        summary_df["pl"] = (summary_df["qty"] * summary_df["price"]) - turnover
        self.summary_df = summary_df

        self.work_df = work_df

    def get_price_from_ds(self, ds, t0, maturity, fop_type, strike=None):
        price = {"C": "price_call", "P": "price_put", "F": "price_fut"}[fop_type]
        if fop_type == "F":
            return float(ds.sel(maturity=maturity)[price].values)
        else:
            return float(ds.sel(maturity=maturity, k=strike)[price].values)
