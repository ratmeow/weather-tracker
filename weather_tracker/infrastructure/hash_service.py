import bcrypt

from weather_tracker.application.interfaces import Hasher


class BcryptHasher(Hasher):
    def hash(self, text: str) -> str:
        return bcrypt.hashpw(text.encode(), bcrypt.gensalt()).decode()

    def verify(self, text: str, hashed_text: str) -> bool:
        return bcrypt.checkpw(text.encode(), hashed_text.encode())
