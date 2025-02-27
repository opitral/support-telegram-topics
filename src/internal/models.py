from datetime import datetime
from enum import Enum
from typing import cast

from sqlalchemy import Integer, String, Enum as SqlEnum, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from pkg.database import Base


class Role(Enum):
    CLIENT = "client"
    ADMIN = "admin"
    OPERATOR = "operator"


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[str] = mapped_column(String(64), nullable=True)
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    role: Mapped[Role] = mapped_column(SqlEnum(Role), nullable=False, default=Role.CLIENT)
    registered_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return (f"<User "
                f"id={self.id}, "
                f"telegram_id={self.telegram_id}, "
                f"username={self.username}, "
                f"first_name={self.first_name}, "
                f"last_name={self.last_name}, "
                f"role={self.role}, "
                f"registered_at={cast(datetime, self.registered_at).strftime('%Y-%m-%d %H:%M')}>")
