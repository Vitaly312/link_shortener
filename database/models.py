from .database import Base
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    original_link: Mapped[str]
    short_link: Mapped[str] = mapped_column(default = lambda: uuid4().hex)
    transitions: Mapped[list["Transition"]] = relationship(back_populates="link")
    access_key: Mapped[str] = mapped_column(default = lambda: uuid4().hex)

class Transition(Base): # переход по ссылке
    __tablename__ = "transitions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    link: Mapped[Link] = relationship(back_populates="transitions")
    link_id: Mapped[int] = mapped_column(ForeignKey("links.id"))

    from_ip: Mapped[str | None] = mapped_column(String(15), nullable=True)
    from_country: Mapped[str | None]
    from_city: Mapped[str | None]
    to_ip: Mapped[str | None] = mapped_column(String(15), nullable=True)
    to_country: Mapped[str | None]
    to_city: Mapped[str | None]
    forwarded_from: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
