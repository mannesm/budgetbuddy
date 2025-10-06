from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class CRUDRepository[T]:
    def __init__(self, model: type[T]):
        self.model = model

    def get(self, db: Session, itemid: Any) -> T | None:
        return db.get(self.model, itemid)

    def list(self, db: Session, *, offset: int = 0, limit: int = 100) -> Sequence[T]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def create(self, db: Session, obj_in: dict[str, Any]) -> T:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_many(self, db: Session, objs_in: Iterable[dict[str, Any]]) -> Sequence[T]:
        db_objs = [self.model(**data) for data in objs_in]
        db.add_all(db_objs)
        db.commit()
        for o in db_objs:
            db.refresh(o)
        return db_objs

    def update(self, db: Session, db_obj: T, obj_in: dict[str, Any]) -> T:
        for k, v in obj_in.items():
            setattr(db_obj, k, v)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: T) -> None:
        db.delete(db_obj)
        db.commit()
