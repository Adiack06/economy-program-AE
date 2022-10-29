from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from PyQt5 import QtCore, Qt, QtGui
import sys
import json
import traceback
import os
import datetime
import re
from typing import Union
# TODO
# display bal after hypothetical buying thing

RAILWAY_STATION       = 0
MARKET_STALL          = 1
POLICE_STATION        = 2
POST_OFFICE           = 3
SMALL_STORE           = 4
HOSPITAL              = 5
FIRE_STATION          = 6
SUPER_STORE           = 7
PIER                  = 8
DOCK                  = 9
QUARRY                = 10
SMALL_FACTORY         = 11
LARGE_FACTORY         = 12
FARMING               = 13
NAVAL_DOCKYARD        = 14
MILLS                 = 15
AIRBASE               = 16
SUPPLY_HUB            = 17
REACTOR               = 18
ELECTRICAL_GENERATION = 19
AIRPORT               = 20
HOUSE                 = 21

ROI = 23

# hack to make json serialise my types properly lmao
def wrapped_default(self, obj):
    return getattr(obj.__class__, "serialise", wrapped_default.default)(obj)
wrapped_default.default = json.JSONEncoder().default
json.JSONEncoder.default = wrapped_default

class BuildingInfo:
    def __init__(self, wage: float, employees: int, cost: float, name: str):
        self.wage = wage
        self.employees = employees
        self.cost = cost
        self.name = name

class Building:
    def __init__(self, btype: int, size: int=None):
        self.btype = btype
        self.size = size
        
        if self.btype == AIRPORT or self.btype == HOUSE:
            assert self.size != None, "For airports and houses, the size must not be None"
    
    def cost(self) -> float:
        if self.btype == AIRPORT:
            return ROI * self.income()
        elif self.btype == HOUSE:
            return {1: 1500, 2: 3000, 4: 6000, 6: 9000}[self.size]
        else:
            return BUILDING_INFO[self.btype].cost
    
    def wage(self) -> float:
        return BUILDING_INFO[self.btype].wage
    
    def employees(self) -> int:
        if self.btype == AIRPORT:
            return self.size / 20
        return BUILDING_INFO[self.btype].employees
    
    def name(self) -> str:
        if self.btype == AIRPORT:
            return str(self.size) + " block long airport"
        if self.btype == HOUSE:
            return str(self.size) + " person house"
        return BUILDING_INFO[self.btype].name
        
    def income(self) -> float:
        return self.wage() * self.employees() * 8 # 8 hours per day
        
    def serialise(self) -> Union[list[int, int], int]:
        # if need to store size, return [type, size]
        if self.size != None:
            return [self.btype, self.size]
        else: # else just a single int
            return self.btype
            
    def deserialise(obj: Union[list[int, int], int]):
        # serialised buildings are either a list of [type, size]
        if type(obj) == type([]):
            return Building(obj[0], obj[1])
        else: # or just a single int, being type
            return Building(obj)
            
    def __hash__(self):
        return hash((self.btype, self.size))
        
    def __eq__(self, other):
        return type(self) == type(other) and self.btype == other.btype and self.size == other.size
        

BUILDING_INFO = {
    RAILWAY_STATION       : BuildingInfo(13.5,  2,     4968,     "Railway Station"),
    MARKET_STALL          : BuildingInfo(11,    1,     2024.00,  "Market Stall"),
    POLICE_STATION        : BuildingInfo(19.6,  3,     10819.20, "Police Station"),
    POST_OFFICE           : BuildingInfo(12.5,  2,     4600.00,  "Post Office"),
    SMALL_STORE           : BuildingInfo(11.5,  2,     4232.00,  "Small Store/Fuel Station"),
    HOSPITAL              : BuildingInfo(26,    3,     14352.00, "Hospital"),
    FIRE_STATION          : BuildingInfo(19,    2,     6992.00,  "Fire station"),
    SUPER_STORE           : BuildingInfo(12.2,  4,     8979.20,  "Super Store"),
    PIER                  : BuildingInfo(14,    1,     2576.00,  "Pier"),
    DOCK                  : BuildingInfo(15.8,  2,     5814.40,  "Dock per 10 blocks"),
    QUARRY                : BuildingInfo(11.2,  2,     4121.60,  "Quarries Per Chunk"),
    SMALL_FACTORY         : BuildingInfo(14.5,  6,     16008.00, "Small Factory"),
    LARGE_FACTORY         : BuildingInfo(15.5,  12,    34224.00, "Large Factory"),
    FARMING               : BuildingInfo(18.5,  1/162, 21.01,    "Farming per block"),
    NAVAL_DOCKYARD        : BuildingInfo(15.5,  1,     2852.00,  "Naval dockyard per 7 blocks"),
    MILLS                 : BuildingInfo(12,    0,     36500.00, "MiLLs"),
    AIRBASE               : BuildingInfo(17.5,  4,     12880.00, "Airbase"),
    SUPPLY_HUB            : BuildingInfo(10.5,  1,     1932.00,  "Supply hub"),
    REACTOR               : BuildingInfo(20.5,  3,     11316.00, "Nuclear/biogas reactor"),
    ELECTRICAL_GENERATION : BuildingInfo(12.5,  2,     4600.00,  "Electrical generation/storage"),
    AIRPORT               : BuildingInfo(18,    0,     69,       "Airport"),
    HOUSE                 : BuildingInfo(0,     0,     69420,    "House"),
}

