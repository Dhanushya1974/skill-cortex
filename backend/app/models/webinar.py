from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Webinar(Base):
    __tablename__ = "webinars"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    price = Column(Float, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="webinars")
    slots = relationship("Slot", back_populates="webinar", cascade="all, delete-orphan")
