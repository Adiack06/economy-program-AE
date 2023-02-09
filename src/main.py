from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
# TODO
# display bal after hypothetical buying thing
# edit transactions

from PyQt5 import QtCore, Qt, QtGui
import numpy as np
import sys
import json
import traceback
import os
import datetime
import re
import requests
import time # DEBUG
sys.path.append("src")
from typing import Union
from building import *
from constants import *
from data import *
from transaction import Transaction, TransactionType
from buildings_tab import BuildingsTab

MY_VERSION = "1.3.2"

# really bad idea tbh
# try to guess the location of economy.json
# by looking at our cwd. if we're still in src
# then it's in ..
# else, assume it's in .
if os.path.basename(os.getcwd()) == "src":
    BACKUP_DIR = os.path.join("..", "backups")
    ECONOMY_FILE = os.path.join("..", "economy.json")
else:
    BACKUP_DIR = "backups"
    ECONOMY_FILE = "economy.json"

class Data:
    def __init__(self):
        self.regions = {}
        self.transactions = []
        self.current_day = None
        self.loans = []
        self.eco_cache = 0

    def set_defaults(self):
        self.transactions.append(Transaction(TransactionType.MANUAL, datetime.date(2022, 10, 10).isoformat(), amount=40000, comment="Initial balance"))
        self.current_day = datetime.date(2022, 10, 10)

    def read_from_file(self, fname):
        with open(fname, "r") as f:
            raw_data = json.loads(f.read())

        self.current_day = datetime.date.fromisoformat(raw_data["current_day"])
        
        for reg in raw_data["regions"]:
            self.regions[reg] = []
            for b in raw_data["regions"][reg]["buildings"]:
                self.regions[reg].append(self.deserialise_building(b))
        
        self.transactions = [self.deserialise_transaction(t) for t in raw_data["transactions"]]
        self.loans = raw_data.get("loans", [])
        self.eco_cache = calc_income(self)[0]

    def write_to_file(self, fname):
        raw_data = {"current_day": self.current_day.isoformat(),
                    "regions": {r: {"buildings": [self.serialise_building(b) for b in self.regions[r]]} for r in self.regions},
                    "loans": self.loans,
                    "transactions": [self.serialise_transaction(t) for t in self.transactions]}
        
        with open(fname, "w") as f:
            f.write(json.dumps(raw_data))

    def serialise_building(self, b):
        # either [type, size, lorentz] if only one
        # or [type, size, lorentz, count] if run length encoded
        if b.count == 1:
            return [b.btype, b.size, b.lorentz]
        else:
            return [b.btype, b.size, b.lorentz, b.count]
            
    def deserialise_building(self, obj, lorentz: float=None):
        if lorentz is None:
            lorentz = 1
        # old serialised buildings are either a list of [type, size]
        # or just a single int type. New serialised buildings are always
        # a list of [type, size, lorentz] to avoid ambiguity.
        # this is actually a lie now, *new* new buildings are either a 
        # [type, size, lorentz] or a [type, size, lorentz, count]
        # for run length encoding
        if type(obj) == list:
            if len(obj) == 2: # old building, type and size
                return Building(obj[0], self.current_day, lorentz, obj[1])
            elif len(obj) == 3: # new building, type size and lorentz
                return Building(obj[0], self.current_day, obj[2], obj[1])
            elif len(obj) == 4: # new new buildig, (type, size, lorentz, count)
                return Building(obj[0], self.current_day, obj[2]. obj[1], count=obj[3])
        else: # old building, just type
            return Building(obj, self.current_day, lorentz)

    def serialise_transaction(self, trans):
        if trans.trans_type == TransactionType.MANUAL:
            return {"amount": trans.amount,
                    "comment": trans.comment,
                    "type": trans.trans_type,
                    "timestamp": trans.timestamp}
        else:
            return {"buildings": [self.serialise_building(b) for b in trans.buildings],
                    "type": trans.trans_type,
                    "timestamp": trans.timestamp}

    def deserialise_transaction(self, object):
        if object["type"] == TransactionType.MANUAL:
            return Transaction(object["type"], object["timestamp"], amount=object["amount"], comment=object["comment"])
        else:
            if object.get("buildings") == None: # old transaction, assume one building + count (+ lorentz)
                buildings = [self.deserialise_building(object["building"], lorentz=object.get("lorentz"))] * object["count"]
                return Transaction(object["type"], object["timestamp"], buildings=buildings)
            else: # new transaction, deserialise list of buildings with one lorentz each
                return Transaction(object["type"], object["timestamp"], buildings=[self.deserialise_building(i) for i in object["buildings"]])
 
    def save(self):
        self.write_to_file(ECONOMY_FILE)

    def add_region(self, reg_name):
        self.regions[reg_name] = []

    def remove_region(self, reg_name):
        del self.regions[reg_name]