MONEY_PREFIX = "UN$"
    
TRANSACTION_MANUAL = 1
TRANSACTION_BUY = 2
TRANSACTION_SELL = 3
TRANSACTION_INCOME = 4

class Transaction:
    def __init__(self, ty, timestamp, *, comment=None, amount=None, building=None, count=None):
        if ty == TRANSACTION_MANUAL:
            assert comment != None, "Comment on manual transaction must not be None"
            assert amount != None, "Amount on manual transaction must not be None"
        else:
            assert building != None, "Building type on auto transaction must not be None"
            assert count != None, "Count on auto transaction must not be None"

        self.amount = amount
        self.comment = comment
        self.trans_type = ty
        self.building = building
        self.count = count
        self.timestamp = timestamp
    
    def serialise(self):
        if self.trans_type == TRANSACTION_MANUAL:
            return {"amount": self.amount, "comment": self.comment, "type": self.trans_type, "timestamp": self.timestamp}
        else:
            return {"count": self.count, "building": self.building, "type": self.trans_type, "timestamp": self.timestamp}

    def deserialise(object):
        if object["type"] == TRANSACTION_MANUAL:
            return Transaction(object["type"], object["timestamp"], amount=object["amount"], comment=object["comment"])
        else:
            return Transaction(object["type"], object["timestamp"], building=Building.deserialise(object["building"]), count=object["count"])
            
    def compute_amount(self) -> int:
        if self.trans_type == TRANSACTION_MANUAL:
            return self.amount
        elif self.trans_type == TRANSACTION_BUY:
            return -self.building.cost() * self.count
        elif self.trans_type == TRANSACTION_SELL:
            return self.building.cost() * self.count
            
    def compute_comment(self):
        if self.trans_type == TRANSACTION_MANUAL:
            return self.comment
        elif self.trans_type == TRANSACTION_BUY:
            return f"Bought {self.count}x {self.building.name()}"
        elif self.trans_type == TRANSACTION_SELL:
            return f"Sold {self.count}x {self.building.name()}"

data = {
    "regions": {},
    "transactions": [],
    "current_day": datetime.date(2022, 10, 10)
}

if os.path.exists("economy.json"):
    with open("economy.json", "r") as f:
        raw_data = json.load(f)
        
    for reg in raw_data["regions"]:
        data["regions"][reg] = {"buildings": []}
        for b in raw_data["regions"][reg]["buildings"]:
            data["regions"][reg]["buildings"].append(Building.deserialise(b))
            
    data["transactions"] = [Transaction.deserialise(t) for t in raw_data["transactions"]]
    data["current_day"] = datetime.date.fromisoformat(raw_data["current_day"])

def serialise_all():
    ddata = data.copy()
    ddata["current_day"] = data["current_day"].isoformat()
    file_data = json.dumps(ddata, indent=4)
    return file_data

def save():
    file_data = serialise_all()
    with open("economy.json", "w") as f:
        f.write(file_data)

def format_date(date):
    return datetime.date.fromisoformat(date).strftime("%d/%m/%Y")

def format_money(amt):
    return MONEY_PREFIX + str(round(amt, 2))

def send_info_popup(txt):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(txt)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

