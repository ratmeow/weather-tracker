from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from weather_tracker.application.interfaces import LocationGateway, UserGateway
from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.value_objects import Coordinates

from .orm_models import LocationORM, UserLocationORM, UserORM


class PgOrmUserGateway(UserGateway):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_login(self, login: str) -> Optional[User]:
        query = select(UserORM).filter_by(login=login)
        result: UserORM | None = await self.session.scalar(query)
        if result:
            return User.create(id_=result.id, login=result.login, hashed_password=result.hashed_password)
        return None

    async def find_by_id(self, user_id: UUID, load_locations: bool = False) -> Optional[User]:
        result = await self.session.get(UserORM, user_id)
        if result:
            user = User.create(id_=result.id, login=result.login, hashed_password=result.hashed_password)
            if load_locations:
                query = (
                    select(LocationORM)
                    .join(UserLocationORM, LocationORM.id == UserLocationORM.location_id)
                    .where(UserLocationORM.user_id == user_id)
                )
                raw_locations = await self.session.scalars(query)
                for raw_loc in raw_locations:
                    user.add_location(
                        Location.create(
                            name=raw_loc.name,
                            id_=raw_loc.id,
                            coordinates=Coordinates(longitude=raw_loc.longitude, latitude=raw_loc.latitude),
                        )
                    )
            return user
        return None

    async def save(self, user: User) -> None:
        exists_user = await self.session.get(UserORM, user.id)
        if not exists_user:
            self.session.add(UserORM(id=user.id, login=user.login, hashed_password=user.hashed_password))

        query = select(UserLocationORM.location_id).filter_by(user_id=user.id)
        locations_db = set(await self.session.scalars(query))
        current_locations = set([loc.id for loc in user.locations])

        loc_to_remove = locations_db - current_locations
        loc_to_add = current_locations - locations_db

        if len(loc_to_remove) > 0:
            delete_query = delete(UserLocationORM).where(UserLocationORM.location_id.in_(loc_to_remove))
            await self.session.execute(delete_query)

        if len(loc_to_add) > 0:
            new_locations = [UserLocationORM(user_id=user.id, location_id=loc_id) for loc_id in loc_to_add]
            self.session.add_all(new_locations)


class PgOrmLocationGateway(LocationGateway):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, location: Location) -> None:
        new_location = LocationORM(
            id=location.id,
            name=location.name,
            latitude=location.coordinates.latitude,
            longitude=location.coordinates.longitude,
        )

        self.session.add(new_location)

    async def get_by_coords(self, coordinates: Coordinates) -> Optional[Location]:
        query = select(LocationORM).filter_by(latitude=coordinates.latitude, longitude=coordinates.longitude)
        result = await self.session.scalar(query)
        if result:
            return Location(
                id=result.id,
                name=result.name,
                coordinates=Coordinates(latitude=result.latitude, longitude=result.longitude),
            )

        return None
