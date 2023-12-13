from sqlalchemy import Column, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username = Column(String(255), primary_key=True, index=True)
    password = Column(String(255))
    role = Column(String(255))

    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'

    MSV = Column(String(255), ForeignKey('users.username'), primary_key=True, index=True)
    hoten = Column(String(255))
    ngaysinh = Column(Date)
    gioitinh = Column(String(255))
    khoa = Column(String(255))
    nganh = Column(String(255))
    GPA = Column(Float)
    GVphutrach = Column(String(255))

    user = relationship("User", back_populates="profile", uselist=False)