def update_backup_formats():
    """Load and save every backup and the economy file,
       which should save every file in the latest format"""

    if not os.path.isdir(BACKUP_DIR):
        return
    
    for fname in os.listdir(BACKUP_DIR):
        newdata = Data()
        newdata.read_from_file(os.path.join(BACKUP_DIR, fname))
        newdata.write_to_file(os.path.join(BACKUP_DIR, fname))

    newdata = Data()
    newdata.read_from_file(ECONOMY_FILE)
    newdata.write_to_file(ECONOMY_FILE)

def get_historical_datas(data):
    """Return a list of backups, plus the current data"""
    if not os.path.isdir(BACKUP_DIR):
        return []
    
    datas = []
    for fname in os.listdir(BACKUP_DIR):
        newdata = Data()
        newdata.read_from_file(os.path.join(BACKUP_DIR, fname))
        datas.append(newdata)
    
    datas.append(data)
    return datas

def send_info_popup(txt):
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(txt)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()

class KeybindTable(QtWidgets.QTableWidget):
    keyPressed = Qt.pyqtSignal(QtGui.QKeyEvent)
    def keyPressEvent(self, event):    
        if type(event) == QtGui.QKeyEvent:
            self.keyPressed.emit(event)

class TransactionsTab(QtWidgets.QWidget):
    recalculate = Qt.pyqtSignal()
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.data = data
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

        self.e_amount.setPlaceholderText("Amount")
        self.e_comment.setPlaceholderText("Comment")
        
        self.layout.addWidget(self.table, 1, 0, 1, 3)
        self.layout.addWidget(self.e_amount, 0, 0)
        self.layout.addWidget(self.e_comment, 0, 1)
        self.layout.addWidget(self.b_add, 0, 2)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)
        
        self.b_add.clicked.connect(self._add_transaction_button)
        self.table.keyPressed[QtGui.QKeyEvent].connect(self._table_keypress)
        
        self.transaction_widgets = []
        
        for t in data.transactions:
            self._add_transaction_to_table(t)
        self.recalculate.emit()
        
    def _table_keypress(self, event):
        if event.key() == QtCore.Qt.Key_Delete and self.table.rowCount() > 0:
            row = self.table.currentRow()
            t = self.data.transactions[row]
            if t.trans_type != TransactionType.MANUAL:
                pass#return

            cont = QtWidgets.QMessageBox.question(self, "Really delete transaction?", "Really delete transaction?")
            if cont == QtWidgets.QMessageBox.No:
                return
            self.data.transactions.pop(row)
            self.table.removeRow(row)
            self.data.save()
            self.recalculate.emit()

    def _add_transaction_button(self):
        try:
            amount = round(float(self.e_amount.text()), 2)
        except ValueError:
            send_info_popup("Enter a valid number for the amount (without any $)")
            return
        
        date = self.data.current_day.isoformat()
        comment = self.e_comment.text()
        self.add_transaction(Transaction(TransactionType.MANUAL, date, comment=comment, amount=amount))
        self.e_comment.setText("")
        self.e_amount.setText("")
    
    def add_transaction(self, transaction: Transaction):
        self.data.transactions.append(transaction)
        self.data.save()

        self._add_transaction_to_table(transaction)
        self.recalculate.emit()
        
    def _add_transaction_to_table(self, transaction: Transaction):
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)
        self.set_row_to(row, transaction)
    
    def set_row_to(self, row, transaction):
        self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(format_money(transaction.compute_amount())))
        self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(format_date(transaction.timestamp)))
        self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(transaction.compute_comment()))

def calc_series(datas, series):
    if series == "Balance":
        return [calc_bal(d) for d in datas]
    elif series == "Population":
        return [calc_population(d)[0] for d in datas]
    elif series == "Income":
        return [calc_income(d)[0] for d in datas]
    elif series == "Expenditure":
        vals = []
        for d in datas:
            vals.append(0)
            for trans in d.transactions:
                if trans.timestamp == d.current_day.isoformat() and trans.compute_amount() < 0:
                    vals[-1] -= trans.compute_amount()
        return vals
    elif series == "Employment":
        return [calc_employment(d) * 100 for d in datas]
    
    elif series == "Time":
        return [i for i, d in enumerate(datas)]
    
