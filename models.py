from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Station(Base):
    __tablename__ = "station"

    number: Mapped[int] = mapped_column(Integer, primary_key=True)
    contract_name: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    # 是否支持现场银行卡/信用卡支付 (JCDecaux API: banking)。0=不支持，1=支持
    banking: Mapped[bool] = mapped_column(Boolean, comment="是否支持现场银行卡/信用卡支付；0=不支持，1=支持")
    # 是否为奖励站点，如还车可获额外时长等 (JCDecaux API: bonus)。0=否，1=是
    bonus: Mapped[bool] = mapped_column(Boolean, comment="是否为奖励站点（还车可获额外时长等）；0=否，1=是")
    bike_stands: Mapped[int] = mapped_column(Integer)

    availabilities: Mapped[list[Availability]] = relationship(
        "Availability",
        back_populates="station",
        cascade="all, delete",
    )


class Availability(Base):
    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[int] = mapped_column(ForeignKey("station.number"), nullable=False)
    available_bikes: Mapped[int] = mapped_column(Integer)
    available_bike_stands: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    last_update: Mapped[int] = mapped_column(BigInteger)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    # 数据请求的时间（抓取该条记录时的时间）
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, comment="数据请求的时间")

    station: Mapped[Station] = relationship("Station", back_populates="availabilities")
