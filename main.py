from PyQt5 import QtWidgets, QtCore, Qt
import sys
import json
import traceback
import os
import datetime
import re



BUILDING_INFO = {
    RAILWAY_STATION       : (13.5,  2,     4968,     "Railway Station"),
    MARKET_STALL          : (11,    1,     2024.00,  "Market Stall"),
    POLICE_STATION        : (19.6,  3,     10819.20, "Police Station"),
    POST_OFFICE           : (12.5,  2,     4600.00,  "Post Office"),
    SMALL_STORE           : (11.5,  2,     4232.00,  "Small Store/Fuel Station"),
    HOSPITAL              : (26,    3,     14352.00, "Hospital"),
    FIRE_STATION          : (19,    2,     6992.00,  "Fire station"),
    SUPER_STORE           : (12.2,  4,     8979.20,  "Super Store"),
    PIER                  : (14,    1,     2576.00,  "Pier"),
    DOCK                  : (15.8,  2,     5814.40,  "Dock per 10 blocks"),
    QUARRY                : (11.2,  2,     4121.60,  "Quarries Per Chunk"),
    SMALL_FACTORY         : (14.5,  6,     16008.00, "Small Factory"),
    LARGE_FACTORY         : (15.5,  12,    34224.00, "Large Factory"),
    FARMING               : (18.5,  1/162, 21.01,    "Farming per block"),
    NAVAL_DOCKYARD        : (15.5,  1,     2852.00,  "Naval dockyard per 7 blocks"),
    MILLS                 : (12,    0,     36500.00, "MiLLs"),
    AIRBASE               : (17.5,  4,     12880.00, "Airbase"),
    SUPPLY_HUB            : (10.5,  1,     1932.00,  "Supply hub"),
    REACTOR               : (20.5,  3,     11316.00, "Nuclear/biogas reactor"),
    ELECTRICAL_GENERATION : (12.5,  2,     4600.00,  "Electrical generation/storage"),
    AIRPORT               : (18,    0,     69,       "Airport"),
}
MONEY_PREFIX = "UN$"

if os.path.exists("economy.json"):
    with open("economy.json", "r") as f:
        data = json.load(f)
else:
    data = {
        "regions": {},
        "transactions": []
    }

# TODO
# check region name before creating (duplicates)
# auto change transactions based on price changes
def save():
    with open("economy.json", "w") as f:
        f.write(json.dumps(data, indent=4))

def format_date(timestamp):
    return datetime.date.fromtimestamp(timestamp).strftime("%d/%m/%Y")

def format_money(amt):
    return MONEY_PREFIX + str(round(amt, 2))
