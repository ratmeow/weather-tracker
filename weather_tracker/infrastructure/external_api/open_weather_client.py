import logging

from weather_tracker.application.dto import LocationDTO
from weather_tracker.application.interfaces import LocationWeatherDTO, WeatherClient
from weather_tracker.config import OpenWeatherConfig
from weather_tracker.domain.entities import Location
from weather_tracker.domain.value_objects import Coordinates

from ..httpl_client.exceptions import AsyncClientInternalError
from ..httpl_client.interfaces import AsyncHTTPClient
from .exceptions import OpenWeatherClientError
from .schemas import OpenWeatherLocationSearchRequest, OpenWeatherLocationWeatherRequest

logger = logging.getLogger(__name__)


class OpenWeatherClient(WeatherClient):
    def __init__(self, async_http_client: AsyncHTTPClient, config: OpenWeatherConfig):
        self.async_http_client = async_http_client
        self.config = config

    async def search_location(self, name: str) -> list[LocationDTO]:
        params = OpenWeatherLocationSearchRequest(q=name, appid=self.config.api_key)

        try:
            response_json = await self.async_http_client.get(url=self.config.search_url, params=params.model_dump())
            result = []
            for item in response_json:
                result.append(
                    LocationDTO(
                        name=item["name"],
                        coordinates=Coordinates(latitude=item["lat"], longitude=item["lon"]),
                        country=item.get("country", None),
                        state=item.get("state", None),
                    )
                )
            return result
        except AsyncClientInternalError as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise OpenWeatherClientError

    async def get_weather_by_location(self, location: Location) -> LocationWeatherDTO:
        params = OpenWeatherLocationWeatherRequest(
            lat=location.coordinates.latitude, lon=location.coordinates.longitude, appid=self.config.api_key
        )

        try:
            response_json = await self.async_http_client.get(url=self.config.weather_url, params=params.model_dump())
            if not isinstance(response_json, dict):
                raise OpenWeatherClientError
            system_info = response_json.get("sys", {})
            main_info = response_json.get("main", {})
            wind_info = response_json.get("wind", {})
            desc_info = response_json.get("weather", [{}])[0] if response_json.get("weather") else {}

            weather = LocationWeatherDTO(
                name=location.name,
                coordinates=location.coordinates,
                country=system_info.get("country"),
                main_state=desc_info.get("main"),
                temperature=main_info.get("temp"),
                temperature_feels=main_info.get("feels_like"),
                wind_speed=wind_info.get("speed"),
                humidity=main_info.get("humidity"),
            )

            return weather
        except AsyncClientInternalError as e:
            raise e
        except Exception as e:
            logger.error(e)
            raise OpenWeatherClientError
