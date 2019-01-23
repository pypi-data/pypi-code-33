from dateutil import relativedelta
import pendulum


class RelativeTimeManager:

    @staticmethod
    def relative_delta(period="months", units=1):
        if period == "months":
            return relativedelta.relativedelta(months=units)
        if period == "days":
            return relativedelta.relativedelta(days=units)
        if period == "hours":
            return relativedelta.relativedelta(hours=units)
        if period == "minutes":
            return relativedelta.relativedelta(minutes=units)
        if period == "seconds":
            return relativedelta.relativedelta(seconds=units)

        return relativedelta.relativedelta()

    @staticmethod
    def relative_delta_to_seconds(current_datetime, offset_datetime):
        current_pendulum = pendulum.parse(current_datetime)
        offset_pendulum = pendulum.parse(offset_datetime)
        delta_p = offset_pendulum.diff(current_pendulum)
        return delta_p.total_seconds()
