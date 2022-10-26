from PyQt5 import QtWidgets, QtCore, Qt, QtGui
import sys
import json
import traceback
import os
import datetime
import re

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

class BuildingInfo:
    def __init__(self, wage: float, employees: int, cost: float, name: str):
        self.wage = wage
        self.employees = employees
        self.cost = cost
        self.name = name

class Building:
    def __init__(self, btype: int, size: int=None):
        self.btype = type
        self.size = size
        
        if self.btype == AIRPORT or self.btype == HOUSE:
            assert self.size != None, "For airports and houses, the size must not be None"
    
    def cost(self) -> float:
        if self.btype == AIRPORT:
            return 69 # TODO fix this
        elif self.btype == HOUSE:
            return [1500, 3000, 6000, 9000][self.size]
        else:
            return BUILDING_INFO[self.btype].cost
    
    def wage(self) -> float:
        return BUILDING_INFO[self.btype].wage
    
    def employees(self) -> int:
        if self.btype == AIRPORT:
            return 420 # TODO fix this
        return BUILDING_INFO[self.btype].employees
    
    def name(self) -> str:
        if self.btype == AIRPORT:
            return str(self.size) + " block long airport"
        if self.btype == HOUSE:
            return str(self.size) + " person house"
        return BUILDING_INFO[self.btype].name
        
    def serialise(self) -> union[list[int, int], int]:
        # if need to store size, return [type, size]
        if self.size != None:
            return [self.btype, self.size]
        else: # else just a single int
            return self.btype
            
    def deserialise(self, obj: union[list[int, int], int]):
        # serialised buildings are either a list of [type, size]
        if type(obj) == type(list):
            return Building(obj[0], obj[1])
        else: # or just a single int, being type
            return Building(obj)
            
    def __hash__(self):
        return hash((self.btype, self.size))
        

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
    AIRPORT               : BuildingInfo(18,    0,     69,       "Lmao this isn't used"),
    HOUSE                 : BuildingInfo(0,     0,     69420,    "we need to have a metting latter about the consciousness of this easter egg in the code lmao")),
}

MONEY_PREFIX = "UN$"
    
TRANSACTION_MANUAL = 1
TRANSACTION_BUY = 2
TRANSACTION_SELL = 3

class Transaction:
    def __init__(self, ty, timestamp, *, comment=None, amount=None, btype=None, count=None):
        if ty == TRANSACTION_MANUAL:
            assert comment != None, "Comment on manual transaction must not be None"
            assert amount != None, "Amount on manual transaction must not be None"
        else:
            assert btype != None, "Building type on auto transaction must not be None"
            assert count != None, "Count on auto transaction must not be None"

        self.amount = amount
        self.comment = comment
        self.trans_type = ty
        self.btype = btype
        self.count = count
        self.timestamp = timestamp
    
    def serialise(self):
        if self.trans_type == TRANSACTION_MANUAL:
            return {"amount": self.amount, "comment": self.comment, "type": self.trans_type, "timestamp": self.timestamp}
        else:
            return {"count": self.count, "btype": self.btype, "type": self.trans_type, "timestamp": self.timestamp}

    def deserialise(object):
        if object["type"] == TRANSACTION_MANUAL:
            return Transaction(object["type"], object["timestamp"], amount=object["amount"], comment=object["comment"])
        else:
            return Transaction(object["type"], object["timestamp"], btype=object["btype"], count=object["count"])
            
    def compute_amount(self) -> int:
        if self.trans_type == TRANSACTION_MANUAL:
            return self.amount
        elif self.trans_type == TRANSACTION_BUY:
            return -BUILDING_INFO[self.btype].cost * self.count
        elif self.trans_type == TRANSACTION_SELL:
            return BUILDING_INFO[self.btype].cost * self.count
            
    def compute_comment(self):
        if self.trans_type == TRANSACTION_MANUAL:
            return self.comment
        elif self.trans_type == TRANSACTION_BUY:
            return f"Bought {self.count}x {BUILDING_INFO[self.btype].name}"
        elif self.trans_type == TRANSACTION_SELL:
            return f"Sold {self.count}x {BUILDING_INFO[self.btype].name}"

data = {
    "regions": {},
    "transactions": []
}

if os.path.exists("economy.json"):
    with open("economy.json", "r") as f:
        raw_data = json.load(f)
        
    for reg in raw_data["regions"]:
        data["regions"][reg] = {"buildings": []]
        for b in raw_data["regions"][reg]["buildings"]:
            data["regions"][reg]["buildings"].append(Building.deserialise(b))
            
    data["transactions"] = [Transaction.deserialise(t) for t in raw_data["transactions"]]
    
def save():
    ser_data = {"regions": data["regions"], "transactions": []}
    for t in data["transactions"]:
        ser_data["transactions"].append(t.serialise())
    with open("economy.json", "w") as f:
        f.write(json.dumps(ser_data, indent=4))