class BuildingEntry(Qt.QObject):
    decrease = Qt.pyqtSignal()
    def __init__(self, b_type, count, parent):
        super().__init__()
        self.b_type = b_type
        self.count = count

        self.l_type = QtWidgets.QLabel(b_type, parent)
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
        self.l_cost.setText(format_money(BUILDING_INFO[self.b_type][2] * count))
        self.l_count.setText(str(count))
        self.l_income.setText(format_money(BUILDING_INFO[self.b_type][0] * BUILDING_INFO[self.b_type][1] * count * 8))
        self.l_employed.setText(str(round(BUILDING_INFO[self.b_type][1] * count, 3)))
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

    def add_building(self, b_type, count):
        item = BuildingEntry(b_type, count, self)
        self.items.append(item)
        idx = len(self.items)
        item.insert(self.layout, idx)
        item.decrease.connect(lambda: self.building_count_decrease.emit(item))
    
    def remove_building(self, b_type):
        item = None
        for n in self.items:
            if n.b_type == b_type:
                item = n
        if item != None:        
            item.remove(self.layout)
            self.items.remove(item)
        else:
            raise RuntimeWarning("BuildingList.remove_building called on non-existent building")

    def update_building(self, b_type, count):
        for n in self.items:
            if n.b_type == b_type:
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

        self.buildings = {}
        self.building_list = BuildingList(self)
        
        self.layout = QtWidgets.QGridLayout(self)
        
        self.type_selector = QtWidgets.QComboBox(self)
        for building in BUILDING_INFO.keys():
            self.type_selector.addItem(building)

        self.e_count = QtWidgets.QSpinBox(self)
        self.e_count.setValue(1)
        self.b_add   = QtWidgets.QPushButton("Add", self)
        self.l_compcost = QtWidgets.QLineEdit(self)
        self.l_compincome = QtWidgets.QLineEdit(self)
        
        self.l_btype = QtWidgets.QLabel("Building type")
        self.l_count = QtWidgets.QLabel("Count")
        self.l_cost  = QtWidgets.QLabel("Cost")
        self.l_income= QtWidgets.QLabel("Income")
        
        self.b_autopay = QtWidgets.QCheckBox("Auto-pay", self)
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
        self.layout.addWidget(self.b_autopay, 2, 5)
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
        self.region_select.activated[str].connect(lambda r: self.region_change())
        self.building_list.building_count_decrease[BuildingEntry].connect(self.remove_building)
        self.recalc_preview()
        self.region_change()

    def add_region(self):
        region = self.e_newregion.text()
        self.region_select.addItem(region)
        data["regions"][region] = {"buildings": {}}
        save()

    def region_change(self):
        self.curr_region = self.region_select.currentText()
        print(data["regions"])

        self.building_list.clear()
        self.buildings = {}
        if self.curr_region == "Total":
            for region in data["regions"].values():
                for bname, count in region["buildings"].items():
                    if not bname in self.buildings:
                        self.buildings[bname] = 0
                    self.buildings[bname] += count
        else:
            self.buildings = data["regions"][self.curr_region]["buildings"]

        for building, count in self.buildings.items():
            self.building_list.add_building(building, count)
        

    def recalc_preview(self):
        item = self.type_selector.currentText()
        count = self.e_count.value()
        building = BUILDING_INFO[item]
        income = building[1] * building[0] * 8 * count
        self.l_compcost.setText(format_money(building[2] * count))
        self.l_compincome.setText(format_money(income))
    
    def check_real_region(self):
        """check the current region is not 'Total'. If it is, warn the user
        returns whether a real region was selected"""
        if self.curr_region == "Total":
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Select a region before adding a building")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return False
        return True

    def add_building(self):
        if not self.check_real_region():
            return

        item = self.type_selector.currentText()
        count = self.e_count.value()
        if not item in self.buildings:
            self.buildings[item] = 0
            self.building_list.add_building(item, 0)
        self.buildings[item] += count
        self.building_list.update_building(item, self.buildings[item])
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()
        
        if self.b_autopay.isChecked():
            self.parent.transactions_tab.add_transaction(
                -BUILDING_INFO[item][2] * count,
                datetime.datetime.now().timestamp(),
                f"Bought {count}x {item}")
    
    def remove_building(self, entry):
        if not self.check_real_region():
            return

        item = entry.b_type
        count = entry.count
        if count <= 1:
            del self.buildings[item]
            self.building_list.remove_building(item)
        else:
            self.buildings[item] -= 1
            self.building_list.update_building(item, self.buildings[item])
        
        if self.b_autopay.isChecked():
            # TODO append to prev transaction
            # "Sold ([0-9]+)x {name}"
            self.parent.transactions_tab.add_transaction(
                BUILDING_INFO[item][2],
                datetime.datetime.now().timestamp(),
                f"Sold 1x {item}"
            )
        
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()

class TransactionsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QtWidgets.QGridLayout(self)
        self.entry_layout = QtWidgets.QGridLayout(self)
        
        
        self.e_amount = QtWidgets.QLineEdit(self)
        self.e_comment= QtWidgets.QLineEdit(self)
        self.l_amount = QtWidgets.QLabel("Amount", self)
        self.l_comment= QtWidgets.QLabel("Comment", self)
        self.l_date   = QtWidgets.QLabel("Date", self)
        self.b_add    = QtWidgets.QPushButton("Add", self)
        self.spacer   = QtWidgets.QLabel("", self)
        
        self.layout.addWidget(self.l_amount, 0, 0)
        self.layout.addWidget(self.l_date, 0, 1)
        self.layout.addWidget(self.l_comment, 0, 2)
        self.layout.addWidget(self.e_amount, 1, 0)
        self.layout.addWidget(self.spacer, 20000, 0) # hacky trick to keep it at the bottom
        self.entry_layout.addWidget(self.e_comment, 0, 0)
        self.entry_layout.addWidget(self.b_add, 0, 1)
        self.entry_layout.setColumnStretch(0, 1)
        self.layout.addLayout(self.entry_layout, 1, 2)
        self.layout.setColumnStretch(2, 1)
        self.layout.setRowStretch(200000, 1)
        self.setLayout(self.layout)
        
        self.b_add.clicked.connect(self._add_transaction_button)
        
        self.transaction_widgets = []
        
    def _add_transaction_button(self):
        try:
            amount = round(float(self.e_amount.text()), 2)
        except ValueError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Enter a valid number for the amount (without any $ or £)")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return
        
        date = datetime.datetime.now().timestamp()
        comment = self.e_comment.text()
        self.add_transaction(amount, date, comment)
    
    def add_transaction(self, amount, date, comment):
        data["transactions"].append((amount, date, comment))
        save()
 
        self.transaction_widgets.append((
            QtWidgets.QLabel(MONEY_PREFIX + str(amount), self),
            QtWidgets.QLabel(format_date(date), self),
            QtWidgets.QLabel(comment, self)))
        
        idx = len(self.transaction_widgets) + 1
        self.layout.addWidget(self.transaction_widgets[-1][0], idx, 0)
        self.layout.addWidget(self.transaction_widgets[-1][1], idx, 1)
        self.layout.addWidget(self.transaction_widgets[-1][2], idx, 2)
        
        self._recalc_balance()
        
    def _recalc_balance(self):
        bal = 0
        for t in data["transactions"]:
            bal += t[0]
        data["bal"] = bal

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
