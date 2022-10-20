from PyQt5 import QtWidgets, QtCore
import sys
import json
import traceback

BUILDING_INFO = {
    "Railway Station"               : (13.5,  2,     4968),
    "Market Stall"                  : (11,    1,     2024.00),
    "Police Station"                : (19.6,  3,     10819.20),
    "Post Office"                   : (12.5,  2,     4600.00),
    "Small Store/Fuel Station"      : (11.5,  2,     4232.00),
    "Hospital"                      : (26,    3,     14352.00),
    "Fire station"                  : (19,    2,     6992.00),
    "Super Store"                   : (12.2,  4,     8979.20),
    "Pier"                          : (14,    1,     2576.00),
    "Dock per 10 blocks"            : (15.8,  2,     5814.40),
    "Quarries Per Chunk"            : (11.2,  2,     4121.60),
    "Small Factory"                 : (14.5,  6,     16008.00),
    "Large Factory"                 : (15.5,  12,    34224.00),
    "Farming 162 block"             : (18.5,  1/162, 21.01),
    "Naval dockyard per 7 blocks"   : (15.5,  1,     2852.00),
    "MiLLs"                         : (12,    0,     36500.00),
    "Airbase"                       : (17.5,  4,     12880.00),
    "Supply hub"                    : (10.5,  1,     1932.00),
    "Nuclear/biogas reactor"        : (20.5,  3,     11316.00),
    "Electrical generation/storage" : (12.5,  2,     4600.00),
}
MONEY_PREFIX = "UN$"

data = {
    "regions": {},
    "bal": 0,
    "withdrawals": [],
    "deposits": [],
}

class BuildingEntry:
    def __init__(self, b_type, count, parent):
        self.b_type = b_type
        self.count = count

        self.l_type = QtWidgets.QLabel(b_type, parent)
        self.l_count = QtWidgets.QLabel(parent)
        self.l_employed = QtWidgets.QLabel(parent)
        self.l_income = QtWidgets.QLabel(parent)
        self.l_cost = QtWidgets.QLabel(parent)
        
        self.update_count(self.count)
        
    def update_count(self, count):
        self.l_cost.setText(MONEY_PREFIX + str(BUILDING_INFO[self.b_type][2] * count))
        self.l_count.setText(str(count))
        self.l_income.setText(MONEY_PREFIX + str(BUILDING_INFO[self.b_type][0] * BUILDING_INFO[self.b_type][1] * count * 8))
        self.l_employed.setText(str(BUILDING_INFO[self.b_type][1] * count))
        self.count = count
        
    def remove(self, layout):
        layout.removeWidget(self.l_type)
        layout.removeWidget(self.l_count)
        layout.removeWidget(self.l_employed)
        layout.removeWidget(self.l_income)
        layout.removeWidget(self.l_cost)
        self.l_type.deleteLater()
        self.l_count.deleteLater()
        self.l_employed.deleteLater()
        self.l_income.deleteLater()
        self.l_cost.deleteLater()
        self.l_type = None
        self.l_count = None
        self.l_employed = None
        self.l_income = None
        self.l_cost = None

class BuildingList(QtWidgets.QWidget):
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
        self.layout.addWidget(item.l_type, idx, 0)
        self.layout.addWidget(item.l_count, idx, 1)
        self.layout.addWidget(item.l_employed, idx, 2)
        self.layout.addWidget(item.l_income, idx, 3)
        self.layout.addWidget(item.l_cost, idx, 4)

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
        
        self.layout.addWidget(self.region_select, 0, 0)
        self.layout.addWidget(self.e_newregion, 0, 1)
        self.layout.addWidget(self.b_newregion, 0, 2)
        self.layout.addWidget(self.b_delregion, 0, 3)
        self.layout.addWidget(self.l_btype, 1, 0)
        self.layout.addWidget(self.l_count, 1, 1)
        self.layout.addWidget(self.l_cost, 1, 2)
        self.layout.addWidget(self.l_income, 1, 3)
        self.layout.addWidget(self.type_selector, 2, 0)
        self.layout.addWidget(self.e_count, 2, 1)
        self.layout.addWidget(self.l_compcost, 2, 2)
        self.layout.addWidget(self.l_compincome, 2, 3)
        self.layout.addWidget(self.b_add, 2, 4)
        self.layout.addWidget(self.building_list, 3, 0, 1, 5)
        self.setLayout(self.layout)
        
        self.l_compcost.setReadOnly(True)
        self.l_compincome.setReadOnly(True)
        self.type_selector.activated[str].connect(lambda t: self.recalc_preview())
        self.e_count.valueChanged[int].connect(lambda n: self.recalc_preview())
        self.b_add.clicked.connect(self.add_building)
        self.b_newregion.clicked.connect(self.add_region)
        self.region_select.activated[str].connect(lambda r: self.region_change())
        self.recalc_preview()
        self.region_change()

    def add_region(self):
        region = self.e_newregion.text()
        self.region_select.addItem(region)
        data["regions"][region] = {"buildings": {}}

    def region_change(self):
        self.curr_region = self.region_select.currentText()

        self.building_list.clear()
        self.buildings.clear()
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
        self.l_compcost.setText(MONEY_PREFIX + str(building[2] * count))
        self.l_compincome.setText(MONEY_PREFIX + str(income))
        
    def add_building(self):
        if self.curr_region == "Total":
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Select a region before adding a building")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            return

        item = self.type_selector.currentText()
        count = self.e_count.value()
        if not item in self.buildings:
            self.buildings[item] = 0
            self.building_list.add_building(item, 0)
        self.buildings[item] += count
        self.building_list.update_building(item, self.buildings[item])
        data["regions"][self.curr_region]["buildings"] = self.buildings

class AirportsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

class HousingTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(BuildingsTab(self), "Buildings")
        self.tab_widget.addTab(AirportsTab(self), "Airports")
        self.tab_widget.addTab(HousingTab(self), "Housing")
        self.tab_widget.addTab(StatsTab(self), "Stats")
        self.tab_widget.addTab(PriceTab(self), "Price")
        self.layout.addWidget(self.tab_widget)
        self.setLayout(self.layout)



def exception_hook(exctype, value, tb):
    traceback_formated = traceback.format_exception(exctype, value, tb)
    traceback_string = "".join(traceback_formated)
    print("Excepthook called, saving and quiteing...")
    print(traceback_string, file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    sys.excepthook = exception_hook
    app = QtWidgets.QApplication(sys.argv)
    ex = Main()
    sys.exit(app.exec_())