def format_date(timestamp):
    return datetime.date.fromtimestamp(timestamp).strftime("%d/%m/%Y")

def format_money(amt):
    return MONEY_PREFIX + str(round(amt, 2))

def send_info_popup(txt):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(txt)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

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
        self.b_add   = QtWidgets.QPushButton("Add", self)
        self.l_compcost = QtWidgets.QLineEdit(self)
        self.l_compincome = QtWidgets.QLineEdit(self)
        
        self.l_btype = QtWidgets.QLabel("Building type")
        self.l_count = QtWidgets.QLabel("Count")
        self.l_cost  = QtWidgets.QLabel("Cost")
        self.l_income= QtWidgets.QLabel("Income")
        
        self.spacer = QtWidgets.QLabel("", self)
        
        self.layout.addWidget(self.region_select, 0, 0)
        self.layout.addWidget(self.e_newregion, 0, 1)
        self.layout.addWidget(self.b_newregion, 0, 2)
        self.layout.addWidget(self.b_delregion, 0, 3)
        self.layout.addWidget(self.l_btype, 1, 0)
        self.layout.addWidget(self.l_count, 1, 1)
        self.layout.addWidget(self.l_income, 1, 2)
        self.layout.addWidget(self.l_cost, 1, 3)
        self.layout.addWidget(self.type_selector, 2, 0)
        self.layout.addWidget(self.e_count, 2, 1)
        self.layout.addWidget(self.l_compincome, 2, 2)
        self.layout.addWidget(self.l_compcost, 2, 3)
        self.layout.addWidget(self.b_add, 2, 4)
        self.layout.addWidget(self.building_list, 3, 0, 1, 5)
        self.layout.addWidget(self.spacer, 4, 0, 1, 5)
        self.layout.setRowStretch(4, 1)
        self.setLayout(self.layout)
        
        self.l_compcost.setReadOnly(True)
        self.l_compincome.setReadOnly(True)
        self.type_selector.activated[str].connect(lambda t: self.recalc_preview())
        self.e_count.valueChanged[int].connect(lambda n: self.recalc_preview())
        self.b_add.clicked.connect(self.add_building)
        self.b_newregion.clicked.connect(self.add_region)
        self.b_delregion.clicked.connect(self.del_region)
        self.region_select.activated[str].connect(lambda r: self.region_change())
        self.building_list.building_count_decrease[BuildingEntry].connect(self.remove_building)
        self.recalc_preview()
        self.region_change()

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
        
        for building, count in building_nums:
            self.building_list.add_building(building, count)
        
    def recalc_preview(self):
        btype = self.type_selector.currentData()
        count = self.e_count.value()
        binfo = BUILDING_INFO[btype]
        income = binfo.employees * binfo.wage * 8 * count
        self.l_compcost.setText(format_money(binfo.cost * count))
        self.l_compincome.setText(format_money(income))
    
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
        count = self.e_count.value()
        if not btype in self.buildings:
            self.buildings[btype] = 0
            self.building_list.add_building(btype, 0)
        self.buildings[btype] += count
        self.building_list.update_building(btype, self.buildings[btype])
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()
        
        self.parent.transactions_tab.add_transaction(Transaction(
            TRANSACTION_BUY,
            datetime.datetime.now().timestamp(),
            btype=btype,
            count=count
        ))

    def remove_building(self, entry):
        if not self.check_real_region():
            return

        btype = entry.b_type
        count = entry.count
        if count <= 1:
            del self.buildings[btype]
            self.building_list.remove_building(btype)
        else:
            self.buildings[btype] -= 1
            self.building_list.update_building(btype, self.buildings[btype])
        
        self.parent.transactions_tab.add_transaction(Transaction(
            TRANSACTION_SELL,
            datetime.datetime.now().timestamp(),
            btype=btype,
            count=1,
        ))
        
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()

class KeybindTable(QtWidgets.QTableWidget):
    keyPressed = Qt.pyqtSignal(QtGui.QKeyEvent)
    def keyPressEvent(self, event):    
        if type(event) == QtGui.QKeyEvent:
            self.keyPressed.emit(event)

class TransactionsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        
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
        
        self.e_amount.setPlaceholderText("Amount")
        self.e_comment.setPlaceholderText("Comment")
        
        self.layout.addWidget(self.table, 1, 0, 1, 3)
        self.layout.addWidget(self.e_amount, 0, 0)
        self.layout.addWidget(self.e_comment, 0, 1)
        self.layout.addWidget(self.b_add, 0, 2)
        self.layout.addWidget(self.l_bal, 2, 0)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)
        
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
        
        date = datetime.datetime.now().timestamp()
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
        self.l_bal.setText("Balance: " + format_money(bal))

class StatsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.transactions_tab = TransactionsTab(self)
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(BuildingsTab(self), "Buildings")
        self.tab_widget.addTab(self.transactions_tab, "Transactions")
        self.tab_widget.addTab(StatsTab(self), "Stats")
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
