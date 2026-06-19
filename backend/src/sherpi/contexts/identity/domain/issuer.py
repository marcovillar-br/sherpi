from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from sherpi.contexts.identity.domain.user import User


class JwtIssuer:
    def __init__(self, secret: str, algorithm: str = "HS256", expire_minutes: int = 60) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._expire_minutes = expire_minutes

    def issue(self, user: User) -> str:
        exp = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        payload: dict[str, object] = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "exp": exp,
        }
        return str(jwt.encode(payload, self._secret, algorithm=self._algorithm))

    def verify(self, token: str) -> dict[str, object]:
        decoded: dict[str, object] = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        return decoded
