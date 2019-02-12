import requests
import time

# API
API_DOCUMENTATION_URL = "https://docs.co2signal.com/"
API_BASE_URL = "https://api.co2signal.com/v1/"
API_ENDPOINTS = {"latest_country_code": API_BASE_URL + "latest?countryCode={country_code}",
                 "latest_coordinates": API_BASE_URL + "latest?lon={longitude}&lat={latitude}",
                 }
WAIT_BETWEEN_REQUEST = 5


def get_latest(token, country_code = None, latitude = None, longitude = None, wait = True):
    """Get latest data from the APIs.
    :param token: the token as received from co2signal.com.
    :param country_code: (optional) the country code of the country (either the country code or both coordinates should
                         be given.
    :param latitude: (optional) the latitude of the location (either the country code or both coordinates should
                     be given.
    :param longitude: (optional) the longitude of the location (either the country code or both coordinates should
                      be given.
    :return: a json object containing the latest values.
    """
    latest_data = None
    header = {'auth-token': token}

    if country_code is not None:
        latest_data = (requests
                           .get(API_ENDPOINTS["latest_country_code"]
                                .format(country_code = country_code),
                                headers = header)
                           .json())
    if (latitude is not None) & (longitude is not None):
        latest_data = (requests
                           .get(API_ENDPOINTS["latest_coordinates"]
                                .format(longitude = str(longitude), latitude = str(latitude)),
                                headers = header)
                           .json())

    if latest_data is None:
        raise ValueError("No inputs defined")

    if 'message' in latest_data.keys():
        if latest_data['message'] == "API rate limit exceeded":
            if wait:
                time.sleep(WAIT_BETWEEN_REQUEST)
                latest_data = get_latest(token = token, country_code = country_code, latitude = latitude,
                                         longitude = longitude, wait = False)
            else:
                raise ValueError("API rate limit exceeded. Please wait a few seconds before retrying the request.")
        else:
            raise ValueError(latest_data['message'])

    return latest_data
