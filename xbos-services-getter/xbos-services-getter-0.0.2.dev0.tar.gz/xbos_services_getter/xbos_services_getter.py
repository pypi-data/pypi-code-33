import grpc

from .lib import *

import datetime
import pytz
import pandas as pd

import xbos_services_utils3 as utils

import os

# TEMPERATURE_BAND_ADDRESS = "localhost:50055"
# PRICE_ADDRESS = "localhost:50051"
# OCCUPANCY_ADDRESS = "localhost:50054"
# OUTSIDE_PREDICTION = "localhost:50059"
# OUTSIDE_HISTORICAL = "localhost:50058"
# DISCOMFORT_ADDRESS = "localhost:50057"
# HVAC_CONSUMPTION_ADDRESS = "localhost:50056"
# INDOOR_HISTORIC_ADDRESS = "localhost:50060"
# INDOOR_PREDICTION_ADDRESS = "localhost:50053"

TEMPERATURE_BAND_ADDRESS = os.environ["TEMPERATURE_BAND_ADDRESS"]
PRICE_ADDRESS = os.environ["PRICE_ADDRESS"]
OCCUPANCY_ADDRESS = os.environ["OCCUPANCY_ADDRESS"]
OUTDOOR_PREDICTION_ADDRESS = os.environ["OUTDOOR_PREDICTION_ADDRESS"]
OUTDOOR_HISTORICAL_ADDRESS = os.environ["OUTDOOR_HISTORICAL_ADDRESS"]
DISCOMFORT_ADDRESS = os.environ["DISCOMFORT_ADDRESS"]
HVAC_CONSUMPTION_ADDRESS = os.environ["HVAC_CONSUMPTION_ADDRESS"]
INDOOR_HISTORIC_ADDRESS = os.environ["INDOOR_HISTORIC_ADDRESS"]
INDOOR_PREDICTION_ADDRESS = os.environ["INDOOR_PREDICTION_ADDRESS"]

# Temperature band functions
def get_temperature_band_stub():
    temperature_band_channel = grpc.insecure_channel(TEMPERATURE_BAND_ADDRESS)
    temperature_band_stub = schedules_pb2_grpc.SchedulesStub(temperature_band_channel)
    return temperature_band_stub


