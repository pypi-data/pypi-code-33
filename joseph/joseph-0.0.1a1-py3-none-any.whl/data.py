from abc import ABC, abstractmethod

import jpxtime3
import numpy as np
import pandas as pd
import xarray as xr

from . import utils


class AbstractBasePrice(ABC):
    @abstractmethod
    def set_maturities(self):
        pass

    @abstractmethod
    def set_t0(self):
        pass

    @abstractmethod
    def set_t1(self):
        pass

    @abstractmethod
    def set_t(self):
        pass

    @abstractmethod
    def set_strikes(self):
        pass

    @abstractmethod
    def set_prices_fut(self):
        pass

    @abstractmethod
    def set_atm(self):
        pass

    @abstractmethod
    def set_price_op(self):
        pass

    @abstractmethod
    def set_iv(self):
        pass

    @abstractmethod
    def set_interpolated_iv(self):
        pass

    @abstractmethod
    def set_interpolated_call(self):
        pass

    @abstractmethod
    def set_interpolated_put(self):
        pass


class DerivativesPrice(AbstractBasePrice):
    columns = {
        "maturity": "maturity",
        "strike": "strike",
        "fop_type": "fop_type",
        "bid": "bid",
        "bid_qty": "bid_qty",
        "ask": "ask",
        "ask_qty": "ask_qty",
        "mid": "mid",
    }
    identifiers = {"Futures": "F", "Call": "C", "Put": "P"}

    def __init__(
        self, df, columns={}, identifiers={}, allow_spread=0, allow_spread_fut=None
    ):

        self.allow_spread = allow_spread
        self.allow_spread_fut = allow_spread_fut
        self.columns.update(columns)
        inverted_dict = dict([[v, k] for k, v in columns.items()])
        self.identifiers.update(identifiers)
        source_df = df.rename(columns=inverted_dict).copy()
        source_df = self.fill_wide_spread(source_df)
        self.source_df = source_df

        self.set_maturities()
        self.set_t0()
        self.set_t1()
        self.set_t()
        self.set_strikes()
        self.set_prices_fut()
        self.set_atm(intervals=125)
        self.set_price_op()

    def set_maturities(self):
        self.maturities = self.source_df["maturity"].unique()

    def set_t0(self):
        self.t0 = utils.take_one_data(self.source_df.index)
        pass

    def set_t1(self):
        pass

    def set_t(self):
        self.t = np.array(
            [
                (pd.to_datetime(t1) - self.t0).total_seconds() / 31_536_000
                for t1 in self.t1
            ]
        )

    def set_strikes(self):
        unique = self.source_df["strike"].unique()
        strikes = unique[np.vectorize(bool)(unique)]
        strikes.sort()
        self.strikes = strikes

    def set_prices_fut(self):
        df = self.source_df[
            self.source_df["fop_type"] == self.identifiers["Futures"]
        ].sort_values("maturity")
        self._set_pricee(df, "fut")

    def set_atm(self, intervals=1):
        self.atm = np.array(
            [utils.get_atm_strike(price, intervals) for price in self.price_fut]
        )

    def set_price_op(self):
        self._set_atters("call")
        self._set_atters("put")
        for maturity in self.maturities:
            self.set_price_op_by_maturity(maturity)

    def set_price_op_by_maturity(self, maturity):
        maturity_no = {m: i for i, m in enumerate(self.maturities)}[maturity]
        call_df = (
            self.source_df[
                (self.source_df["fop_type"] == self.identifiers["Call"])
                & (self.source_df["maturity"] == maturity)
            ]
            .set_index("strike")
            .sort_index()
            .copy()
        )
        put_df = (
            self.source_df[
                (self.source_df["fop_type"] == self.identifiers["Put"])
                & (self.source_df["maturity"] == maturity)
            ]
            .set_index("strike")
            .sort_index()
            .copy()
        )
        if np.isnan(self.price_fut).any():
            filled_s = (
                pd.Series(self.price_fut)
                .fillna(self.price_fut[~np.isnan(self.price_fut)].mean())
                .values
            )
            s = filled_s[maturity_no]
            filled_atm = (
                pd.Series(self.atm).fillna(self.atm[~np.isnan(self.atm)].mean()).values
            )
            atm = filled_atm[maturity_no]
        else:
            s = self.price_fut[maturity_no]
            atm = self.atm[maturity_no]
        otm_call = utils.fill_zero_under_threshold(
            utils.fill_otm(call_df["mid"], atm, 0), 0
        )
        otm_put = utils.fill_zero_under_threshold(
            utils.fill_otm(put_df["mid"], atm, 1), 1
        )
        call_df.loc[otm_call.index, "mid"] = otm_call
        put_df.loc[otm_put.index, "mid"] = otm_put
        itm_call = utils.calc_parity_from_series_data(s, otm_put, 1)
        itm_put = utils.calc_parity_from_series_data(s, otm_call, 0)
        call_df.loc[itm_call.index, "mid"] = itm_call
        put_df.loc[itm_put.index, "mid"] = itm_put

        self._set_pricee(call_df, "call")
        self._set_pricee(put_df, "put")

    def fill_wide_spread(self, df):
        new_df = df.reset_index().copy()
        if self.allow_spread_fut:
            ix_fut = new_df[new_df["fop_type"] == self.identifiers["Futures"]].index
            ix_op = new_df.index.difference(ix_fut)
            new_df.loc[ix_fut, "mid"] = np.where(
                (new_df.loc[ix_fut, "ask"] - new_df.loc[ix_fut, "bid"])
                < self.allow_spread_fut,
                new_df.loc[ix_fut, "mid"].values,
                np.nan,
            )
            new_df.loc[ix_op, "mid"] = np.where(
                (new_df.loc[ix_op, "ask"] - new_df.loc[ix_op, "bid"])
                < self.allow_spread,
                new_df.loc[ix_op, "mid"].values,
                np.nan,
            )
        else:
            new_df["mid"] = np.where(
                (df["ask"] - df["bid"]) < self.allow_spread, df["mid"].values, np.nan
            )
        return new_df.set_index("date")

    def _set_pricee(self, df, attr_name):
        if attr_name == "fut":
            setattr(self, f"bid_{attr_name}", df["bid"].values)
            setattr(self, f"bid_qty_{attr_name}", df["bid_qty"].values)
            setattr(self, f"ask_{attr_name}", df["ask"].values)
            setattr(self, f"ask_qty_{attr_name}", df["ask_qty"].values)
            setattr(self, f"price_{attr_name}", df["mid"].values)
        else:
            getattr(self, f"bid_{attr_name}").append(df["bid"])
            getattr(self, f"bid_qty_{attr_name}").append(df["bid_qty"])
            getattr(self, f"ask_{attr_name}").append(df["ask"])
            getattr(self, f"ask_qty_{attr_name}").append(df["ask_qty"])
            getattr(self, f"price_{attr_name}").append(df["mid"])

    def _set_atters(self, attr_name):
        setattr(self, f"bid_{attr_name}", [])
        setattr(self, f"bid_qty_{attr_name}", [])
        setattr(self, f"ask_{attr_name}", [])
        setattr(self, f"ask_qty_{attr_name}", [])
        setattr(self, f"price_{attr_name}", [])

    def set_iv(self):
        pass

    def set_interpolated_iv(self):
        pass

    def set_interpolated_call(self):
        pass

    def set_interpolated_put(self):
        pass