def calc_employment(data):
    """Return (total, regional) employment calculated given some data"""
    regions = {}
    total_people = 0
    total_jobs = 0
    for region in data["regions"]:
        jobs = 0
        people = 0
        for building in data["regions"][region]["buildings"]:
            if building.btype == HOUSE:
                people += building.size
            else:
                jobs += building.employees()
        
        if people == 0:
            rate = 0
        else:
            rate = jobs / people
        regions[region] = rate
        total_people += people
        total_jobs += jobs
    
    return total_jobs / total_people if total_people != 0 else 0, regions

def calc_income(data):
    employment, regional_employment = calc_employment(data)
    gross_income = 0
    regional_income = {}
    reduce_by = lambda i, p: i / p if p >= 1 else i * p
    for region in data["regions"]:
        region_gross_income = 0
        for building in data["regions"][region]["buildings"]:
            region_gross_income += building.income()

        region_income = reduce_by(region_gross_income, regional_employment[region])
        regional_income[region] = region_income
        gross_income += region_gross_income
    
    income = reduce_by(gross_income, employment)
    return income, regional_income

class BuildingEntry(Qt.QObject):
    decrease = Qt.pyqtSignal()
    def __init__(self, building, count, parent):
        super().__init__()
        self.building = building
        self.count = count

        self.l_type = QtWidgets.QLabel(building.name(), parent)
        self.l_count = QtWidgets.QLabel(parent)
        self.l_employed = QtWidgets.QLabel(parent)
        self.l_income = QtWidgets.QLabel(parent)
        self.l_cost = QtWidgets.QLabel(parent)
        self.b_decrease = QtWidgets.QPushButton("-", parent)
        
        self.b_decrease.clicked.connect(lambda: self.decrease.emit())
        width = self.b_decrease.fontMetrics().boundingRect("-").width() + 7
        self.b_decrease.setMaximumWidth(width)
        self.b_decrease.setMaximumHeight(width) # square
        self.update_count(self.count)
        
    def update_count(self, count):
        self.l_cost.setText(format_money(self.building.cost() * count))
        self.l_count.setText(str(count))
        self.l_income.setText(format_money(self.building.wage() * self.building.employees() * count * 8))
        self.l_employed.setText(str(round(self.building.employees() * count, 3)))
        self.count = count
        
    def remove(self, layout):
        layout.removeWidget(self.l_type)
        layout.removeWidget(self.l_count)
        layout.removeWidget(self.l_employed)
        layout.removeWidget(self.l_income)
        layout.removeWidget(self.l_cost)
        layout.removeWidget(self.b_decrease)
        self.l_type.deleteLater()
        self.l_count.deleteLater()
        self.l_employed.deleteLater()
        self.l_income.deleteLater()
        self.l_cost.deleteLater()
        self.b_decrease.deleteLater()
        self.l_type = None
        self.l_count = None
        self.l_employed = None
        self.l_income = None
        self.l_cost = None
        self.b_decrease = None
        
    def insert(self, layout, idx):
        layout.addWidget(self.l_type, idx, 0)
        layout.addWidget(self.l_count, idx, 1)
        layout.addWidget(self.l_employed, idx, 2)
        layout.addWidget(self.l_income, idx, 3)
        layout.addWidget(self.l_cost, idx, 4)
        layout.addWidget(self.b_decrease, idx, 5)

class BuildingList(QtWidgets.QWidget):
    building_count_decrease = Qt.pyqtSignal(BuildingEntry)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        self.setLayout(self.layout)
        self.index = 0
        self.items = []
        self.l_type = QtWidgets.QLabel("Bulding type")
        self.l_count = QtWidgets.QLabel("Count")
        self.l_employed = QtWidgets.QLabel("Employed")
        self.l_income = QtWidgets.QLabel("Income")
        self.l_cost = QtWidgets.QLabel("Cost")
        
        self.layout.addWidget(self.l_type, 0, 0)
        self.layout.addWidget(self.l_count, 0, 1)
        self.layout.addWidget(self.l_employed, 0, 2)
        self.layout.addWidget(self.l_income, 0, 3)
        self.layout.addWidget(self.l_cost, 0, 4)

    def add_building(self, building, count):
        item = BuildingEntry(building, count, self)
        self.items.append(item)
        idx = len(self.items)
        item.insert(self.layout, idx)
        item.decrease.connect(lambda: self.building_count_decrease.emit(item))
    
    def remove_building(self, building):
        item = None
        for n in self.items:
            if n.building == building:
                item = n
        if item != None:
            item.remove(self.layout)
            self.items.remove(item)
        else:
            raise RuntimeWarning("BuildingList.remove_building called on non-existent building")

    def update_building(self, building, count):
        for n in self.items:
            if n.building == building:
                n.update_count(count)
                
    def clear(self):
        for item in self.items:
            item.remove(self.layout)
        
        self.items.clear()
    
class BuildingsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        self.region_select = QtWidgets.QComboBox(self)
        self.e_newregion = QtWidgets.QLineEdit(self)
        self.b_newregion = QtWidgets.QPushButton("New region", self)
        self.b_delregion = QtWidgets.QPushButton("Delete region", self)
        
        self.region_select.addItem("Total")
        for region in data["regions"].keys():
            self.region_select.addItem(region)

        self.buildings = []
        self.building_list = BuildingList(self)
        
        self.layout = QtWidgets.QGridLayout(self)
        
        self.type_selector = QtWidgets.QComboBox(self)
        for btype, binfo in BUILDING_INFO.items():
            self.type_selector.addItem(binfo.name, userData=btype)

        self.e_count = QtWidgets.QSpinBox(self)
        self.e_count.setValue(1)
        self.e_count.setMaximum(999)
        self.e_size  = QtWidgets.QSpinBox(self)
        self.e_size.setMaximum(999)
        self.e_size.hide()
        self.b_add   = QtWidgets.QPushButton("Add", self)
        self.l_compcost = QtWidgets.QLineEdit(self)
        self.l_compincome = QtWidgets.QLineEdit(self)
        self.l_compemployees=QtWidgets.QLineEdit(self)
        
        self.l_btype = QtWidgets.QLabel("Building type")
        self.l_count = QtWidgets.QLabel("Count")
        self.l_cost  = QtWidgets.QLabel("Cost")
        self.l_income= QtWidgets.QLabel("Income")
        self.l_employees=QtWidgets.QLabel("Employees")
        self.l_size  = QtWidgets.QLabel("Size")
        
        self.spacer = QtWidgets.QLabel("", self)
        
        self.layout.addWidget(self.region_select, 0, 0)
        self.layout.addWidget(self.e_newregion, 0, 1)
        self.layout.addWidget(self.b_newregion, 0, 2)
        self.layout.addWidget(self.b_delregion, 0, 3)
        self.layout.addWidget(self.l_btype, 1, 0)
        self.layout.addWidget(self.l_count, 1, 1)
        self.layout.addWidget(self.l_income, 1, 2)
        self.layout.addWidget(self.l_cost, 1, 3)
        self.layout.addWidget(self.l_employees, 1, 4)
        self.layout.addWidget(self.l_size, 1, 5)
        self.layout.addWidget(self.type_selector, 2, 0)
        self.layout.addWidget(self.e_count, 2, 1)
        self.layout.addWidget(self.l_compincome, 2, 2)
        self.layout.addWidget(self.l_compcost, 2, 3)
        self.layout.addWidget(self.l_compemployees, 2, 4)
        self.layout.addWidget(self.e_size, 2, 5)
        self.layout.addWidget(self.b_add, 2, 6)
        self.layout.addWidget(self.building_list, 3, 0, 1, 7)
        self.layout.addWidget(self.spacer, 4, 0, 1, 7)
        self.layout.setRowStretch(4, 1)
        self.setLayout(self.layout)
        
        self.l_compcost.setReadOnly(True)
        self.l_compincome.setReadOnly(True)
        self.l_compemployees.setReadOnly(True)
        self.type_selector.activated[str].connect(lambda t: self.recalc_preview())
        self.e_count.valueChanged[int].connect(lambda n: self.recalc_preview())
        self.e_size.valueChanged[int].connect(lambda s: self.recalc_preview())
        self.b_add.clicked.connect(self.add_building)
        self.b_newregion.clicked.connect(self.add_region)
        self.b_delregion.clicked.connect(self.del_region)
        self.region_select.activated[str].connect(lambda r: self.region_change())
        self.building_list.building_count_decrease[BuildingEntry].connect(self.remove_building)
        self.recalc_preview()
        self.region_change()
        
        self.parent.transactions_tab.recalc_income()

    def add_region(self):
        region = self.e_newregion.text()
        if len(region.strip()) == 0:
            send_info_popup("Enter a region name first")
            return
        if region in data["regions"]:
            send_info_popup("Enter a unique region name")
            return
            
        self.e_newregion.setText("")

        self.region_select.addItem(region)
        data["regions"][region] = {"buildings": []}
        save()
    
    def del_region(self):
        if not self.check_real_region():
            return

        region = self.region_select.currentText()
        reply = QtWidgets.QMessageBox.question(self, f"Delete region", "Really delete region '{region}'? The buildings won't be transferred.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:
            return
            
        del data["regions"][region]
        save()
        self.region_select.removeItem(self.region_select.currentIndex())

    def region_change(self):
        self.curr_region = self.region_select.currentText()

        self.building_list.clear()
        self.buildings = []
        if self.curr_region == "Total":
            for region in data["regions"].values():
                for building in region["buildings"]:
                    self.buildings.append(building)
        else:
            self.buildings = data["regions"][self.curr_region]["buildings"]
        
        building_nums = {}
        for building in self.buildings:
            if not building in building_nums:
                building_nums[building] = 0
            building_nums[building] += 1
        
        for building, count in building_nums.items():
            self.building_list.add_building(building, count)
        
    def recalc_preview(self):
        btype = self.type_selector.currentData()
        count = self.e_count.value()
        if btype == HOUSE or btype == AIRPORT:
            self.e_size.show()
            self.l_size.show()
            size = self.e_size.value()
            building = Building(btype, size)
            if btype == HOUSE and not size in [1, 2, 4, 6]: # perhaps the size is not valid yet, let's just ignore that
                self.l_compcost.setText("Invalid size")
                self.l_compincome.setText("Invalid size")
                return
        else:
            self.e_size.hide()
            self.l_size.hide()
            building = Building(btype)
            
        income = building.income() * count
        self.l_compcost.setText(format_money(building.cost() * count))
        self.l_compincome.setText(format_money(income))
        self.l_compemployees.setText(str(round(building.employees() * count, 3)))
    
    def check_real_region(self):
        """check the current region is not 'Total'. If it is, warn the user
        returns whether a real region was selected"""
        if self.curr_region == "Total":
            send_info_popup("Select a region first")
            return False
        return True

    def add_building(self):
        if not self.check_real_region():
            return

        btype = self.type_selector.currentData()
        if btype == AIRPORT or btype == HOUSE:
            building = Building(btype, self.e_size.value())
        else:
            building = Building(btype)

        count = self.e_count.value()
        if not building in self.buildings:
            self.building_list.add_building(building, 0)
        
        for i in range(count): # hack, just like clicking it multiple times lol
            self.buildings.append(building)

        self.building_list.update_building(building, self.buildings.count(building))
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()
        
        self.parent.transactions_tab.add_transaction(Transaction(
            TRANSACTION_BUY,
            data["current_day"].isoformat(),
            building=building,
            count=count
        ))
        
        self.parent.transactions_tab.recalc_income()

    def remove_building(self, entry: BuildingEntry):
        if not self.check_real_region():
            return

        building = entry.building
        count = entry.count
        self.buildings.remove(building)
        if count <= 1:
            self.building_list.remove_building(building)
        else:
            self.building_list.update_building(building, self.buildings.count(building))
        
        self.parent.transactions_tab.add_transaction(Transaction(
            TRANSACTION_SELL,
            data["current_day"].isoformat(),
            building=building,
            count=1,
        ))
        
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()
        self.parent.transactions_tab.recalc_income()

class KeybindTable(QtWidgets.QTableWidget):
    keyPressed = Qt.pyqtSignal(QtGui.QKeyEvent)
    def keyPressEvent(self, event):    
        if type(event) == QtGui.QKeyEvent:
            self.keyPressed.emit(event)

class TransactionsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.income = 0
        self.layout = QtWidgets.QGridLayout(self)
        self.bottom_layout = QtWidgets.QHBoxLayout()
        
        self.table = KeybindTable(self)
        self.table.setColumnCount(3)
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(["Amount", "Date", "Comment"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        self.e_amount = QtWidgets.QLineEdit(self)
        self.e_comment= QtWidgets.QLineEdit(self)
        self.b_add    = QtWidgets.QPushButton("Add", self)
        self.l_bal    = QtWidgets.QLabel(self)
        self.l_income = QtWidgets.QLabel(self)
        self.l_employment=QtWidgets.QLabel(self)
        
        self.e_amount.setPlaceholderText("Amount")
        self.e_comment.setPlaceholderText("Comment")
        
        self.layout.addWidget(self.table, 1, 0, 1, 3)
        self.layout.addWidget(self.e_amount, 0, 0)
        self.layout.addWidget(self.e_comment, 0, 1)
        self.layout.addWidget(self.b_add, 0, 2)
        self.layout.addLayout(self.bottom_layout, 2, 0)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)
        
        self.b_get_paid = QtWidgets.QPushButton("Get paid", self)
        self.b_get_paid.clicked.connect(self.get_paid)
        
        self.bottom_layout.addWidget(self.l_bal)
        self.bottom_layout.addWidget(self.l_income)
        self.bottom_layout.addWidget(self.l_employment)
        self.bottom_layout.addWidget(self.b_get_paid)
        
        self.b_add.clicked.connect(self._add_transaction_button)
        self.table.keyPressed[QtGui.QKeyEvent].connect(self._table_keypress)
        
        self.transaction_widgets = []
        
        for t in data["transactions"]:
            self._add_transaction_to_table(t)
        self._recalc_balance()
        
    def _table_keypress(self, event):
        if event.key() == QtCore.Qt.Key_Delete and self.table.rowCount() > 0:
            row = self.table.currentRow()
            data["transactions"].pop(row)
            self.table.removeRow(row)
            save()
            self._recalc_balance()

    def _add_transaction_button(self):
        try:
            amount = round(float(self.e_amount.text()), 2)
        except ValueError:
            send_info_popup("Enter a valid number for the amount (without any $ or £)")
            return
        
        date = data["current_day"].isoformat()
        comment = self.e_comment.text()
        self.add_transaction(Transaction(TRANSACTION_MANUAL, date, comment=comment, amount=amount))
        self.e_comment.setText("")
        self.e_amount.setText("")
    
    def add_transaction(self, transaction: Transaction):
        data["transactions"].append(transaction)
        save()

        self._add_transaction_to_table(transaction)
        self._recalc_balance()
        
    def _add_transaction_to_table(self, transaction: Transaction):
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(format_money(transaction.compute_amount())))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(format_date(transaction.timestamp)))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(transaction.compute_comment()))

    def _recalc_balance(self):
        bal = 0
        for t in data["transactions"]:
            bal += t.compute_amount()
        
        # TODO again terrible, see below
        self.parent.stats_tab.l_bal.setText("Balance: " + format_money(bal))
        self.l_bal.setText("Balance: " + format_money(bal))
        
    def recalc_income(self):
        employment, regional_employment = calc_employment(data)
        income, regional_income = calc_income(data)
        self.income = income # TODO do I need this?
        
        # TODO terrible place to put this lol
        # make it better ig (signals?)
        # Set both the labels at the bottom of this tab and also those of the stats tab
        self.parent.stats_tab.l_income.setText("Income: " + format_money(self.income))
        self.l_income.setText("Income: " + format_money(self.income))
        self.parent.stats_tab.l_employment.setText("Employment: " + str(round(employment * 100, 2)) + "%")
        self.l_employment.setText("Employment: " + str(round(employment * 100, 2)) + "%")
        
    def get_paid(self):
        self.add_transaction(Transaction(
            TRANSACTION_MANUAL,
            data["current_day"].isoformat(),
            comment="Income",
            amount=self.income,
        ))

