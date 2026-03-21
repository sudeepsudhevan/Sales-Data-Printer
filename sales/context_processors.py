from .utils import ensure_todays_price

def latest_price(request):
    """
    Ensures today's price is recorded and returns the most recent entry.
    """
    entry = ensure_todays_price()
    return {'latest_price_entry': entry}