class DerivativesData(DerivativesPrice):
    def __init__(
        self,
        df,
        columns={},
        identifiers={},
        allow_spread=0,
        allow_spread_fut=None,
        r=0.0,
        q=0.0,
    ):
        super().__init__(df, columns, identifiers, allow_spread, allow_spread_fut)
        self.n = len(self.maturities)
        self.r = self.set_arr(r)
        self.q = self.set_arr(q)
        self.set_iv()
        self.set_interpolated_iv()
        self.set_interpolated_call()
        self.set_interpolated_put()
        self.set_atm_iv()
        self.set_atm_iv_std()

    def set_arr(self, value):
        if isinstance(value, float):
            return np.full(self.n, value)
        elif len(value) == self.n:
            return value
        else:
            raise ValueError

    def get_iv(self, i):
        s, r, q, t = self.price_fut[i], self.r[i], self.q[i], self.t[i]
        atm = self.atm[i]
        otm_call = utils.fill_otm(self.price_call[i], atm, 0)
        iv_call = utils.calc_iv_from_series_data(otm_call, s, r, q, t, 0)
        otm_put = utils.fill_otm(self.price_put[i], atm, 1)
        iv_put = utils.calc_iv_from_series_data(otm_put, s, r, q, t, 1)
        return pd.concat([iv_put, iv_call]).sort_index()

    def set_iv(self):
        self.iv = [self.get_iv(i) for i in range(self.n)]

    def set_interpolated_iv(self):
        self.interpolated_iv = [iv.interpolate(method="cubic") for iv in self.iv]

    def get_interpolated_prem(self, i, right):
        s, r, q, t = self.price_fut[i], self.r[i], self.q[i], self.t[i]
        price = {0: self.price_call[i], 1: self.price_put[i]}[right].copy()
        price_null = price[price.isnull()]
        iv = self.interpolated_iv[i].loc[price_null.index]
        interp_price = utils.calc_greeks_or_prem_from_series_data(
            "prem", iv, s, r, q, t, right
        )
        price.loc[interp_price.index] = interp_price
        return price

    def set_interpolated_call(self):
        self.interpolated_call = [
            self.get_interpolated_prem(i, 0) for i in range(self.n)
        ]

    def set_interpolated_put(self):
        self.interpolated_put = [
            self.get_interpolated_prem(i, 1) for i in range(self.n)
        ]

    def get_atm_iv(self, i):
        s, atm = self.price_fut[i], self.atm[i]
        if np.isnan(np.array([s, atm])).any():
            return np.nan
        ntm = utils.get_ntm_strike(s, atm, 125)
        atm_iv, ntm_iv = self.iv[i][atm], self.iv[i][ntm]
        return utils.interpolate(s, [atm, ntm], [atm_iv, ntm_iv])

    def set_atm_iv(self):
        self.atm_iv = [self.get_atm_iv(i) for i in range(self.n)]

    def set_atm_iv_std(self):
        if self.year == 365:
            std_days = 0.082_191_780_821_917_8  # 30 / 365.0
        else:
            std_days = 0.101_020_408_163_265_31  # 24.75 / 245
        self.atm_iv_std = utils.interpolate(std_days, self.t, self.atm_iv)

    def to_ds(self):
        dataset = DataSet(self)
        return dataset.to_ds()


