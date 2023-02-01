from building import Building
from enum import IntEnum, unique

@unique
class TransactionType(IntEnum):
    MANUAL = 1
    BUY    = 2
    SELL   = 3
    INCOME = 4

class Transaction:
    def __init__(self, ty, timestamp, *, comment=None, amount=None, buildings=None):
        if ty == TransactionType.MANUAL:
            assert comment != None, "Comment on manual transaction must not be None"
            assert amount != None, "Amount on manual transaction must not be None"
        else:
            assert buildings != None, "Buildings type on auto transaction must not be None"

        self.amount = amount
        self.comment = comment
        self.trans_type = ty
        self.buildings = buildings
        self.timestamp = timestamp
    
    def serialise(self):
        if self.trans_type == TransactionType.MANUAL:
            return {"amount": self.amount, "comment": self.comment, "type": self.trans_type, "timestamp": self.timestamp}
        else:
            return {"buildings": self.buildings, "type": self.trans_type, "timestamp": self.timestamp}

    def deserialise(object, date):
        if object["type"] == TransactionType.MANUAL:
            return Transaction(object["type"], object["timestamp"], amount=object["amount"], comment=object["comment"])
        else:
            if object.get("buildings") == None: # old transaction, assume one building + count (+ lorentz)
                buildings = [Building.deserialise(object["building"], date, lorentz=object.get("lorentz"))] * object["count"]
                return Transaction(object["type"], object["timestamp"], buildings=buildings)
            else: # new transaction, deserialise list of buildings with one lorentz each
                return Transaction(object["type"], object["timestamp"], buildings=[Building.deserialise(i, date) for i in object["buildings"]])
            
    def compute_amount(self) -> int:
        if self.trans_type == TransactionType.MANUAL:
            return self.amount
        elif self.trans_type == TransactionType.BUY:
            return -sum([building.cost() for building in self.buildings])
        elif self.trans_type == TransactionType.SELL:
            return sum([building.cost() for building in self.buildings])
            
    def compute_comment(self):
        if self.trans_type == TransactionType.MANUAL:
            return self.comment
        elif self.trans_type == TransactionType.BUY:
            return f"Bought {len(self.buildings)}x {self.buildings[0].name()}"
        elif self.trans_type == TransactionType.SELL:
            return f"Sold {len(self.buildings)}x {self.buildings[0].name()}"