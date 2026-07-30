from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserCreate


def create_user(db: Session, user: UserCreate):

    db_user = User(
        name=user.name,
        email=user.email
    )

    db.add(db_user)

    db.commit()

    db.refresh(db_user)

    return db_user


def get_users(db: Session):

    return db.query(User).all()


def get_user(db: Session, user_id: int):

    return db.query(User).filter(
        User.id == user_id
    ).first()


def delete_user(db: Session, user_id: int):

    user = get_user(db, user_id)

    if user:
        db.delete(user)
        db.commit()

    return user