class GraphControls(QtWidgets.QWidget):
    def __init__(self, figure, data, parent=None):
        super().__init__(parent)
        self.figure = figure
        self.data = data
        self.ax = figure.subplots()

        self.layout = QtWidgets.QVBoxLayout(self)
        self.graph_type = QtWidgets.QComboBox(self)
        self.x_axis = QtWidgets.QComboBox(self)
        self.y_axis = QtWidgets.QComboBox(self)
        
        self.l_gtype = QtWidgets.QLabel("Graph type", self)
        self.l_xaxis = QtWidgets.QLabel("Plot...", self)
        self.l_yaxis = QtWidgets.QLabel("Against...", self)
        
        self.b_plot = QtWidgets.QPushButton("Plot", self)
        self.b_clear = QtWidgets.QPushButton("Clear", self)
        
        self.graph_type.addItems(["Line graph", "Scatter graph", "Pie chart"])
        
        self.layout.addWidget(self.l_gtype)
        self.layout.addWidget(self.graph_type)
        self.layout.addWidget(self.l_xaxis)
        self.layout.addWidget(self.x_axis)
        self.layout.addWidget(self.l_yaxis)
        self.layout.addWidget(self.y_axis)
        self.layout.addWidget(self.b_plot)
        self.layout.addWidget(self.b_clear)
        
        self.setLayout(self.layout)
        
        self.graph_type.activated[str].connect(lambda x: self.update())
        self.x_axis.activated[str].connect(lambda x: self.update())
        self.y_axis.activated[str].connect(lambda x: self.update())
        self.b_plot.clicked.connect(self.plot)
        self.b_clear.clicked.connect(self.clear)
        
        self.update()
        
    def clear(self):
        self.figure.clear()
        self.ax = self.figure.subplots()
        # self.ax.clear()
        self.figure.canvas.draw()
        
    def update(self):
        ty = self.graph_type.currentText()
        itemx = self.x_axis.currentIndex()
        itemy = self.y_axis.currentIndex()
        self.x_axis.clear()
        self.y_axis.clear()
        # TODO graph something of just one region
        if ty == "Line graph" or ty == "Scatter graph":
            self.x_axis.addItems(["Balance", "Income", "Expenditure", "Employment", "Population"])
            self.y_axis.addItems(["Time"])
            
        if ty == "Scatter graph":
            self.y_axis.addItems(["Balance", "Income", "Expenditure", "Employment", "Population"])
            
        if ty == "Pie chart":
            self.x_axis.addItems(["Income", "Population"])
            self.y_axis.addItems(["Region", "Industry"])
            
        # elif ty == "Bar chart":
            # self.x_axis.addItems(["Employment"])
            # self.y_axis.addItems(["Region"])
        
        if itemx < self.x_axis.count():
            self.x_axis.setCurrentIndex(itemx)
            
        if itemy < self.y_axis.count():
            self.y_axis.setCurrentIndex(itemy)
    
    def plot(self):
        # TODO do it
        gtype = self.graph_type.currentText()
        xaxis = self.x_axis.currentText()
        yaxis = self.y_axis.currentText()
        if len(xaxis) < 1 or len(yaxis) < 1:
            return
            
        if gtype == "Pie chart":
            if xaxis == "Income" and yaxis == "Region":
                _, regional_income = calc_income(data)
                values, labels = regional_income.values(), regional_income.keys()
            elif xaxis == "Population" and yaxis == "Region":
                _, regional_pop = calc_population(data)
                values, labels = regional_pop.values(), regional_pop.keys()
            elif xaxis == "Income" and yaxis == "Industry":
                ind = calc_industry_income(data)
                values, labels = ind.values(), ind.keys()
            else:
                return # invalid configuration

            values, labels = zip(*sorted(zip(values, labels), key=lambda i: i[0]))
            cm = plt.get_cmap("plasma")
            colours = [cm(i) for i in np.linspace(0, 1, len(values))]

            self.ax.pie(values, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90, colors=colours)
            self.ax.axis('equal')
        
        elif gtype == "Line graph" or gtype == "Scatter graph":
            datas = sorted(get_historical_datas(self.data), key=lambda d: d.current_day)
            xvals = calc_series(datas, xaxis)
            yvals = calc_series(datas, yaxis)
            if gtype == "Line graph":
                self.ax.plot(yvals, xvals)
            else:
                self.ax.scatter(yvals, xvals)
        
        # elif gtype == "Bar chart":
            # if xaxis == "Employment" and yaxis == "Region":
                # _, regional_employment = calc_employment(data)
                # self.ax.bar(regional_employment.keys(), list(map(lambda n: n * 100, regional_employment.values())))
            
        self.figure.canvas.draw()

