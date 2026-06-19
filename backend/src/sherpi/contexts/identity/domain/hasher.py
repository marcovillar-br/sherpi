from __future__ import annotations

import bcrypt


class BcryptHasher:
    _ROUNDS: int = 12

    def hash(self, plain: str) -> str:
        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=self._ROUNDS))
        return hashed.decode()

    def verify(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
