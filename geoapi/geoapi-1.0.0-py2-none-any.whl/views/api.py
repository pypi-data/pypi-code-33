from flask import Blueprint, jsonify
from geoquery import query


bp = Blueprint(
    __name__,
    __name__,
    template_folder='templates',
    url_prefix='/api'
)


@bp.route(
    '/locations/<country_code>/<lat>/<lon>/<distance>'
)
def api_locations(country_code, lat, lon, distance):
    return jsonify(query(
        country_code=country_code,
        latitude=float(lat),
        longitude=float(lon),
        distance=float(distance)
    ))