class GraphControls(QtWidgets.QWidget):
    def __init__(self, figure, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.ax = figure.subplots()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.graph_type = QtWidgets.QComboBox(self)
        self.x_axis = QtWidgets.QComboBox(self)
        self.y_axis = QtWidgets.QComboBox(self)
        
        self.l_gtype = QtWidgets.QLabel("Graph type", self)
        self.l_xaxis = QtWidgets.QLabel("Plot...", self)
        self.l_yaxis = QtWidgets.QLabel("Against...", self)
        
        self.b_plot = QtWidgets.QPushButton("Plot", self)
        
        self.graph_type.addItems(["Line graph", "Scatter graph", "Bar chart", "Pie chart"])
        
        self.layout.addWidget(self.l_gtype)
        self.layout.addWidget(self.graph_type)
        self.layout.addWidget(self.l_xaxis)
        self.layout.addWidget(self.x_axis)
        self.layout.addWidget(self.l_yaxis)
        self.layout.addWidget(self.y_axis)
        self.layout.addWidget(self.b_plot)
        
        self.setLayout(self.layout)
        
        self.graph_type.activated[str].connect(lambda x: self.update())
        self.x_axis.activated[str].connect(lambda x: self.update())
        self.y_axis.activated[str].connect(lambda x: self.update())
        self.b_plot.clicked.connect(self.plot)
        
        self.update()
        
    def update(self):
        ty = self.graph_type.currentText()
        self.x_axis.clear()
        self.y_axis.clear()
        # TODO graph something of just one region
        if ty == "Line graph":
            self.x_axis.addItems(["Balance", "Income", "Expenditure", "Employment"])
            self.y_axis.addItems(["Time"])
            
        elif ty == "Pie chart":
            self.x_axis.addItems(["Income", "Expenditure"])
            self.y_axis.addItems(["Region"])
            
        elif ty == "Bar chart":
            self.x_axis.addItems(["Employment"])
            self.y_axis.addItems(["Region"])
    
    def plot(self):
        # TODO do it
        gtype = self.graph_type.currentText()
        xaxis = self.x_axis.currentText()
        yaxis = self.y_axis.currentText()
        
        if gtype == "Pie chart":
            if xaxis == "Income" and yaxis == "Region":
                _, regional_income = calc_income(data)
            
                self.ax.pie(regional_income.values(), labels=regional_income.keys(), autopct='%1.1f%%', shadow=True, startangle=90)
            self.ax.axis('equal')
            
        self.figure.canvas.draw()

class MoronException(Exception):
    pass

class StatsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QtWidgets.QGridLayout(self)
        
        self.l_income = QtWidgets.QLabel(self)
        self.l_employment = QtWidgets.QLabel(self)
        self.l_bal = QtWidgets.QLabel(self)
        self.b_next_day = QtWidgets.QPushButton("New day", self)
        self.bottom_spacer = QtWidgets.QLabel(self)
        
        self.graph_layout = QtWidgets.QVBoxLayout(self)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)
        
        self.graph_controls = GraphControls(self.figure, self)
                
        self.layout.addWidget(self.l_income, 0, 0)
        self.layout.addWidget(self.l_employment, 1, 0)
        self.layout.addWidget(self.l_bal, 2, 0)
        self.layout.addWidget(self.b_next_day, 3, 0)
        self.layout.addWidget(self.graph_controls, 4, 0)
        self.layout.addWidget(self.bottom_spacer, 5, 0)
        self.layout.addLayout(self.graph_layout, 0, 1, 100, 1)
        self.layout.setRowStretch(3, 1)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)
        
        self.b_next_day.clicked.connect(self.next_day)
    
    def next_day(self):
        save()
        if os.path.exists("backups") and os.path.isfile("backups"):
            raise MoronException("You absolute idiot, you made a file called 'backups', that's where I want to store my backups! Please delete or rename it")
        if not os.path.exists("backups"):
            os.mkdir("backups")
        
        # Yes, this is a race condition or TOC/TOU bug
        # The truth is, I do not care, for it is exceedingly unlikely that anything could happen in between
        # also it wouldn't even matter that much it would just crash and save the progress anyway lmao
        
        text_data = serialise_all()
        with open(os.path.join("backups", data["current_day"].isoformat() + ".json"), "w") as f:
            f.write(text_data)
            
        data["current_day"] += datetime.timedelta(days=1)

class PriceTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

class Main(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_gui()
        self.show()
        
    def init_gui(self):
        self.layout = QtWidgets.QVBoxLayout(self)

        self.stats_tab = StatsTab(self)
        self.transactions_tab = TransactionsTab(self)
        self.buildings_tab = BuildingsTab(self)
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(self.buildings_tab, "Buildings")
        self.tab_widget.addTab(self.transactions_tab, "Transactions")
        self.tab_widget.addTab(self.stats_tab, "Stats")
        self.tab_widget.addTab(PriceTab(self), "Price")
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)

def exception_hook(exctype, value, tb):
    traceback_formated = traceback.format_exception(exctype, value, tb)
    traceback_string = "".join(traceback_formated)
    print("Excepthook called, saving and quiteing...")
    # TODO maybe save data in ram data["regions"][btab.curr_region]["buildings"] = btab.buildings
    save()
    print(traceback_string, file=sys.stderr)
    
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText("An error occurred in the main process. Your data should be safe (in theory). Please send the following report to me(james):\n" + traceback_string)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
    sys.exit(1)

if __name__ == '__main__':
    sys.excepthook = exception_hook
    app = QtWidgets.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
