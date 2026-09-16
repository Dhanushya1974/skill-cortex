from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True, nullable=False)
    description = Column(String(500))
    is_active = Column(Boolean, default=True, nullable=False)

    users = relationship("User", back_populates="department")
    webinars = relationship("Webinar", back_populates="department")
