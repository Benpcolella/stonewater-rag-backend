#!/usr/bin/env python3
"""
Response Formatter
Converts structured query results into clean, user-friendly formats
"""

def format_metric_name(metric: str) -> str:
    """Convert metric path to readable name"""
    aliases = {
        'cap_rate': 'Cap Rate',
        'cap_rate_exit': 'Exit Cap Rate',
        'cap_rate_going_in': 'Going-In Cap Rate',
        'irr': 'Levered IRR',
        'levered_irr': 'Levered IRR',
        'equity_multiple': 'Equity Multiple',
        'ltc': 'LTC %',
        'interest_rate': 'Interest Rate',
        'loan_amount': 'Loan Amount',
        'units': 'Units',
        'total_units': 'Total Units',
    }

    # Check if it's an alias
    for alias, name in aliases.items():
        if alias in metric.lower():
            return name

    # If it's a full path, extract the last part
    if '.' in metric:
        return metric.split('.')[-1].replace('_', ' ').title()

    return metric.replace('_', ' ').title()


def format_by_state(query_result: dict) -> str:
    """Format state-level query results"""
    data = query_result.get('data', {})
    state = data.get('state', 'Unknown')
    metric = data.get('metric', 'Metric')
    results = data.get('results', [])

    metric_name = format_metric_name(metric)
    intro = f"Here are the {metric_name.lower()} we've seen in {state}"

    if not results:
        return f"{intro}:\n  None found"

    lines = [f"{intro}:"]
    for r in results:
        deal_name = r.get('deal', 'Unknown')
        city = r.get('city', '')
        value = r.get('value', 'N/A')
        lines.append(f"  • {deal_name} ({city}): {value}")

    return '\n'.join(lines)


def format_by_city(query_result: dict) -> str:
    """Format city-level query results"""
    data = query_result.get('data', {})
    city = data.get('city', 'Unknown')
    state = data.get('state', 'Unknown')
    metric = data.get('metric', 'Metric')
    results = data.get('results', [])

    metric_name = format_metric_name(metric)
    if state and state != 'All':
        intro = f"Here are the {metric_name.lower()} we've seen in {city}, {state}"
    else:
        intro = f"Here are the {metric_name.lower()} we've seen in {city}"

    if not results:
        return f"{intro}:\n  None found"

    lines = [f"{intro}:"]
    for r in results:
        deal_name = r.get('deal', 'Unknown')
        value = r.get('value', 'N/A')
        lines.append(f"  • {deal_name}: {value}")

    return '\n'.join(lines)


def format_search(query_result: dict) -> str:
    """Format search results"""
    if query_result.get('status') == 'no_match':
        query = query_result.get('query', 'your search')
        return f"No deals found matching \"{query}\""

    data = query_result.get('data', {})
    deal_name = query_result.get('matched_deal', 'Unknown')

    lines = [f"**{deal_name}**\n"]

    # Property info
    prop = data.get('property', {})
    lines.append("PROPERTY:")
    lines.append(f"  Location: {data.get('location', 'N/A')}")
    lines.append(f"  Market: {data.get('market', 'N/A')}")
    lines.append(f"  Units: {prop.get('units', 'N/A')}")
    lines.append(f"  Rentable SF: {prop.get('rentable_sf', 'N/A')}")
    lines.append("")

    # Financing
    fin = data.get('financing', {})
    lines.append("FINANCING:")
    lines.append(f"  Loan Amount: {fin.get('loan_amount', 'N/A')}")
    lines.append(f"  LTC: {fin.get('ltc_percent', 'N/A')}")
    lines.append(f"  Interest Rate: {fin.get('interest_rate', 'N/A')}")
    lines.append("")

    # Returns
    ret = data.get('returns', {})
    lines.append("RETURNS:")
    lines.append(f"  Levered IRR: {ret.get('levered_irr', 'N/A')}")
    lines.append(f"  Equity Multiple: {ret.get('equity_multiple', 'N/A')}")
    lines.append(f"  Exit Cap Rate: {ret.get('cap_rate_exit', 'N/A')}")
    lines.append(f"  Going-In Cap Rate: {ret.get('cap_rate_going_in', 'N/A')}")

    return '\n'.join(lines)


def format_comparison(query_result: dict) -> str:
    """Format comparison results as a clean table"""
    data = query_result.get('data', {})
    results = data.get('results', [])
    location = query_result.get('location', 'Deals')
    metrics_str = query_result.get('metrics', '')

    if not results:
        return f"No deals found in {location}"

    lines = [f"**Deal Comparison - {location}**\n"]

    # Build table
    headers = ['Deal', 'Location'] + metrics_str.split(',')
    lines.append(" | ".join(headers))
    lines.append("-" * (len(" | ".join(headers))))

    for r in results:
        row = [r.get('deal', 'Unknown'), r.get('location', 'Unknown')]
        for metric in metrics_str.split(','):
            metric = metric.strip()
            # Try to find metric in results
            value = None
            for key, val in r.items():
                if metric in key.lower() or metric in str(key).lower():
                    value = val
                    break
            row.append(value or 'N/A')
        lines.append(" | ".join(str(x) for x in row))

    return '\n'.join(lines)


def format_deal_metrics(query_result: dict) -> str:
    """Format deal metrics results"""
    data = query_result.get('data', {})
    deal_name = query_result.get('deal', 'Unknown')
    metrics_requested = query_result.get('metrics_requested', '')

    lines = [f"**{deal_name}**\n"]
    lines.append(f"Metrics Requested: {metrics_requested}\n")

    for key, value in data.items():
        if key == 'deal':
            continue
        metric_name = format_metric_name(key)
        lines.append(f"  {metric_name}: {value}")

    return '\n'.join(lines)


def format_response(query_result: dict, response_type: str = 'auto') -> str:
    """
    Format a query result based on type
    Auto-detects type if not specified
    """
    status = query_result.get('status', 'error')

    if status == 'error':
        return f"Error: {query_result.get('error', 'Unknown error')}"

    if response_type == 'auto':
        # Auto-detect based on query result structure
        if 'data' in query_result:
            data = query_result['data']
            if 'results' in data:
                # Check the structure of results
                if data['results'] and isinstance(data['results'][0], dict):
                    first_result = data['results'][0]
                    if 'state' in first_result and 'value' in first_result:
                        response_type = 'by_state'
                    elif 'location' in first_result and 'value' in first_result:
                        response_type = 'by_city'

        if 'matched_deal' in query_result:
            response_type = 'search'
        elif 'metrics_requested' in query_result:
            response_type = 'deal_metrics'
        elif 'location' in query_result and 'metrics' in query_result:
            response_type = 'comparison'

    # Format based on detected type
    if response_type == 'by_state':
        return format_by_state(query_result)
    elif response_type == 'by_city':
        return format_by_city(query_result)
    elif response_type == 'search':
        return format_search(query_result)
    elif response_type == 'comparison':
        return format_comparison(query_result)
    elif response_type == 'deal_metrics':
        return format_deal_metrics(query_result)
    else:
        # Fallback to JSON
        import json
        return json.dumps(query_result, indent=2)
