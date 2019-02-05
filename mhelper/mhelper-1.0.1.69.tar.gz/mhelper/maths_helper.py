from typing import Tuple

INFINITE = float( 'Inf' )

def increment_mean( mean: float, count: int, new_value: float ) -> Tuple[float, int]:
    new_count = count + 1
    new_mean = mean + ((new_value - mean) / new_count)
    return new_mean, new_count


def safe_div( a, b ):
    if b == 0:
        return INFINITE
    
    return a / b


def percent(a, b):
    return a, safe_div(a,b)