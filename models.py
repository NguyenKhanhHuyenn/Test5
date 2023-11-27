from sqlalchemy import Column, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = 'profiles'

    MSV = Column(String, ForeignKey('users.username'), primary_key=True, index=True)
    hoten = Column(String)
    ngaysinh = Column(Date)
    gioitinh = Column(String)
    khoa = Column(String)
    nganh = Column(String)
    GPA = Column(Float)
    GVphutrach = Column(String)

    user = relationship("User", back_populates="profile", uselist=False)
    def __init__(self, msv, hoten, ngaysinh, gioitinh, khoa, nganh, gpa, gvphutrach):
        self.MSV = msv
        self.hoten = hoten
        self.ngaysinh = ngaysinh
        self.gioitinh = gioitinh
        self.khoa = khoa
        self.nganh = nganh
        self.GPA = gpa
        self.GVphutrach = gvphutrach
