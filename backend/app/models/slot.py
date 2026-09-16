from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship

from app.database import Base


class Slot(Base):
    __tablename__ = "slots"

    id = Column(Integer, primary_key=True)
    webinar_id = Column(Integer, ForeignKey("webinars.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    webinar = relationship("Webinar", back_populates="slots")
