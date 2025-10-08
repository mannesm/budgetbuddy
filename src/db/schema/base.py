from typing import Any

from sqlalchemy import MetaData, inspect
from sqlalchemy.orm import DeclarativeBase, declared_attr
from src.db.config import NAMING_CONVENTION
from src.db.mixins.timestamp import TimestampMixin
from src.db.mixins.uuid_pk import UUIDPrimaryKeyMixin

DEFAULT_SCHEMA = "budgetbuddy"


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __table_args__(cls) -> dict:
        return {"schema": DEFAULT_SCHEMA}

    # 3) Pretty repr for easier debugging/logging
    def __repr__(self) -> str:
        cols = []
        insp = inspect(self).mapper.column_attrs
        for attr in insp:
            name = attr.key
            val = getattr(self, name, None)
            cols.append(f"{name}={val!r}")
        return f"<{self.__class__.__name__} {' '.join(cols)}>"

    # 4) Handy serializer for quick debugging / JSON responses
    def to_dict(self) -> dict[str, Any]:
        insp = inspect(self).mapper.column_attrs
        return {attr.key: getattr(self, attr.key) for attr in insp}


class ModelBase(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __abstract__ = True
