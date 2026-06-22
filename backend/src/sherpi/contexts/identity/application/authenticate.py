from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sherpi.contexts.identity.domain.hasher import BcryptHasher
from sherpi.contexts.identity.domain.issuer import JwtIssuer
from sherpi.contexts.identity.domain.ports import UserRepository
from sherpi.shared_kernel.errors import AuthenticationError


class Authenticate:
    def __init__(
        self,
        repo: UserRepository,
        hasher: BcryptHasher,
        issuer: JwtIssuer,
        max_attempts: int = 5,
        lockout_minutes: int = 15,
    ) -> None:
        self._repo = repo
        self._hasher = hasher
        self._issuer = issuer
        self._max_attempts = max_attempts
        self._lockout_minutes = lockout_minutes
        self._attempts: dict[str, list[datetime]] = {}

    def run(self, email: str, password: str) -> str:
        self._check_lockout(email)
        user = self._repo.get_by_email(email)
        if (
            user is None
            or not user.is_active
            or not self._hasher.verify(password, user.hashed_password)
        ):
            self._record_failure(email)
            raise AuthenticationError("Credenciais inválidas.")
        self._attempts.pop(email, None)
        return self._issuer.issue(user)

    def _check_lockout(self, email: str) -> None:
        now = datetime.now(UTC)
        cutoff = now - timedelta(minutes=self._lockout_minutes)
        recent = [t for t in self._attempts.get(email, []) if t > cutoff]
        self._attempts[email] = recent
        if len(recent) >= self._max_attempts:
            raise AuthenticationError("Conta bloqueada temporariamente. Tente mais tarde.")

    def _record_failure(self, email: str) -> None:
        self._attempts.setdefault(email, []).append(datetime.now(UTC))
