from PyQt5 import QtWidgets, Qt
from data import *
from building_list import BuildingList, BuildingEntry
from constants import BUILDING_INFO
from building import Building
from transaction import Transaction, TransactionType

def send_info_popup(txt):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(txt)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

class BuildingsTab(QtWidgets.QWidget):
    region_changed = Qt.pyqtSignal(str)
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.data = data
        
        self.region_select = QtWidgets.QComboBox(self)
        self.e_newregion = QtWidgets.QLineEdit(self)
        self.b_newregion = QtWidgets.QPushButton("New region", self)
        self.b_delregion = QtWidgets.QPushButton("Delete region", self)
        
        self.region_select.addItem("Total")
        for region in data.regions.keys():
            self.region_select.addItem(region)

        self.buildings = []
        self.building_list = BuildingList(self)
        
        self.layout = QtWidgets.QGridLayout(self)
        
        self.type_selector = QtWidgets.QComboBox(self)
        for btype, binfo in sorted(BUILDING_INFO.items(), key=lambda n: n[1].name):
            self.type_selector.addItem(binfo.name, userData=btype)
        self.type_selector.setMaxVisibleItems(len(BUILDING_INFO))
        
        self.e_count = QtWidgets.QSpinBox(self)
        self.e_count.setValue(1)
        self.e_count.setMaximum(99999)
        self.e_size  = QtWidgets.QSpinBox(self)
        self.e_size.setMaximum(999)
        self.e_size.hide()
        self.b_add   = QtWidgets.QPushButton("Add", self)
        self.l_compcost = QtWidgets.QLabel(self)
        self.l_compincome = QtWidgets.QLabel(self)
        self.l_compemployees=QtWidgets.QLabel(self)
        
        self.l_btype = QtWidgets.QLabel("Building type")
        self.l_count = QtWidgets.QLabel("Count")
        self.l_cost  = QtWidgets.QLabel("Cost")
        self.l_income= QtWidgets.QLabel("Income")
        self.l_employees=QtWidgets.QLabel("Employees")
        self.l_size  = QtWidgets.QLabel("Size")
        
        self.l_proj_bal = QtWidgets.QLabel(self)
        self.l_proj_income = QtWidgets.QLabel(self)
        self.l_proj_employ = QtWidgets.QLabel(self)
        
        self.spacer = QtWidgets.QLabel("", self)
        
        self.layout.addWidget(self.region_select, 0, 0)
        self.layout.addWidget(self.e_newregion,   0, 1)
        self.layout.addWidget(self.b_newregion,   0, 2)
        self.layout.addWidget(self.b_delregion,   0, 3)
        self.layout.addWidget(self.l_btype,       1, 0)
        self.layout.addWidget(self.l_count,       1, 1)
        self.layout.addWidget(self.l_income,      1, 2)
        self.layout.addWidget(self.l_cost,        1, 3)
        self.layout.addWidget(self.l_employees,   1, 4)
        self.layout.addWidget(self.l_size,        1, 5)
        self.layout.addWidget(self.type_selector, 2, 0)
        self.layout.addWidget(self.e_count,       2, 1)
        self.layout.addWidget(self.l_compincome,  2, 2)
        self.layout.addWidget(self.l_compcost,    2, 3)
        self.layout.addWidget(self.l_compemployees, 2, 4)
        self.layout.addWidget(self.e_size,        2, 5)
        self.layout.addWidget(self.b_add,         2, 6)
        
        self.layout.addWidget(self.l_proj_bal,    3, 0)
        self.layout.addWidget(self.l_proj_income, 3, 1)
        self.layout.addWidget(self.l_proj_employ, 3, 2)
        
        self.layout.addWidget(self.building_list, 4, 0, 1, 7)
        self.layout.addWidget(self.spacer,        5, 0, 1, 7)
        self.layout.setRowStretch(5, 1)
        self.setLayout(self.layout)
        
        self.type_selector.activated[str].connect(lambda t: self.recalc_preview())
        self.e_count.valueChanged[int].connect(lambda n: self.recalc_preview())
        self.e_size.valueChanged[int].connect(lambda s: self.recalc_preview())
        self.b_add.clicked.connect(self.add_building)
        self.b_newregion.clicked.connect(self.add_region)
        self.b_delregion.clicked.connect(self.del_region)
        self.region_select.activated[str].connect(lambda r: self.region_change())
        self.building_list.building_count_decrease[BuildingEntry].connect(self.remove_building)
        self.region_change()
        self.recalc_preview()
        
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
        self.data.add_region(region)
        self.data.save()
    
    def del_region(self):
        if not self.check_real_region():
            return

        region = self.region_select.currentText()
        reply = QtWidgets.QMessageBox.question(self, f"Delete region", "Really delete region '{region}'? The buildings won't be transferred.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.No:
            return
            
        self.data.remove_region(region)
        self.data.save()
        self.region_select.removeItem(self.region_select.currentIndex())

    def region_change(self):
        self.curr_region = self.region_select.currentText()

        self.building_list.clear()
        self.buildings = []
        if self.curr_region == "Total":
            for region in self.data.regions.values():
                for building in region:
                    self.buildings.append(building)
        else:
            self.buildings = self.data.regions[self.curr_region]
        
        building_nums = []
        for building in self.buildings:
            bid = (building.btype, building.size)
            if not (building.btype, building.size) in [(b[0].btype, b[0].size) for b in building_nums]:
                building_nums.append([building, 0])
                idx = len(building_nums) - 1
            else:
                idx = [i for i, b in enumerate(building_nums) if b[0].is_roughly(building)][0]
            building_nums[idx][1] += building.count
        
        for building, count in building_nums:
            self.building_list.add_building(building, count)
        
        self.recalc_preview()
        self.region_changed.emit(self.curr_region)
        
    def recalc_preview(self):
        btype = self.type_selector.currentData()
        count = self.e_count.value()
        if btype == BType.HOUSE or btype == BType.AIRPORT:
            self.e_size.show()
            self.l_size.show()
            size = self.e_size.value()
            building = Building(btype, self.data.current_day, Building.get_lorentz(self.data.eco_cache), size, count=count)
            if btype == BType.HOUSE and not size in [1, 2, 4, 6]: # perhaps the size is not valid yet, let's just ignore that
                self.l_compcost.setText("Invalid size")
                self.l_compincome.setText("Invalid size")
                return
        else:
            self.e_size.hide()
            self.l_size.hide()
            building = Building(btype, self.data.current_day, Building.get_lorentz(self.data.eco_cache), count=count)
 
        income = building.income()
        self.l_compcost.setText(format_money(building.cost(l=Building.get_lorentz(self.data.eco_cache))))
        self.l_compincome.setText(format_money(income))
        self.l_compemployees.setText(str(round(building.employees() * count, 3)))
        
        if self.curr_region == "Total":
            self.l_proj_bal.hide()
            self.l_proj_income.hide()
            self.l_proj_employ.hide()
            return
            
        self.l_proj_bal.show()
        self.l_proj_income.show()
        self.l_proj_employ.show()
        self.data.regions[self.curr_region].append(building)
                
        self.l_proj_bal.setText("Projected bal: " + format_money(calc_bal(self.data) - building.cost(l=Building.get_lorentz(self.data.eco_cache))))
        self.l_proj_income.setText("Projected income: " + format_money(calc_income(self.data)[0]))
        self.l_proj_employ.setText("Projected employment: " + str(round(calc_employment(self.data) * 100, 1)) + "%")
        
        self.data.regions[self.curr_region].pop()
    
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
        if btype == BType.AIRPORT or btype == BType.HOUSE:
            building = Building(btype, self.data.current_day, Building.get_lorentz(self.data.eco_cache), self.e_size.value(), count=count)
        else:
            building = Building(btype, self.data.current_day, Building.get_lorentz(self.data.eco_cache), count=count)

        if not (building.btype, building.size) in [(b.btype, b.size) for b in self.buildings]:
            self.building_list.add_building(building, 0)
        
        self.buildings.append(building)

        self.building_list.update_building(building, sum([b.count for b in self.buildings if b.is_roughly(building)]))
        self.data.regions[self.curr_region] = self.buildings
        self.data.save()
        
        self.parent.transactions_tab.add_transaction(Transaction(
            TransactionType.BUY,
            self.data.current_day.isoformat(),
            buildings=[building],
        ))
        
    def remove_building(self, entry: BuildingEntry):
        if not self.check_real_region():
            return

        count, ok = QtWidgets.QInputDialog.getInt(self, "Sell building", "How many " + entry.building.name() + "s do you want to sell?", 1, 1, entry.count)
        if not ok:
            return

        correct_types = [b for b in self.buildings if b.btype == entry.building.btype and b.size == entry.building.size]
        correct_types = sorted(correct_types, key=lambda b: -b.lorentz)
        buildings = []
        for b in correct_types[:count]:
            self.buildings.remove(b)
            buildings.append(b)
        
        if entry.count <= count:
            self.building_list.remove_building(buildings[0])
        else:
            self.building_list.update_building(buildings[0], len([1 for b in self.buildings if b.is_roughly(buildings[0])]))

        last_t = data["transactions"][-1]
        if False and last_t.trans_type == TransactionType.BUY and last_t.building == building and last_t.count >= count:
            # update/cancel out last transaction instead
            if last_t.count == count:
                # get rid entirely
                data["transactions"].pop(-1)
                self.parent.transactions_tab.table.removeRow(len(data["transactions"]))
            else:
                last_t.count -= count
                self.parent.transactions_tab.set_row_to(len(data["transactions"]) - 1, last_t)

        else:
            self.parent.transactions_tab.add_transaction(Transaction(
                TransactionType.SELL,
                data["current_day"].isoformat(),
                buildings=buildings,
            ))
        
        data["regions"][self.curr_region]["buildings"] = self.buildings
        save()
        self.recalc_preview()