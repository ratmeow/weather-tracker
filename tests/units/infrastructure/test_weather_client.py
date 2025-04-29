from decimal import Decimal

import pytest

from weather_tracker.domain.entities import Location
from weather_tracker.domain.value_objects import Coordinates
from weather_tracker.infrastructure.external_api.exceptions import OpenWeatherClientError
from weather_tracker.infrastructure.httpl_client.exceptions import AsyncClientInternalError


@pytest.mark.asyncio
async def test_search_location(open_weather_client):
    location_name = "Moscow"
    locations = await open_weather_client.search_location(name=location_name)

    assert len(locations) > 0
    assert "Moscow" in [loc.name for loc in locations]
    assert "Kazan" not in [loc.name for loc in locations]


@pytest.mark.asyncio
async def test_search_empty_location(open_weather_client):
    location_name = ""
    with pytest.raises(AsyncClientInternalError):
        await open_weather_client.search_location(name=location_name)


@pytest.mark.asyncio
async def test_search_location_open_weather_client_error(open_weather_client):
    location_name = "Ufa"
    with pytest.raises(OpenWeatherClientError):
        await open_weather_client.search_location(name=location_name)


@pytest.mark.asyncio
async def test_get_weather(open_weather_client):
    location = Location.create(name="Moscow", coordinates=Coordinates(Decimal(40), Decimal(60)))

    weather = await open_weather_client.get_weather_by_location(location=location)
    assert weather.name == "Moscow"
    assert weather.temperature is not None


@pytest.mark.asyncio
async def test_get_weather_invalid_params(open_weather_client):
    location = Location.create(name="Moscow", coordinates=Coordinates(Decimal(-40), Decimal(60)))
    with pytest.raises(AsyncClientInternalError):
        await open_weather_client.get_weather_by_location(location=location)


@pytest.mark.asyncio
async def test_get_weather_client_error(open_weather_client):
    location = Location.create(name="Moscow", coordinates=Coordinates(Decimal(60), Decimal(60)))
    with pytest.raises(OpenWeatherClientError):
        await open_weather_client.get_weather_by_location(location=location)
