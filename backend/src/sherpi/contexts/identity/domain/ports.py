from __future__ import annotations

from typing import Protocol, runtime_checkable

from sherpi.contexts.identity.domain.user import User


@runtime_checkable
class UserRepository(Protocol):
    def get_by_email(self, email: str) -> User | None: ...

    def get_by_id(self, user_id: str) -> User | None: ...

    def save(self, user: User) -> None: ...

    def exists(self, email: str) -> bool: ...
