from main import calc_income, calc_employment
# from PyQt5 import QtWidgets
from building import *
from constants import *

# class Day(QtWidgets.QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.layout = QtWidgets.QGridLayout(self)
#         self.l_bal = QtWidgets.QLabel(self)
#         self.l_employ = QtWidgets.QLabel(self)
#         self.l_income = QtWidget.QLabel(self)
#         self.
#         self.setLayout(self.layout)

# class Main(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.layout = QtWidgets.QHBoxLayout(self)
#         self.layout.addWidget(Day(self))
#         self.setLayout(self.layout)
#         self.show()

# if __name__ == "__main__":
#     app = QtWidgets.QApplication([])
#     ex = Main()
#     app.exec_()

class Economy:
    def __init__(self, buildings=None, balance=40000, loans=None):
        if buildings is None:
            self.buildings = []
        else:
            self.buildings = buildings
        if loans is None:
            self.loans = []
        else:
            self.loans = loans

        self.bal = balance

    def add_building(self, building):
        self.buildings.append(building)
        self.bal -= building[0].cost() * building[1]

    def add_loan(self, loan):
        self.loans.append(loan)
        self.bal += loan[0]

    def pay_for_loan(self, idx, amt):
        self.loans[idx][0] -= amt
        self.bal -= amt

    def income(self):
        return calc_income(self.get_data())[0]

    def employ(self):
        return calc_employment(self.get_data())[0]
        
    def get_data(self):
        buildings = []
        for b in self.buildings:
            for i in range(b[1]):
                buildings.append(b[0])
        
        return {"regions": {"a": {"buildings": buildings}}}

    def day(self):
        income = self.income()
        employment = self.employ()
        self.bal += income
        if self.bal < 0:
            self.bal += self.bal * OVERDRAFT_INTEREST

        for l in self.loans:
            l[0] *= 1 + l[1]

        print(f"Bal: {self.bal:.2f}, Emp: {employment:.2f}, Inc: {income:.2f}")
        # print("Loans:")
        # for i, l in enumerate(self.loans):
            # print(f"{i}: {l[0]:.2f} @ {l[1] * 100:.2f}%")

        # print("\n")

import datetime
d = datetime.date.today()

things_to_build = [(Building(FARMING, d), 50)] * 32 + [
    (Building(FARMING, d), 19),
    (Building(HOUSE, d, 4), 1),
    (Building(HOUSE, d, 4), 1),
    (Building(HOUSE, d, 4), 1),
    (Building(HOUSE, d, 4), 1),
    (Building(HOUSE, d, 2), 1),
    (Building(HOUSE, d, 2), 1),
    (Building(HOUSE, d, 2), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
    (Building(OFFICE, d), 1),
]

def do_something(eco, val):
    pass

def fitness(val):
    eco = Economy(buildings=[
            (Building(HOUSE, d, 4), 7),
            (Building(AIRPORT, d, 100), 1),
            (Building(MARKET_STALL, d), 1),
            (Building(AIRPORT, d, 109), 1),
            (Building(POLICE_STATION, d), 1),
            (Building(HOSPITAL, d), 1),
            (Building(POST_OFFICE, d), 1),
            (Building(OFFICE, d), 9),
            (Building(FARMING, d), 300),
        ], balance=-4118.68,
           loans=[[13147.8, 0.042]])

    for i in range(10):
        eco.day()
        do_something(eco, val)

    return eco.income() if eco.bal > 0 else 0
print(len(things_to_build))
print(fitness(0))