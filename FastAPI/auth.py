from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import User, Profile
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'e5cbb89fb62e43b61c183867934252e3'
ALGORITHM = 'HS256'

o2auth_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    MSV: str
    password: str
    role: str  # Add role to CreateUserRequest

class Token(BaseModel):
    access_token: str
    token_type: str

class CreateProfileRequest(BaseModel):
    MSV: str
    hoten: str
    ngaysinh: str
    gioitinh: str
    khoa: str
    nganh: str
    GPA: float
    GVphutrach: str

class UpdateProfileRequest(BaseModel):
    hoten: str
    ngaysinh: str
    gioitinh: str
    khoa: str
    nganh: str
    GPA: float
    GVphutrach: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: Annotated[str, Depends(o2auth_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        role: str = payload.get('role')
        if username is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {'username': username, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

db_dependency = Annotated[Session, Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = User(
        username=create_user_request.MSV,
        password=create_user_request.password,
        role=create_user_request.role  # Set the role from the request
    )
    db.add(create_user_model)
    db.commit()

@router.post("/token/", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    token = create_access_token(user.username, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}

@router.get("/view-all-profiles")
async def get_all_profiles(
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied. Only admin can view all profiles.'
        )

    profiles = db.query(Profile).all()
    return profiles

@router.get("/view-my-profile")
async def view_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Assuming the current_user is a student, you can get their MSV (username)
    msv = current_user['username']

    # Retrieve the profile of the current user (student)
    user_profile = db.query(Profile).filter(Profile.MSV == msv).first()

    if not user_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for the current user."
        )

    return user_profile

@router.post("/add-profile", status_code=status.HTTP_201_CREATED)
async def add_profile(
    request: CreateProfileRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied. Only admin can add profiles.'
        )

    # Check if the user already has a profile
    existing_profile = db.query(Profile).filter(Profile.MSV == request.MSV).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Profile already exists for this student.'
        )
    profile_data = request.model_dump()

    new_profile = Profile(
        msv=profile_data['MSV'],
        hoten=profile_data['hoten'],
        ngaysinh=profile_data['ngaysinh'],
        gioitinh=profile_data['gioitinh'],
        khoa=profile_data['khoa'],
        nganh=profile_data['nganh'],
        gpa=profile_data['GPA'],
        gvphutrach=profile_data['GVphutrach']
    )
    db.add(new_profile)
    db.commit()

    return {'message': 'Profile added successfully.'}

@router.put("/edit-student-profile/{msv}")
async def edit_student_profile(
    msv: str,
    update_data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Ensure that the current user is an admin
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied. Only admin can edit student profiles.'
        )

    # Retrieve the student's profile to edit
    student_profile = db.query(Profile).filter(Profile.MSV == msv).first()

    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile not found for the student with MSV: {msv}"
        )

    # Update the profile with the new data
    for field, value in update_data.model_dump().items():
        setattr(student_profile, field, value)

    db.commit()
    db.refresh(student_profile)

    return student_profile

@router.delete("/delete-profile/{msv}")
async def delete_profile(
    msv: str,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    # Kiểm tra xem người gửi yêu cầu có quyền xóa profile không
    if user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Permission denied. Only admin can delete profiles.'
        )

    # Tìm profile cần xóa
    profile = db.query(Profile).filter(Profile.MSV == msv).first()

    # Nếu không tìm thấy, nâng cấp HTTPException
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Profile not found.'
        )

    # Xóa profile
    db.delete(profile)
    db.commit()

    return {'message': 'Profile deleted successfully.'}

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username, User.password == password).first()
    if not user:
        return False
    return user

def create_access_token(username: str, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'role': role}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
