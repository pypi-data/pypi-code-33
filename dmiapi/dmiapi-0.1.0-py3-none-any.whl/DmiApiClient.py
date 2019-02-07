from datetime import datetime

import asyncio
import aiohttp
from aiohttp.hdrs import USER_AGENT

import json

import logging

from .constants import *

class DmiApiClient(object):
    """This class allows access to the Danish Metrology Institute (DMI) API.

    Note that it is based on trial and error, there is very little
    official documentation about this API yet, so use at your own risk.
    """    

    def __init__(self):
        """Initialize the class.
        """
        self.logger = logging.getLogger(__name__)
        self.headers = {
            USER_AGENT: '{}/{}'.format('py-dmiapi', '0.1.0'),
        }


    async def async_observations(self, station_id):
        """Fetch the latest observations for a given weather station or location."""
        try:
            params = {
                API_PARAM_COMMAND: API_COMMAND_OBSERVATIONS,
                API_PARAM_ID: int(station_id),
            }            
            
            async with aiohttp.ClientSession() as session:
                async with session.get(API_BASE_URL,
                                       params = params,
                                       headers = self.headers,
                                       timeout = API_TIMEOUT) as response:
                    self.logger.debug("Request '%s' finished with status code %s", response.url, response.status)
                    data = await response.json(encoding = 'utf-8')

                    # Find all measurements and times for this station
                    measurements = set()
                    times = set()
                    result_data = {}
                    for k, v in data.items():
                        if isinstance(v, dict):
                            measurements.update([k])
                            times.update(v.keys())
                        else:
                            # Not measurements, but meta-data about the station
                            result_data[k] = v
              
                    # Re-arrange data in time steps (as forecast respondse)
                    observations = []
                    for t in sorted(times):
                        observation = { 
                            'time': datetime.strptime(t, TIME_FORMAT)
                        }
                        for m in measurements:
                            observation[m[0].lower() + m[1:]] = data[m][t] if t in data[m] else None
                        observations.append(observation)
                    
                    result_data['observations'] = observations
                    return result_data
        except:
            self.logger.exception("While fetching observations")


    async def async_forecasts(self, station_id):
        """Fetch the latest forecasts for a given location"""
        try:
            params = {
                API_PARAM_COMMAND: API_COMMAND_FORECAST,
                API_PARAM_ID: int(station_id),
            }            
            
            async with aiohttp.ClientSession() as session:
                async with session.get(API_BASE_URL,
                                       params = params,
                                       headers = self.headers,
                                       timeout = API_TIMEOUT) as response:
                    self.logger.debug("Request '%s' finished with status code %s", response.url, response.status)
                    data = await response.json(encoding = 'utf-8')

                    # Rename danish variable, since all others are english
                    forecasts = data.pop('timeserie')

                    # Parse dates
                    for f in forecasts:
                        f['time'] = datetime.strptime(f['time'], TIME_FORMAT)

                    data['forecasts'] = forecasts

                    return data
        except:
            self.logger.exception("While fetching forecast")


    def observations(self, station_id):
        """Fetch the latest observations for a given weather station or location."""
        return asyncio.get_event_loop().run_until_complete(self.async_observations(station_id))


    def forecasts(self, station_id):
        """Fetch the latest forecasts for a given location"""
        return asyncio.get_event_loop().run_until_complete(self.async_forecast(station_id))