def get_comfortband(temperature_band_stub, bldg, zone, start, end, window):
    """Gets comfortband as pd.df.
    :param temperature_band_stub: grpc stub for temperature_band microservice
    :param bldg: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware) start of comfortband
    :param end: (datetime timezone aware) end of comfortband
    :param window: (str) the interval in which to split the comfortband.
    :return pd.df columns=["t_low", "t_high"], valus=float, index=time"""
    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = utils.get_window_in_sec(window)

    # call service
    comfortband_response = temperature_band_stub.GetComfortband(
        schedules_pb2.Request(building=bldg, zone=zone, start=int(start_unix), end=int(end_unix), window=window,
                              unit="F"))

    # process data
    comfortband_final = pd.DataFrame(columns=["t_high", "t_low"],
                                     index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in comfortband_response.schedules:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        comfortband_final.loc[msg_datetime]["t_high"] = msg.temperature_high
        comfortband_final.loc[msg_datetime]["t_low"] = msg.temperature_low

    return comfortband_final


def get_do_not_exceed(temperature_band_stub, bldg, zone, start, end, window):
    """Gets comfortband as pd.df.
    :param temperature_band_stub: grpc stub for temperature_band microservice
    :param bldg: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware) start of safetyband
    :param end: (datetime timezone aware) end of safetyband
    :param window: (str) the interval in which to split the safetyband.
    :return pd.df columns=["t_low", "t_high"], valus=float, index=time"""
    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = utils.get_window_in_sec(window)

    # call service
    do_not_exceed_response = temperature_band_stub.GetDoNotExceed(
        schedules_pb2.Request(building=bldg, zone=zone, start=int(start_unix), end=int(end_unix), window=window,
                              unit="F"))

    # process data
    do_not_exceed_final = pd.DataFrame(columns=["t_high", "t_low"],
                                       index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in do_not_exceed_response.schedules:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        do_not_exceed_final.loc[msg_datetime]["t_high"] = msg.temperature_high
        do_not_exceed_final.loc[msg_datetime]["t_low"] = msg.temperature_low

    return do_not_exceed_final


# occupancy functions
def get_occupancy_stub():
    occupancy_channel = grpc.insecure_channel(OCCUPANCY_ADDRESS)
    return occupancy_pb2_grpc.OccupancyStub(occupancy_channel)


def get_occupancy(occupancy_stub, bldg, zone, start, end, window):
    """Gets occupancy as pd.series.
    :param occupancy_stub: grpc stub for occupancy microservice
    :param bldg: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return pd.series valus=float, index=time"""

    start_unix = start.timestamp() * 1e9
    end_unix = end.timestamp() * 1e9
    window_seconds = utils.get_window_in_sec(window)

    # call service
    occupancy_response = occupancy_stub.GetOccupancy(
        occupancy_pb2.Request(building=bldg, zone=zone, start=int(start_unix), end=int(end_unix), window=window))

    # process data
    occupancy_final = pd.Series(index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in occupancy_response.occupancies:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        occupancy_final.loc[msg_datetime] = msg.occupancy

    return occupancy_final


# discomfort functions
def get_discomfort_stub():
    discomfort_channel = grpc.insecure_channel(DISCOMFORT_ADDRESS)
    return discomfort_pb2_grpc.DiscomfortStub(discomfort_channel)

def get_discomfort(discomfort_stub, building, temperature, temperature_low, temperature_high, occupancy):
    discomfort_response = discomfort_stub.GetLinearDiscomfort(discomfort_pb2.Request(building=building,
                                                                                    temperature=temperature,
                                                                                    temperature_low=temperature_low,
                                                                                    temperature_high=temperature_high,
                                                                                    unit="F",
                                                                                    occupancy=occupancy))
    return discomfort_response.cost


# indoor historic functions
def get_indoor_historic_stub():
    indoor_historic_channel = grpc.insecure_channel(INDOOR_HISTORIC_ADDRESS)
    return indoor_temperature_action_pb2_grpc.IndoorTemperatureActionStub(indoor_historic_channel)


def get_indoor_temperature_historic(indoor_historic_stub, building, zone, start, end, window):
    """Gets historic indoor temperature as pd.series.
    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return pd.series valus=float, index=time"""
    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = utils.get_window_in_sec(window)

    # call service
    historic_indoor_response = indoor_historic_stub.GetRawTemperatures(
        indoor_temperature_action_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window))

    # process data
    historic_indoor_final = pd.Series(index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in historic_indoor_response.temperatures:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        historic_indoor_final.loc[msg_datetime] = msg.temperature

    return historic_indoor_final


def get_actions_historic(indoor_historic_stub, building, zone, start, end, window):
    """Gets historic indoor temperature as pd.series.
    :param indoor_historic_stub: grpc stub for historic indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return pd.series valus=float, index=time"""
    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = utils.get_window_in_sec(window)

    # call service
    historic_action_response = indoor_historic_stub.GetRawActions(
        indoor_temperature_action_pb2.Request(building=building, zone=zone, start=start_unix, end=end_unix,
                                              window=window))

    # process data
    historic_action_final = pd.Series(index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in historic_action_response.actions:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        historic_action_final.loc[msg_datetime] = msg.action

    return historic_action_final


# Indoor temperature prediction functions
def get_indoor_temperature_prediction_stub():
    indoor_temperature_prediction_channel = grpc.insecure_channel(INDOOR_PREDICTION_ADDRESS)
    return thermal_model_pb2_grpc.ThermalModelStub(indoor_temperature_prediction_channel)


def get_indoor_temperature_prediction(indoor_prediction_stub, building, zone, current_time, action, t_in, t_out,
                                      other_zone_temperatures, occupancy):
    """Gets prediction of indoor temperature.
    :param indoor_prediction_stub: grpc stub for prediction of indoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param current_time: (datetime timezone aware)
    :param action: (int) Action as given in utils file.
    :param t_in: (float) current temperature inside of zone.
    :param t_out: (float) currrent outdoor temperature.
    :param other_zone_temperatures: {zone_i: indoor temperature of zone_i}
    :param occupancy: (float) Indicator: Is the zone currently occupied.
    :return (float) temperature in 5 minutes after current_time in Fahrenheit."""
    current_time_unix = int(current_time.timestamp() * 1e9)

    # call service
    indoor_prediction_response = indoor_prediction_stub.GetPrediction(
        thermal_model_pb2.PredictionRequest(building=building, zone=zone, current_time=current_time_unix,
                                              action=action,
                                              indoor_temperature=t_in, outside_temperature=t_out,
                                              other_zone_temperatures=other_zone_temperatures,
                                              temperature_unit="F", occupancy=occupancy))

    return indoor_prediction_response.temperature


# HVAC Consumption functions
def get_hvac_consumption_stub():
    hvac_consumption_channel = grpc.insecure_channel(HVAC_CONSUMPTION_ADDRESS)
    return hvac_consumption_pb2_grpc.ConsumptionHVACStub(hvac_consumption_channel)


def get_hvac_consumption(hvac_consumption_stub, building, zone):
    hvac_consumption_response = hvac_consumption_stub.GetConsumption(
        hvac_consumption_pb2.Request(building=building, zone=zone))

    hvac_consumption_final = {utils.NO_ACTION: 0,
                              utils.HEATING_ACTION: hvac_consumption_response.heating_consumption,
                              utils.COOLING_ACTION: hvac_consumption_response.cooling_consumption,
                              utils.FAN: hvac_consumption_response.ventilation_consumption,
                              utils.TWO_STAGE_HEATING_ACTION: hvac_consumption_response.heating_consumption_stage_two,
                              utils.TWO_STAGE_COOLING_ACTION: hvac_consumption_response.cooling_consumption_stage_two}

    return hvac_consumption_final


# Outdoor temperature functions
def get_outdoor_historic_stub():
    outdoor_historic_channel = grpc.insecure_channel(OUTDOOR_HISTORICAL_ADDRESS)
    return outdoor_temperature_historical_pb2_grpc.OutdoorTemperatureStub(outdoor_historic_channel)


def get_outdoor_temperature_historic(outdoor_historic_stub, building, start, end, window):
    """Gets historic outdoor temperature as pd.series.
    :param indoor_historic_stub: grpc stub for historic outdoor temperature microservice
    :param building: (str) building name
    :param zone: (str) zone name
    :param start: (datetime timezone aware)
    :param end: (datetime timezone aware)
    :param window: (str) the interval in which to split the data.
    :return pd.series valus=float, index=time"""
    start_unix = int(start.timestamp() * 1e9)
    end_unix = int(end.timestamp() * 1e9)
    window_seconds = utils.get_window_in_sec(window)

    # call service
    historic_outdoor_response = outdoor_historic_stub.GetTemperature(
        outdoor_temperature_historical_pb2.TemperatureRequest(
            building=building, start=int(start_unix), end=int(end_unix), window=window))

    # process data
    historic_outdoor_final = pd.Series(index=pd.date_range(start, end, freq=str(window_seconds) + "S"))[:-1]
    for msg in historic_outdoor_response.temperatures:
        msg_datetime = datetime.datetime.utcfromtimestamp(msg.time / 1e9).replace(tzinfo=pytz.utc).astimezone(
            tz=start.tzinfo)
        historic_outdoor_final.loc[msg_datetime] = msg.temperature

    return historic_outdoor_final
