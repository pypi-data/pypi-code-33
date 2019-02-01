"""
Package for estimating price elasticities and making price-aware forecasts 
"""
from warnings import warn

try:
    from ftk.price_aware.pricing_engine_estimator import PricingEngineEstimator
except ImportError:
    warn('Unable to import PricingEngineEstimator. '
         + 'The pricingengine package may not be available in this environment.')
