#!/usr/bin/env python3
"""
Structured Deal Query Engine
Provides filtered, fuzzy-searchable access to deals database
"""

import json
from typing import List, Dict, Any, Optional

# Try to import fuzzywuzzy, fall back to basic string matching if not available
try:
    from fuzzywuzzy import fuzz, process
    HAS_FUZZYWUZZY = True
except ImportError:
    HAS_FUZZYWUZZY = False
    # Provide basic string matching fallback
    class SimpleFuzz:
        @staticmethod
        def token_set_ratio(a, b):
            """Simple string similarity (0-100)"""
            a_lower = a.lower()
            b_lower = b.lower()
            if a_lower == b_lower:
                return 100
            if a_lower in b_lower or b_lower in a_lower:
                return 80
            return 0

    class SimpleProcess:
        @staticmethod
        def extractOne(query, choices, scorer=None):
            """Find best matching choice"""
            if scorer is None:
                scorer = SimpleFuzz.token_set_ratio
            best_match = None
            best_score = 0
            for choice in choices:
                score = scorer(query, choice)
                if score > best_score:
                    best_score = score
                    best_match = choice
            return (best_match, best_score) if best_match else (None, 0)

    fuzz = SimpleFuzz()
    process = SimpleProcess()

class DealQueryEngine:
    """Query deals with filtering, fuzzy search, and structured responses"""

    def __init__(self, deals_db_path: str):
        """Initialize with deals database"""
        self.deals = {}
        self.load_deals(deals_db_path)
        self._build_indices()

    def load_deals(self, path: str):
        """Load deals from JSON database"""
        try:
            with open(path, 'r') as f:
                self.deals = json.load(f)
        except Exception as e:
            print(f"Error loading deals: {e}")
            self.deals = {}

    def _build_indices(self):
        """Build search indices for fuzzy matching"""
        self.deal_names = list(self.deals.keys())
        self.locations = []
        self.states = set()
        self.cities = set()

        for deal_name, deal_data in self.deals.items():
            prop = deal_data.get('property_information', {})
            location = prop.get('address', '')
            state = prop.get('state', '')
            city = prop.get('city', '')

            if location:
                self.locations.append(location)
            if state:
                self.states.add(state)
            if city:
                self.cities.add(city)

    def fuzzy_search_deal(self, query: str, threshold: int = 70) -> Optional[str]:
        """
        Fuzzy search for a deal by name or location
        Returns best matching deal name or None
        """
        if not query:
            return None

        # Try exact match first
        if query in self.deals:
            return query

        # Fuzzy match on deal names
        match, score = process.extractOne(query, self.deal_names, scorer=fuzz.token_set_ratio)
        if score >= threshold:
            return match

        # Fuzzy match on locations
        for deal_name, deal_data in self.deals.items():
            prop = deal_data.get('property_information', {})
            location = prop.get('address', '')
            city = prop.get('city', '')

            # Check both location and city
            for text in [location, city]:
                if text:
                    similarity = fuzz.token_set_ratio(query.lower(), text.lower())
                    if similarity >= threshold:
                        return deal_name

        return None

    def get_deals_by_state(self, state: str) -> List[str]:
        """Get all deal names in a state (case-insensitive)"""
        state = state.upper()
        return [
            name for name, data in self.deals.items()
            if data.get('property_information', {}).get('state', '').upper() == state
        ]

    def get_deals_by_city(self, city: str) -> List[str]:
        """Get all deal names in a city (fuzzy match)"""
        return [
            name for name, data in self.deals.items()
            if fuzz.token_set_ratio(city.lower(),
                                   data.get('property_information', {}).get('city', '').lower()) > 70
        ]

    def format_metric(self, value: Any) -> str:
        """Format metric value for display"""
        if value is None:
            return "N/A"
        if isinstance(value, str):
            return value
        if isinstance(value, (int, float)):
            return str(value)
        return str(value)

    def extract_metric(self, deal_data: Dict, metric: str) -> Any:
        """
        Extract a specific metric from deal data
        Supports nested access: "construction_financing.loan_amount"
        """
        parts = metric.split('.')
        value = deal_data

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None

        # Handle nested dict values (like {'total': '...', 'total_numeric': ...})
        if isinstance(value, dict) and 'total' in value:
            return value.get('total')
        elif isinstance(value, dict) and 'percent' in value:
            return value.get('percent')

        return value

    def query_metric(self, metric: str, state: Optional[str] = None,
                     city: Optional[str] = None) -> Dict[str, Any]:
        """
        Query a specific metric across deals
        Optional filters by state and/or city
        """
        results = []

        for deal_name, deal_data in self.deals.items():
            prop = deal_data.get('property_information', {})

            # Apply filters
            if state and prop.get('state', '').upper() != state.upper():
                continue
            if city and fuzz.token_set_ratio(city.lower(), prop.get('city', '').lower()) <= 70:
                continue

            # Extract metric
            value = self.extract_metric(deal_data, metric)
            if value is not None:
                results.append({
                    'deal': deal_name,
                    'location': prop.get('address', prop.get('city', 'N/A')),
                    'city': prop.get('city', ''),
                    'state': prop.get('state', ''),
                    'value': self.format_metric(value),
                    'metric': metric
                })

        return {
            'metric': metric,
            'state': state or 'All',
            'city': city or 'All',
            'count': len(results),
            'results': sorted(results, key=lambda x: x['location'])
        }

    def compare_metrics(self, metrics: List[str], deal_names: Optional[List[str]] = None,
                       state: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare multiple metrics across deals
        """
        # Filter deals if needed
        if deal_names:
            deals_to_compare = {k: v for k, v in self.deals.items() if k in deal_names}
        elif state:
            deals_to_compare = {k: v for k, v in self.deals.items()
                               if v.get('property_information', {}).get('state', '').upper() == state.upper()}
        else:
            deals_to_compare = self.deals

        results = []
        for deal_name, deal_data in deals_to_compare.items():
            prop = deal_data.get('property_information', {})
            row = {
                'deal': deal_name,
                'location': prop.get('address', prop.get('city', 'N/A')),
                'city': prop.get('city', ''),
                'state': prop.get('state', ''),
            }

            # Add each metric
            for metric in metrics:
                value = self.extract_metric(deal_data, metric)
                row[metric] = self.format_metric(value)

            results.append(row)

        return {
            'metrics': metrics,
            'count': len(results),
            'results': results
        }

    def get_deal_summary(self, deal_name: str) -> Optional[Dict[str, Any]]:
        """Get formatted summary of a deal"""
        deal_name = self.fuzzy_search_deal(deal_name) or deal_name

        if deal_name not in self.deals:
            return None

        deal = self.deals[deal_name]
        prop = deal.get('property_information', {})
        fin = deal.get('construction_financing', {})
        ret = deal.get('project_returns', {})
        fin_sum = deal.get('financial_summary', {})

        return {
            'name': deal_name,
            'location': prop.get('address', 'N/A'),
            'market': prop.get('market', 'N/A'),
            'underwriting_date': prop.get('underwriting_date', 'N/A'),
            'property': {
                'units': prop.get('total_units', 'N/A'),
                'rentable_sf': prop.get('rentable_sf', 'N/A'),
                'gross_sf': prop.get('gross_sf', 'N/A'),
                'parking': prop.get('parking_spaces', 'N/A'),
            },
            'financing': {
                'loan_amount': fin.get('loan_amount', 'N/A'),
                'ltc_percent': fin.get('ltc_percent', 'N/A'),
                'interest_rate': fin.get('interest_rate_percent', 'N/A'),
            },
            'returns': {
                'levered_irr': ret.get('levered_irr_percent', 'N/A'),
                'equity_multiple': ret.get('levered_equity_multiple', 'N/A'),
                'cap_rate_exit': ret.get('exit_cap_rate_percent', 'N/A'),
                'cap_rate_going_in': ret.get('yield_on_cost_percent', 'N/A'),
            },
            'costs': {
                'total': fin_sum.get('total_cost', {}).get('total', 'N/A'),
                'hard_costs': fin_sum.get('hard_costs', {}).get('total', 'N/A'),
                'soft_costs': fin_sum.get('soft_costs', {}).get('total', 'N/A'),
                'land_costs': fin_sum.get('land_costs', {}).get('total', 'N/A'),
            }
        }

    def get_metrics_available(self) -> List[str]:
        """Get list of all available metrics"""
        return [
            'property_information.project_name',
            'property_information.address',
            'property_information.market',
            'property_information.total_units',
            'property_information.rentable_sf',
            'property_information.gross_sf',
            'construction_financing.loan_amount',
            'construction_financing.ltc_percent',
            'construction_financing.interest_rate_percent',
            'project_returns.levered_irr_percent',
            'project_returns.levered_equity_multiple',
            'project_returns.exit_cap_rate_percent',
            'project_returns.yield_on_cost_percent',
            'financial_summary.total_cost.total',
        ]


# Common metric aliases for easier querying
METRIC_ALIASES = {
    'cap_rate': 'project_returns.exit_cap_rate_percent',
    'cap_rate_exit': 'project_returns.exit_cap_rate_percent',
    'cap_rate_going_in': 'project_returns.yield_on_cost_percent',
    'irr': 'project_returns.levered_irr_percent',
    'levered_irr': 'project_returns.levered_irr_percent',
    'equity_multiple': 'project_returns.levered_equity_multiple',
    'loan_amount': 'construction_financing.loan_amount',
    'ltc': 'construction_financing.ltc_percent',
    'interest_rate': 'construction_financing.interest_rate_percent',
    'units': 'property_information.total_units',
    'total_units': 'property_information.total_units',
    'rentable_sf': 'property_information.rentable_sf',
    'gross_sf': 'property_information.gross_sf',
    'total_cost': 'financial_summary.total_cost.total',
    'market': 'property_information.market',
    'address': 'property_information.address',
}


def resolve_metric_alias(metric: str) -> str:
    """Resolve metric aliases to full paths"""
    return METRIC_ALIASES.get(metric.lower(), metric)
