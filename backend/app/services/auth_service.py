from sqlalchemy.orm import Session

from app.exceptions.errors import AuthError, ConflictError
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, email: str, password: str, first_name: str, last_name: str) -> User:
        if self.repo.get_by_email(email):
            raise ConflictError("An account with this email already exists.")
        return self.repo.create(email, hash_password(password), first_name, last_name)

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password.")
        return create_access_token(subject=user.email)
