import urllib.request
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MarketDataService:
    """Fetches real live market data (Forex rates) from public APIs."""
    
    _cache: Dict[str, Any] = {}
    _cache_time: float = 0
    CACHE_DURATION = 3600  # 1 hour
    
    @classmethod
    def get_live_rates(cls) -> Dict[str, float]:
        """Fetches live USD exchange rates. Returns a dictionary of currency -> rate."""
        import time
        current_time = time.time()
        
        # Return cached data if fresh
        if cls._cache and (current_time - cls._cache_time < cls.CACHE_DURATION):
            return cls._cache
            
        try:
            # Using ExchangeRate-API (free, no key required for basic tier)
            url = "https://open.er-api.com/v6/latest/USD"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                
                if data.get("result") == "success":
                    rates = data.get("rates", {})
                    # Add some specific focus currencies if they exist, providing defaults if missing
                    focus_rates = {
                        "ZAR": rates.get("ZAR", 19.0),
                        "GBP": rates.get("GBP", 0.8),
                        "EUR": rates.get("EUR", 0.93),
                        "BWP": rates.get("BWP", 13.5), # Botswana Pula
                        "ZWL": rates.get("ZWL", 322.0) 
                    }
                    # Filter out any lingering Nones just in case
                    focus_rates = {k: v for k, v in focus_rates.items() if v is not None}
                    
                    cls._cache = focus_rates
                    cls._cache_time = current_time
                    return focus_rates

                
        except Exception as e:
            logger.error(f"Failed to fetch live market data: {e}")
            
        return cls._cache or {"ZAR": 19.0, "GBP": 0.8, "EUR": 0.93, "ZWL": 322.0} # Fallback only if complete failure

