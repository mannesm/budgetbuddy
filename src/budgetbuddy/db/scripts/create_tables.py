from sqlalchemy import create_engine

from src.budgetbuddy.db.base import Base
from src.budgetbuddy.db.config import DATABASE_URL

#
# for _, module_name, _ in pkgutil.iter_modules(src.budgetbuddy.db.models.__path__):
#     importlib.import_module(f"{src.budgetbuddy.db.models.__name__}.{module_name}")

engine = create_engine(DATABASE_URL, echo=True)

Base.metadata.create_all(engine)
