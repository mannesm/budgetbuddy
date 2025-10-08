from datetime import datetime

from sqlalchemy import DateTime, text
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    createdtimestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updatedtimestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=text("CURRENT_TIMESTAMP"),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
