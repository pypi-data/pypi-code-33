import functools
from urllib.parse import urljoin

from django.conf import settings


def get_url(url_name, default=None):
    return getattr(settings, url_name, None) or default


# SERVICES
SERVICE_EXPORT_READINESS = get_url(
    'DIRECTORY_CONSTANTS_URL_EXPORT_READINESS',
    'https://www.great.gov.uk'
)
SERVICES_INVEST = get_url(
    'DIRECTORY_CONSTANTS_URL_INVEST',
    'https://invest.great.gov.uk'
)
SERVICES_EVENTS = get_url(
    'DIRECTORY_CONSTANTS_URL_EVENTS',
    'https://www.events.trade.gov.uk'
)
SERVICES_SOO = get_url(
    'DIRECTORY_CONSTANTS_URL_SELLING_ONLINE_OVERSEAS',
    'https://selling-online-overseas.export.great.gov.uk'
)
SERVICES_FAS = get_url(
    'DIRECTORY_CONSTANTS_URL_FIND_A_SUPPLIER',
    'https://trade.great.gov.uk'
)
build_great_url = functools.partial(urljoin, SERVICE_EXPORT_READINESS)
SERVICES_SSO = get_url(
    'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON',
    build_great_url('sso/')
)
SERVICES_EXOPPS = get_url(
    'DIRECTORY_CONSTANTS_URL_EXPORT_OPPORTUNITIES',
    build_great_url('export-opportunities/')
)
SERVICES_FAB = get_url(
    'DIRECTORY_CONSTANTS_URL_FIND_A_BUYER',
    build_great_url('find-a-buyer/')
)
SERVICES_SSO_PROFILE = get_url(
    'DIRECTORY_CONSTANTS_URL_SSO_PROFILE',
    build_great_url('profile/')
)


# Export readiness
ADVICE_CREATE_AN_EXPORT_PLAN = build_great_url('advice/create-an-export-plan/')
ADVICE_FIND_AN_EXPORT_MARKET = build_great_url('advice/find-an-export-market/')
ADVICE_DEFINE_ROUTE_TO_MARKET = build_great_url(
    'advice/define-route-to-market/')
ADVICE_GET_EXPORT_FINANCE_AND_FUNDING = build_great_url(
    'advice/get-export-finance-and-funding/')
ADVICE_MANAGE_PAYMENT_FOR_EXPORT_ORDERS = build_great_url(
    'advice/manage-payment-for-export-orders/')
ADVICE_PREPARE_TO_DO_BUSINESS_IN_A_FOREIGN_COUNTRY = build_great_url(
    'advice/prepare-to-do-business-in-a-foreign-country/')
ADVICE_MANAGE_LEGAL_AND_ETHICAL_COMPLIANCE = build_great_url(
    'advice/manage-legal-and-ethical-compliance/')
ADVICE_PREPARE_FOR_EXPORT_PROCEDURES_AND_LOGISTICS = build_great_url(
    'advice/prepare-for-export-procedures-and-logistics/')

CUSTOM_PAGE = build_great_url('custom/')
EXPORTING_NEW = build_great_url('new/')
EXPORTING_OCCASIONAL = build_great_url('occasional/')
EXPORTING_REGULAR = build_great_url('regular/')
GUIDANCE_MARKET_RESEARCH = build_great_url('market-research/')
GUIDANCE_CUSTOMER_INSIGHT = build_great_url('customer-insight/')
GUIDANCE_FINANCE = build_great_url('finance/')
GUIDANCE_BUSINESS_PLANNING = build_great_url('business-planning/')
GUIDANCE_GETTING_PAID = build_great_url('getting-paid/')
GUIDANCE_OPERATIONS_AND_COMPLIANCE = build_great_url(
    'operations-and-compliance/'
)
GET_FINANCE = build_great_url('get-finance/')
TERMS_AND_CONDITIONS = build_great_url('terms-and-conditions/')
ABOUT = build_great_url('about/')
PRIVACY_AND_COOKIES = build_great_url('privacy-and-cookies/')
PERFORMANCE_DASHBOARD = build_great_url('performance-dashboard/')
FEEDBACK = build_great_url('contact/feedback/')
CONTACT_US = build_great_url('contact/')

DIT = (
    'https://www.gov.uk/government/organisations/'
    'department-for-international-trade'
)

# Invest
build_invest_url = functools.partial(urljoin, SERVICES_INVEST)
INVEST_INDUSTRIES = build_invest_url('industries/')
INVEST_SETUP_GUIDE = build_invest_url('uk-setup-guide/')
