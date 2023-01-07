class UIDNotFound(Exception):
    pass

class ShenheAccountNotFound(Exception):
    pass

class ItemNotFound(Exception):
    pass

class NoPlayerFound(Exception):
    pass

class NoCharacterFound(Exception):
    pass

class CardNotFound(Exception):
    pass

class InvalidWeaponCalcInput(Exception):
    pass

class InvalidAscensionInput(Exception):
    pass

class DBError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg