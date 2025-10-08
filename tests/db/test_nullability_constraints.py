import uuid
from datetime import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.db.repository.base import CRUDRepository
from src.db.schema.base import DEFAULT_SCHEMA, Base


def _dummy_value_for_column(col):
    """Return a sensible dummy value for a SQLAlchemy Column object."""
    t = col.type.__class__.__name__.lower()
    if "uuid" in t:
        return uuid.uuid4()
    if "integer" in t or "int" in t:
        return 1
    if "float" in t or "numeric" in t or "decimal" in t:
        return 1.0
    if "boolean" in t:
        return True
    if "date" in t or "time" in t:
        return datetime.now(datetime.UTC)
    return "x"


@pytest.mark.integration
def test_model_metadata_matches_db_nullability(test_engine):
    """Ensure the SQLAlchemy model column.nullable matches the actual DB column nullability.

    This detects the case where your ORM declares nullable=False but the real DB still allows NULL
    (e.g., because the column was created earlier without the NOT NULL constraint).
    """
    inspector = inspect(test_engine)

    mismatches = []

    for _table_name, table_obj in Base.metadata.tables.items():
        # SQLAlchemy tables may include schema in the Table key; split if necessary
        schema = table_obj.schema or DEFAULT_SCHEMA
        # Remove schema prefix if present in table_name key
        name = table_obj.name

        try:
            cols = inspector.get_columns(name, schema=schema)
        except Exception:
            # If the inspector can't see the table, record mismatch
            mismatches.append((name, "table-not-found", None, None))
            continue

        # make a map of db column -> nullable
        db_nullable = {c["name"]: c.get("nullable") for c in cols}

        for col in table_obj.columns:
            model_nullable = bool(col.nullable)
            db_col_nullable = db_nullable.get(col.name)
            # If DB doesn't know this column, consider it a mismatch
            if db_col_nullable is None:
                mismatches.append((name, col.name, model_nullable, "missing-in-db"))
                continue
            if model_nullable != db_col_nullable:
                mismatches.append((name, col.name, model_nullable, db_col_nullable))

    if mismatches:
        details = "\n".join(f"Table {t} Column {c}: model nullable={m} vs db nullable={d}" for t, c, m, d in mismatches)
        pytest.fail(f"Found nullability mismatches between model metadata and DB:\n{details}")


@pytest.mark.integration
def test_db_enforces_not_null_columns(db_session: Session):
    """For each model table, attempt to insert NULL into each non-nullable column and expect DB to reject it.

    We construct minimal payloads for the model using sensible dummy values for required columns and
    then set the target column to None. The repository's create() method commits, so an IntegrityError
    should be raised if the DB enforces NOT NULL.
    """
    failures = []

    # Iterate model classes from metadata: map table name to ORM class via registry
    mapper_registry = Base.registry
    # Base.metadata.tables gives Table objects keyed by schema.table or table name
    for table_obj in Base.metadata.tables.values():
        # find ORM class mapped to this table
        mapped_class = None
        for cls in mapper_registry.mappers:
            if cls.local_table is table_obj:
                mapped_class = cls.class_
                break
        if mapped_class is None:
            # No mapped class (maybe an auxiliary table), skip
            continue

        repo = CRUDRepository(mapped_class)

        # find columns that are non-nullable and that have no server_default and are not PK autoinc
        required_cols = []
        for col in table_obj.columns:
            if col.primary_key:
                continue
            if col.nullable:
                continue
            if col.server_default is not None:
                continue
            if col.default is not None:
                continue
            # column considered required and should be provided by user
            required_cols.append(col)

        if not required_cols:
            continue

        # Build base payload with dummy values for all required columns
        base_payload = {}
        for col in table_obj.columns:
            if col.primary_key:
                continue
            if col.name in [c.name for c in required_cols]:
                base_payload[col.name] = _dummy_value_for_column(col)
            else:
                # For optional columns, skip unless they have server defaults (server default will apply)
                continue

        # Try each required column by setting it to None and expecting IntegrityError
        for target in required_cols:
            payload = dict(base_payload)
            payload[target.name] = None
            try:
                repo.create(db_session, payload)
            except IntegrityError:
                # Expected: DB enforced NOT NULL
                # Rollback the session's inner state to continue safely
                db_session.rollback()
                continue
            except Exception as exc:
                # Unexpected exception: record it
                db_session.rollback()
                failures.append((table_obj.name, target.name, f"unexpected-exception: {exc!r}"))
            else:
                # If no exception raised, DB allowed a NULL where model expected non-nullable
                db_session.rollback()
                failures.append((table_obj.name, target.name, "no-integrity-error"))

    if failures:
        details = "\n".join(f"{t}.{c}: {msg}" for t, c, msg in failures)
        pytest.fail("Database does not enforce NOT NULL for some required columns (or unexpected errors):\n" + details)
