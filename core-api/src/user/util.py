# core-api/src/user/util.py

import hashlib
import uuid
from datetime import date


class Util:

    @staticmethod
    def salifyHash(pwd, email):
        salt = uuid.uuid5(uuid.NAMESPACE_URL, email).hex
        return hashlib.sha512((pwd + salt).encode()).hexdigest()

    @staticmethod
    def calculate_age(birthdate):
        if not birthdate:
            return None
        today = date.today()
        return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))