from __future__ import annotations

from sqlalchemy import Engine
from sqlmodel import Session, select

from sherpi.contexts.identity.domain.user import Role, User
from sherpi.infrastructure.persistence.models import UserRow


class SqlUserRepository:
    """Implementa `UserRepository` sobre SQLModel/SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        self._engine = engine

    def get_by_email(self, email: str) -> User | None:
        with Session(self._engine) as s:
            row = s.exec(select(UserRow).where(UserRow.email == email)).first()
            return self._to_domain(row) if row else None

    def get_by_id(self, user_id: str) -> User | None:
        with Session(self._engine) as s:
            row = s.get(UserRow, user_id)
            return self._to_domain(row) if row else None

    def save(self, user: User) -> None:
        with Session(self._engine) as s:
            existing = s.exec(select(UserRow).where(UserRow.email == user.email)).first()
            if existing:
                existing.hashed_password = user.hashed_password
                existing.role = user.role
                existing.is_active = user.is_active
                s.add(existing)
            else:
                s.add(
                    UserRow(
                        id=user.id,
                        email=user.email,
                        hashed_password=user.hashed_password,
                        role=user.role,
                        is_active=user.is_active,
                    )
                )
            s.commit()

    def exists(self, email: str) -> bool:
        with Session(self._engine) as s:
            return s.exec(select(UserRow).where(UserRow.email == email)).first() is not None

    def _to_domain(self, row: UserRow) -> User:
        return User(
            id=row.id,
            email=row.email,
            hashed_password=row.hashed_password,
            role=Role(row.role),
            is_active=row.is_active,
        )