class MoronException(Exception):
    pass

class StatsTab(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QtWidgets.QGridLayout(self)
        
        self.graph_layout = QtWidgets.QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)

        self.graph_controls = GraphControls(self.figure, data, self)

        self.layout.addWidget(self.graph_controls, 0, 0, 1, 1)
        self.layout.addLayout(self.graph_layout, 0, 1, 3, 1)
        self.layout.setColumnStretch(1, 1)
        self.setLayout(self.layout)

class LoansTab(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.data = data

        self.layout = QtWidgets.QGridLayout(self)
        
        self.e_amount = QtWidgets.QSpinBox(self)
        self.e_amount.setMaximum(999999999)
        self.l_amount = QtWidgets.QLabel("Amount", self)
        self.b_un = QtWidgets.QCheckBox("UN loan", self)
        self.e_interest_rate = QtWidgets.QDoubleSpinBox(self)
        self.l_interest_rate = QtWidgets.QLabel("Interest Rate (%)", self)
        self.e_name = QtWidgets.QLineEdit(self)
        self.l_name = QtWidgets.QLabel("Name", self)
        self.b_get_loan = QtWidgets.QPushButton("Add loan", self)

        self.ongoing_loans = QtWidgets.QGridLayout()
        self.spacer = QtWidgets.QLabel("")

        self.layout.addWidget(self.l_amount, 0, 0)
        self.layout.addWidget(self.e_amount, 1, 0)
        self.layout.addWidget(self.b_un,     1, 1)
        self.layout.addWidget(self.l_interest_rate, 0, 2)
        self.layout.addWidget(self.e_interest_rate, 1, 2)
        self.layout.addWidget(self.l_name, 0, 3)
        self.layout.addWidget(self.e_name, 1, 3)
        self.layout.addWidget(self.b_get_loan, 1, 4)
        self.layout.addLayout(self.ongoing_loans, 4, 0, 1, 5)
        self.layout.addWidget(self.spacer, 5, 0, 1, 5)
        self.layout.setRowStretch(5, 1)

        self.setLayout(self.layout)

        self.b_un.clicked.connect(self.un_loan)
        self.b_get_loan.clicked.connect(self.get_loan)
        self.loans = []
        self.ongoing_loans.addWidget(QtWidgets.QLabel("Amount due for payback"), 0, 0)
        self.ongoing_loans.addWidget(QtWidgets.QLabel("Interest rate"), 0, 1)
        self.ongoing_loans.addWidget(QtWidgets.QLabel("Lender name"), 0, 2)
        self.curr_row = 1

        self.update_loan_widgets()

    def un_loan(self):
        if self.b_un.isChecked():
            self.e_interest_rate.setEnabled(False)
            self.e_interest_rate.setValue(UN_LOAN_INTEREST * 100)
            self.e_name.setEnabled(False)
            self.e_name.setText("UN")
        else:
            self.e_interest_rate.setEnabled(True)
            self.e_name.setEnabled(True)

    def get_loan(self):
        self.data.loans.append([self.e_amount.value(), self.e_interest_rate.value(), self.e_name.text(), 0])
        self.add_loan_widgets(data.loans[-1])
        self.parent.transactions_tab.add_transaction(Transaction(
            TransactionType.MANUAL,
            self.data.current_day.isoformat(),
            comment="Loan from " + self.e_name.text(),
            amount=self.e_amount.value(),
        ))
        self.data.save()

    def make_payment(self, pos, loan):
        amount, ok = QtWidgets.QInputDialog.getDouble(self, "Make loan payment", "How much would you like to pay?", 0, 1, loan[0], 2)
        if not ok:
            return

        self.parent.transactions_tab.add_transaction(Transaction(
            TransactionType.MANUAL,
            self.data.current_day.isoformat(),
            comment="Loan payment to " + loan[2],
            amount=-amount
        ))

        # this is stupid
        idx = -1
        for i, l in enumerate(data.loans):
            if l[1] == loan[1] and l[2] == loan[2]:
                idx = i
                break
        if idx == -1:
            raise MoronException("For some reason the loan you tried to pay off wasn't found in your total loan list. big but report to jams plz")
        self.data.loans[idx][3] += amount
        self.data.loans[idx][0] -= amount
        if self.data.loans[idx][0] < 0.01:
            if self.data.loans[idx][2] != "UN":
                to_pay_other = self.data.loans[idx][3]
                send_info_popup("You paid a total of " + format_money(to_pay_other) + " to " + self.data.loans[idx][2])
            self.data.loans.pop(idx)
            self.update_loan_widgets()
        else:
            self.loans[pos][0].setText(format_money(self.data.loans[idx][0]))
        self.data.save()

    def add_loan_widgets(self, loan):
        self.loans.append((
            QtWidgets.QLabel(format_money(loan[0])),
            QtWidgets.QLabel(str(round(loan[1], 2)) + "%"),
            QtWidgets.QLabel(loan[2]),
            QtWidgets.QPushButton("Make payment")
        ))
        l = len(self.loans)
        self.loans[-1][3].clicked.connect(lambda: self.make_payment(l - 1, loan))

        for col, w in enumerate(self.loans[-1]):
            self.ongoing_loans.addWidget(w, self.curr_row, col)

        self.curr_row += 1

    def update_loan_widgets(self):
        for row in self.loans:
            for w in row:
                self.ongoing_loans.removeWidget(w)
        self.loans.clear()

        self.curr_row = 1

        for loan in self.data.loans:
            self.add_loan_widgets(loan)

class Main(QtWidgets.QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.init_gui(data)

        self.show()
        
    def init_gui(self, data):
        self.layout = QtWidgets.QVBoxLayout(self)

        self.local_stats_layout = QtWidgets.QHBoxLayout()
        self.global_stats_layout = QtWidgets.QHBoxLayout()
        self.date_layout = QtWidgets.QHBoxLayout()
        
        self.b_update_day = QtWidgets.QPushButton("Update day to today's date", self)
        self.b_next_day = QtWidgets.QPushButton("Next day", self)
        self.b_update_day.clicked.connect(lambda: self.update_day())
        self.b_next_day.clicked.connect(lambda: self.update_day(delta=1))

        self.l_bal = QtWidgets.QLabel(self)
        self.l_income = QtWidgets.QLabel(self)
        self.l_employment = QtWidgets.QLabel(self)
        self.l_pop = QtWidgets.QLabel(self)
        self.l_jobs = QtWidgets.QLabel(self)
        self.l_lorentz = QtWidgets.QLabel(self)
        self.l_date = QtWidgets.QLabel(self)

        self.l_regincome = QtWidgets.QLabel(self)
        self.l_regpop = QtWidgets.QLabel(self)
        self.l_regjobs = QtWidgets.QLabel(self)
        self.l_regemploy = QtWidgets.QLabel(self)

        self.local_stats_layout.addWidget(self.l_regincome)
        self.local_stats_layout.addWidget(self.l_regemploy)
        self.local_stats_layout.addWidget(self.l_regpop)
        self.local_stats_layout.addWidget(self.l_regjobs)

        self.global_stats_layout.addWidget(self.l_bal)
        self.global_stats_layout.addWidget(self.l_income)
        self.global_stats_layout.addWidget(self.l_employment)
        self.global_stats_layout.addWidget(self.l_pop)
        self.global_stats_layout.addWidget(self.l_jobs)
        self.global_stats_layout.addWidget(self.l_lorentz)
        
        self.date_layout.addWidget(self.l_date)
        self.date_layout.addWidget(self.b_next_day)
        self.date_layout.addWidget(self.b_update_day)
        
        self.stats_tab = StatsTab(data, self)
        self.transactions_tab = TransactionsTab(data, self)
        self.buildings_tab = BuildingsTab(data, self)
        self.loans_tab = LoansTab(data, self)
        
        self.tab_widget = QtWidgets.QTabWidget(self)
        self.tab_widget.addTab(self.buildings_tab, "Buildings")
        self.tab_widget.addTab(self.transactions_tab, "Transactions")
        self.tab_widget.addTab(self.stats_tab, "Stats")
        self.tab_widget.addTab(self.loans_tab, "Loans")
        self.layout.addWidget(self.tab_widget)
        self.layout.addLayout(self.local_stats_layout)
        self.layout.addLayout(self.global_stats_layout)
        self.layout.addLayout(self.date_layout)
        
        self.setLayout(self.layout)
        self.recalculate()
        self.transactions_tab.recalculate.connect(self.recalculate)

    def recalculate(self):
        self.recalc_balance()
        self.recalc_income()
        self.l_date.setText("Current date: " + format_date(self.data.current_day.isoformat()))
        self.l_pop.setText("Population: " + str(calc_population(self.data)[0]))
        self.l_jobs.setText("Jobs: " + str(round(calc_jobs(self.data)[0], 2)))
        self.buildings_tab.recalc_preview()
        self.l_lorentz.setText("L: " + str(round(Building.get_lorentz(self.data.eco_cache), 4)))
        self.recalc_regional_stats(self.buildings_tab)
        
    def recalc_regional_stats(self, buildings_tab):
        if buildings_tab.curr_region == "Total":
            # no regional stats
            self.l_regincome.hide()
            self.l_regemploy.hide()
            self.l_regpop.hide()
            self.l_regjobs.hide()
        else:
            _, reg_pop = calc_population(self.data)
            _, reg_jobs = calc_jobs(self.data)
            pop = reg_pop[buildings_tab.curr_region]
            jobs = reg_jobs[buildings_tab.curr_region]
            
            if pop != 0:
                employ_percent = jobs / pop * 100
            else:
                employ_percent = 0

            _, regional_income = calc_income(self.data)
            inc = regional_income[buildings_tab.curr_region]
            
            self.l_regincome.show()
            self.l_regemploy.show()
            self.l_regpop.show()
            self.l_regjobs.show()
            self.l_regincome.setText("Income (region): " + str(format_money(inc)))
            self.l_regemploy.setText("Employment (region): " + str(round(employ_percent, 1)) + "%")
            self.l_regpop.setText("Population (region): " + str(pop))
            self.l_regjobs.setText("Jobs (region): " + str(round(jobs, 2)))
            
    def recalc_balance(self):
        bal = calc_bal(self.data)
        self.l_bal.setText("Balance: " + format_money(bal))
        
    def recalc_income(self):
        global eco_cache
        employment = calc_employment(self.data)
        income, regional_income = calc_income(self.data)
        self.data.eco_cache = income
        
        self.l_income.setText("Income: " + format_money(income))
        self.l_employment.setText("Employment: " + str(round(employment * 100, 2)) + "%")
        
    def get_paid(self):
        # this check is currently redundant but I left it in for the lulz
        for n in data["transactions"][::-1]:
            if n.comment == "Income" and n.timestamp == self.data.current_day.isoformat():
                send_info_popup("YE CANNAE FOCKEN DAE THAT M8\n(you can only get paid once per day)")
                return
        income, regional_income = calc_income(data)
        self.transactions_tab.add_transaction(Transaction(
            TransactionType.MANUAL,
            self.data.current_day.isoformat(),
            comment="Income",
            amount=income,
        ))
        bal = calc_bal(data)
        if bal < 0:
            self.transactions_tab.add_transaction(Transaction(
                TransactionType.MANUAL,
                self.data.current_day.isoformat(),
                comment="Overdraft interest",
                amount=bal * OVERDRAFT_INTEREST,
            ))

    def calc_loans(self):
        for loan in self.data.loans:
            loan[0] *= loan[1] / 100 + 1
        self.loans_tab.update_loan_widgets()

    def update_day(self, delta=None):
        if delta is not None:
            now = datetime.date.today()
            next_day = self.data.current_day + datetime.timedelta(days=delta)
            if next_day > now:
                send_info_popup("Woah there buddy you aren't goint 88mph\n(you're trying to go into the future!)")
                return

        self.data.save()
        if os.path.exists(BACKUP_DIR) and os.path.isfile(BACKUP_DIR):
            raise MoronException("You absolute idiot, you made a file called 'backups', that's where I want to store my backups! Please delete or rename it")
        if not os.path.exists(BACKUP_DIR):
            os.mkdir(BACKUP_DIR)
        
        # Yes, this is a race condition or TOC/TOU bug
        # The truth is, I do not care, for it is exceedingly unlikely that anything could happen in between
        # also it wouldn't even matter that much it would just crash and save the progress anyway lmao
        
        self.data.write_to_file(os.path.join(BACKUP_DIR, self.data.current_day.isoformat() + ".json"))
            
        if delta is None:
            self.data.current_day = datetime.date.today()
        else:
            self.data.current_day += datetime.timedelta(days=delta)
        self.get_paid()
        self.calc_loans()
        self.recalculate()
        self.data.save()

def exception_hook(exctype, value, tb):
    traceback_formated = traceback.format_exception(exctype, value, tb)
    traceback_string = "".join(traceback_formated)
    print("Excepthook called, saving and quiteing...")
    data.save()
    print(traceback_string, file=sys.stderr)
    
    msg = QtWidgets.QMessageBox()
    msg.setIcon(QtWidgets.QMessageBox.Critical)
    msg.setText("An error occurred in the main process. Your data should be safe (in theory). Please send the following report to me(james):\n" + traceback_string)
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
    sys.exit(1)

class Updater(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout(self)
        self.doing = QtWidgets.QLabel(self)
        self.progress = QtWidgets.QProgressBar(self)
        self.layout.addWidget(self.doing)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)

    def update(self):
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)
        self.uworker = UpdateWorker()

        self.uworker.progress_changed.connect(lambda prog: self.progress.setValue(prog))
        self.uworker.progress_max.connect(lambda m: self.progress.setMaximum(m))
        self.uworker.update_status.connect(lambda s: self.doing.setText(s))
        self.uworker.result.connect(lambda res: self.update_done(res[0], res[1]))
        self.uworker.start()

    def update_done(self, updated, msg):
        if updated:
            send_info_popup(msg)
        elif msg is not None:
            choice = QtWidgets.QMessageBox.warning(self, "Update Failed",
                                   "Error updating: " + msg,
                                   QtWidgets.QMessageBox.Retry | QtWidgets.QMessageBox.Ignore,
                                   QtWidgets.QMessageBox.Retry)

            if choice == QtWidgets.QMessageBox.Retry:
                self.update()
                return
        self.done(updated)

class UpdateWorker(QtCore.QThread):
    progress_changed = Qt.pyqtSignal(int)
    progress_max = Qt.pyqtSignal(int)
    result = Qt.pyqtSignal(object)
    update_status = Qt.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        res = self.autoupdate()
        self.result.emit(res)
    
    def autoupdate(self):
        self.update_status.emit("Checking for updates...")
        try:
            vers_r = requests.get("http://cospox.com/eco/version")
        except Exception as e:
            return False, "Getting version, other error " + str(e)
        if vers_r.status_code != 200:
            return False, "Getting version, status " + str(vers_r.status_code)
        if vers_r.text.strip() == MY_VERSION:
            # already up to date
            return False, None

        self.update_status.emit("Fetching file list...")
        
        try:
            flist = requests.get("http://cospox.com/eco/files")
        except Exception as e:
            return False, "Getting file list, other error " + str(e)

        if flist.status_code != 200:
            return False, "Getting file list, status " + str(flist.status_code)

        num_files = len(flist.text.strip().split(","))
        self.progress_max.emit(num_files + 1)
        val = 1
        self.progress_changed.emit(val)

        for fname in flist.text.strip().split(","):
            self.update_status.emit("Downloading " + fname + " (" + str(val) + "/" + str(num_files - 1) + ")")
            try:
                r = requests.get("http://cospox.com/eco/" + fname)
            except Exception as e:
                return False, "Getting file " + fname + ", other error " + str(e)
 
            if r.status_code != 200:
                return False, "Getting update file " + fname + ", status " + str(r.status_code)
            with open(os.path.join("src", fname), "w", newline="") as f:
                f.write(r.text)

            val += 1
            self.progress_changed.emit(val)

        return True, "Downloaded version " + vers_r.text + ". Restart program to update."

if __name__ == '__main__':
    import threading
    sys.excepthook = exception_hook
    app = QtWidgets.QApplication(sys.argv)
    updater = Updater()
    updater.update()
    if updater.exec():
        sys.exit(0)
    
    data = Data()
    if os.path.exists(ECONOMY_FILE):
        data.read_from_file(ECONOMY_FILE)
    else:
        data.set_defaults()

    ex = Main(data)
    if os.path.isfile("stylesheets.qss"):
        with open("stylesheets.qss", "r") as f:
            ex.setStyleSheet(f.read())
    if os.path.isfile("appearance.json"):
        with open("appearance.json", "r") as f:
            ap = json.load(f)
        
        app.setStyle(ap["style"])

    sys.exit(app.exec_())
