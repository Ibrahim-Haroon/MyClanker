import json
import re
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class BusinessInfo:
    number: Optional[str]
    hours: Optional[str]
    stars: Optional[float]
    price_range: Optional[str]


@dataclass
class BusinessDirectory:
    businesses: Dict[str, BusinessInfo]


class SearchParserService:
    @staticmethod
    def _clean_str(v: Any) -> Optional[str]:
        if v is None:
            return None
        t = str(v).strip()
        return t or None

    @staticmethod
    def _clean_stars(v: Any) -> Optional[float]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        m = re.search(r"[\d.]+", str(v))  # e.g., "4.5 stars"
        return float(m.group(0)) if m else None

    def clean(self, web_results: str) -> BusinessDirectory:
        s = web_results.strip()
        # Strip code fences if present
        if s.startswith("```") and s.endswith("```"):
            s = s[3:-3].strip()
        # If it's a log/print wrapper, try to slice out the outermost JSON object
        if not s.startswith("{"):
            i, j = s.find("{"), s.rfind("}")
            if i != -1 and j != -1 and j > i:
                s = s[i:j + 1]
        try:
            obj = json.loads(s)
        except json.JSONDecodeError as e:
            raise ValueError(f"Could not parse JSON from response: {e}") from e

        businesses: Dict[str, BusinessInfo] = {}
        for name, data in obj.items():
            if not isinstance(data, dict):
                continue
            number = data.get("number") or data.get("phone") or data.get("phone_number")
            hours = data.get("hours") or data.get("opening_hours")
            stars = data.get("stars") or data.get("rating")
            price = data.get("price_range") or data.get("price") or data.get("priceRange")

            businesses[name] = BusinessInfo(
                number=self._clean_str(number),
                hours=self._clean_str(hours),
                stars=self._clean_stars(stars),
                price_range=self._clean_str(price),
            )

        return BusinessDirectory(businesses=businesses)
