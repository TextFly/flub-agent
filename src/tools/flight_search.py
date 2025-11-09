"""
Flight Search Tool

Provides flight search functionality using the fast-flights library.
Converted from fast-flights-mcp to be a direct tool.
"""

from typing import Dict, Any
from datetime import datetime
import re
from fast_flights import FlightData, Passengers, Result, get_flights


def parse_price(price_str: str) -> int:
    """Parse price string like '$121' or '$$121' to integer."""
    try:
        return int(price_str.replace('$', '').replace(',', ''))
    except:
        return 0


def parse_duration(duration_str: str) -> int:
    """Parse duration string like '1 hr 34 min' to total minutes."""
    try:
        hours = 0
        minutes = 0

        hour_match = re.search(r'(\d+)\s*hr', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))

        min_match = re.search(r'(\d+)\s*min', duration_str)
        if min_match:
            minutes = int(min_match.group(1))

        return hours * 60 + minutes
    except:
        return 0


def calculate_price_range(flights: list) -> Dict[str, Any]:
    """Calculate price range from flight list."""
    if not flights:
        return {"min": 0, "max": 0, "average": 0}

    prices = [parse_price(f.price) for f in flights]
    return {
        "min": min(prices),
        "max": max(prices),
        "average": round(sum(prices) / len(prices), 2)
    }


def search_flights(
    date: str,
    from_airport: str,
    to_airport: str,
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Search for flights between two airports on a specific date.

    Args:
        date: Flight date in YYYY-MM-DD format (e.g., "2025-01-01")
        from_airport: Departure airport code (e.g., "TPE", "LAX", "JFK", "EWR")
        to_airport: Arrival airport code (e.g., "MYJ", "SFO", "LHR", "LAX")
        adults: Number of adult passengers (default: 1)
        children: Number of child passengers (default: 0)
        infants_in_seat: Number of infants in seat (default: 0)
        infants_on_lap: Number of infants on lap (default: 0)
        max_results: Maximum number of flights to return (default: 10)

    Returns:
        Dictionary with flight search results including price, flight details, and metadata
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")

        # Create flight data and passengers objects
        flight_data = FlightData(
            date=date,
            from_airport=from_airport.upper(),
            to_airport=to_airport.upper()
        )

        passengers = Passengers(
            adults=adults,
            children=children,
            infants_in_seat=infants_in_seat,
            infants_on_lap=infants_on_lap
        )

        # Get flights using the API
        result: Result = get_flights(
            flight_data=[flight_data],
            trip='one-way',
            passengers=passengers,
            seat='economy'
        )

        # Format response
        flights_list = []
        for i, flight in enumerate(result.flights[:max_results]):
            flight_info = {
                "rank": i + 1,
                "name": flight.name,
                "departure": flight.departure,
                "arrival": flight.arrival,
                "departure_time_ahead": getattr(flight, 'departure_time_ahead', None),
                "arrival_time_ahead": getattr(flight, 'arrival_time_ahead', None),
                "duration": flight.duration,
                "stops": flight.stops,
                "price": flight.price,
                "is_best": flight.is_best,
            }

            if hasattr(flight, 'delay'):
                flight_info['delay'] = flight.delay

            flights_list.append(flight_info)

        price_range = calculate_price_range(result.flights)

        return {
            "success": True,
            "query": {
                "date": date,
                "from": from_airport.upper(),
                "to": to_airport.upper(),
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants_in_seat": infants_in_seat,
                    "infants_on_lap": infants_on_lap
                }
            },
            "current_price_indicator": result.current_price,
            "price_range": price_range,
            "total_flights": len(result.flights),
            "flights_returned": len(flights_list),
            "flights": flights_list
        }

    except ValueError as e:
        return {"success": False, "error": f"Invalid date format. Use YYYY-MM-DD: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Flight search failed: {str(e)}"}


def find_best_price(
    date: str,
    from_airport: str,
    to_airport: str,
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0
) -> Dict[str, Any]:
    """
    Find the cheapest flight option for a given route and date.

    Args:
        date: Flight date in YYYY-MM-DD format
        from_airport: Departure airport code
        to_airport: Arrival airport code
        adults: Number of adult passengers (default: 1)
        children: Number of child passengers (default: 0)
        infants_in_seat: Number of infants in seat (default: 0)
        infants_on_lap: Number of infants on lap (default: 0)

    Returns:
        Dictionary with the cheapest flight details and pricing information
    """
    try:
        flight_data = FlightData(
            date=date,
            from_airport=from_airport.upper(),
            to_airport=to_airport.upper()
        )

        passengers = Passengers(
            adults=adults,
            children=children,
            infants_in_seat=infants_in_seat,
            infants_on_lap=infants_on_lap
        )

        result: Result = get_flights(
            flight_data=[flight_data],
            trip='one-way',
            passengers=passengers,
            seat='economy'
        )

        if not result.flights:
            return {"success": False, "error": "No flights found"}

        cheapest_flight = min(result.flights, key=lambda f: parse_price(f.price))

        return {
            "success": True,
            "query": {
                "date": date,
                "from": from_airport.upper(),
                "to": to_airport.upper()
            },
            "cheapest_flight": {
                "name": cheapest_flight.name,
                "departure": cheapest_flight.departure,
                "arrival": cheapest_flight.arrival,
                "duration": cheapest_flight.duration,
                "stops": cheapest_flight.stops,
                "price": cheapest_flight.price,
                "is_best": cheapest_flight.is_best
            },
            "price_comparison": {
                "current_price_indicator": result.current_price,
                "price_range": calculate_price_range(result.flights),
                "cheapest_price": cheapest_flight.price,
                "average_price": round(sum(parse_price(f.price) for f in result.flights) / len(result.flights), 2)
            }
        }

    except Exception as e:
        return {"success": False, "error": f"Failed to find best price: {str(e)}"}