class N225DerivativesData(DerivativesData):
    def __init__(
        self,
        df,
        columns={},
        identifiers={"Futures": "M"},
        allow_spread=30,
        allow_spread_fut=50,
        year=365,
        r=0.001,
        q=0.0,
    ):
        self.year = year
        super().__init__(df, columns, identifiers, allow_spread, allow_spread_fut)

    def set_t1(self):
        t1 = [jpxtime3.get_sq(maturity) for maturity in self.maturities]
        opening = jpxtime3.DaySession().opening
        ser = pd.Series(
            self.maturities, index=[pd.datetime.combine(t1_, opening) for t1_ in t1]
        )
        ser.sort_index(inplace=True)
        self.maturities = ser.values
        self.t1 = ser.index.values

    def set_t(self):
        self.t = np.array(
            [
                jpxtime3.get_t(self.t0, pd.to_datetime(t1), year=self.year)
                for t1 in self.t1
            ]
        )


class DataSet:
    def __init__(self, data):
        data_variables = (
            "price_call",
            "bid_call",
            "bid_qty_call",
            "ask_call",
            "ask_qty_call",
            "price_put",
            "bid_put",
            "bid_qty_put",
            "ask_put",
            "ask_qty_put",
            "interpolated_call",
            "interpolated_put",
            "iv",
            "interpolated_iv",
        )

        for var in data_variables:
            setattr(self, var, self.merge_data(getattr(data, var), data.strikes))

        self.coordinates = {
            "t0": data.t0,
            "maturity": ("maturity", data.maturities),
            "k": ("k", data.strikes),
            "r": ("maturity", data.r),
            "q": ("maturity", data.q),
            "s": ("maturity", data.price_fut),
            "t1": ("maturity", data.t1),
            "t": ("maturity", data.t),
            "atm_iv": ("maturity", data.atm_iv),
            "atm": ("maturity", data.atm),
            "atm_iv_std": data.atm_iv_std,
        }
        self.data_variables = {
            "price_fut": (["maturity"], data.price_fut),
            "bid_fut": (["maturity"], data.bid_fut),
            "bid_qty_fut": (["maturity"], data.bid_qty_fut),
            "ask_fut": (["maturity"], data.ask_fut),
            "ask_qty_fut": (["maturity"], data.ask_qty_fut),
            "price_call": (["k", "maturity"], self.price_call),
            "bid_call": (["k", "maturity"], self.bid_call),
            "bid_qty_call": (["k", "maturity"], self.bid_qty_call),
            "ask_call": (["k", "maturity"], self.ask_call),
            "ask_qty_call": (["k", "maturity"], self.ask_qty_call),
            "price_put": (["k", "maturity"], self.price_put),
            "bid_put": (["k", "maturity"], self.bid_put),
            "bid_qty_put": (["k", "maturity"], self.bid_qty_put),
            "ask_put": (["k", "maturity"], self.ask_put),
            "ask_qty_put": (["k", "maturity"], self.ask_qty_put),
            "interpolated_call": (["k", "maturity"], self.interpolated_call),
            "interpolated_put": (["k", "maturity"], self.interpolated_put),
            "iv": (["k", "maturity"], self.iv),
            "interpolated_iv": (["k", "maturity"], self.interpolated_iv),
        }

    def merge_data(self, data, strikes):
        df = pd.concat(data, axis=1)
        return df.reindex(strikes).values

    def to_ds(self):
        return xr.Dataset(self.data_variables, coords=self.coordinates)
