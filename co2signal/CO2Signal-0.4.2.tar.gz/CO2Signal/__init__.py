from CO2Signal.co2signal import get_latest

def get_latest_carbon_intensity(token, country_code = None, latitude = None, longitude = None):
    """Get latest carbon intensity.
    :param token: the token as received from co2signal.com.
    :param country_code: (optional) the country code of the country (either the country code or both coordinates should
                         be given.
    :param latitude: (optional) the latitude of the location (either the country code or both coordinates should
                     be given.
    :param longitude: (optional) the longitude of the location (either the country code or both coordinates should
                      be given.
    :return: the latest carbon intensity in gCO2eq/kWh.
    """

    latest_data = get_latest(token, country_code, latitude, longitude)

    if 'data' not in latest_data.keys():
        raise ValueError("This location currently does not provide a carbon intensity. Please check electricitymap.org for further information.")

    if 'carbonIntensity' not in latest_data['data'].keys():
        raise ValueError("This location currently does not provide a carbon intensity. Please check electricitymap.org for further information.")

    latest_carbon_intensity = latest_data['data']['carbonIntensity']

    return latest_carbon_intensity