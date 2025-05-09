import sys
import redis
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QLineEdit,
    QStackedWidget, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt

r = redis.Redis(host='redis', port=6379, decode_responses=True)

class ATM:
    def __init__(self):
        self.r = r
        if not self.r.exists("password"):
            self.r.set("password", "1234")
        if not self.r.exists("balance"):
            self.r.set("balance", 1000000)
        self.language = "fa"

    @property
    def balance(self):
        return int(self.r.get("balance"))

    @balance.setter
    def balance(self, value):
        self.r.set("balance", value)

    @property
    def password(self):
        return self.r.get("password")

    @password.setter
    def password(self, value):
        self.r.set("password", value)

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            return True
        return False

    def transfer(self, amount):
        return self.withdraw(amount)

    def change_password(self, new_pass):
        self.password = new_pass

    def get_balance(self):
        return self.balance


atm = ATM()

translations = {
    'fa': {
        'welcome': 'به دستگاه خودپرداز خوش آمدید',
        'enter_password': 'لطفاً رمز عبور خود را وارد کنید:',
        'login': 'ورود',
        'language_select': 'زبان را انتخاب کنید:',
        'english': 'English',
        'farsi': 'فارسی',
        'invalid_password': 'رمز عبور اشتباه است!',
        'menu': 'لطفاً یک گزینه را انتخاب کنید:',
        'balance': 'مشاهده موجودی',
        'withdraw': 'برداشت وجه',
        'transfer': 'انتقال وجه',
        'change_password': 'تغییر رمز عبور',
        'exit': 'خروج',
        'amount': 'لطفاً مبلغ را وارد کنید:',
        'success': 'عملیات با موفقیت انجام شد',
        'fail': 'موجودی کافی نیست',
        'new_password': 'رمز عبور جدید را وارد کنید:',
        'card_number': 'شماره کارت مقصد را وارد کنید:'
    },
    'en': {
        'welcome': 'Welcome to ATM',
        'enter_password': 'Please enter your password:',
        'login': 'Login',
        'language_select': 'Select your language:',
        'english': 'English',
        'farsi': 'فارسی',
        'invalid_password': 'Invalid password!',
        'menu': 'Please select an option:',
        'balance': 'Check Balance',
        'withdraw': 'Withdraw',
        'transfer': 'Transfer',
        'change_password': 'Change Password',
        'exit': 'Exit',
        'amount': 'Enter amount:',
        'success': 'Operation successful',
        'fail': 'Insufficient funds',
        'new_password': 'Enter new password:',
        'card_number': 'Enter recipient card number:'
    }
}

class LanguageSelection(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        self.label = QLabel("Select your language:")
        self.button_en = QPushButton("English")
        self.button_fa = QPushButton("فارسی")
        layout.addWidget(self.label)
        layout.addWidget(self.button_en)
        layout.addWidget(self.button_fa)
        self.setLayout(layout)
        self.button_en.clicked.connect(lambda: self.select_language('en'))
        self.button_fa.clicked.connect(lambda: self.select_language('fa'))

    def select_language(self, lang):
        atm.language = lang
        self.stack.widget(1).update_ui()
        self.stack.setCurrentIndex(1)

class PasswordScreen(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        self.label = QLabel()
        self.edit = QLineEdit()
        self.edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.button = QPushButton()
        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.button.clicked.connect(self.check_password)

    def update_ui(self):
        t = translations[atm.language]
        self.label.setText(t['enter_password'])
        self.button.setText(t['login'])

    def check_password(self):
        if self.edit.text() == atm.password:
            self.stack.widget(2).update_ui()
            self.stack.setCurrentIndex(2)
        else:
            QMessageBox.warning(self, "Error", translations[atm.language]['invalid_password'])

class MenuScreen(QWidget):
    def __init__(self, stack):
        super().__init__()
        self.stack = stack
        layout = QVBoxLayout()
        self.label = QLabel()
        self.buttons = {
            'balance': QPushButton(),
            'withdraw': QPushButton(),
            'transfer': QPushButton(),
            'change_password': QPushButton(),
            'exit': QPushButton()
        }
        layout.addWidget(self.label)
        for btn in self.buttons.values():
            layout.addWidget(btn)
        self.setLayout(layout)

        self.buttons['balance'].clicked.connect(self.show_balance)
        self.buttons['withdraw'].clicked.connect(self.withdraw)
        self.buttons['transfer'].clicked.connect(self.transfer)
        self.buttons['change_password'].clicked.connect(self.change_password)
        self.buttons['exit'].clicked.connect(sys.exit)

    def update_ui(self):
        t = translations[atm.language]
        self.label.setText(t['menu'])
        self.buttons['balance'].setText(t['balance'])
        self.buttons['withdraw'].setText(t['withdraw'])
        self.buttons['transfer'].setText(t['transfer'])
        self.buttons['change_password'].setText(t['change_password'])
        self.buttons['exit'].setText(t['exit'])

    def show_balance(self):
        QMessageBox.information(self, "Balance", f"{translations[atm.language]['balance']}: {atm.get_balance()}")

    def withdraw(self):
        t = translations[atm.language]
        amount, ok = QInputDialog.getInt(self, t['withdraw'], t['amount'])
        if ok:
            if atm.withdraw(amount):
                QMessageBox.information(self, "Success", t['success'])
            else:
                QMessageBox.warning(self, "Failed", t['fail'])

    def transfer(self):
        t = translations[atm.language]
        card_number, ok1 = QInputDialog.getText(self, t['transfer'], t['card_number'])
        if not ok1:
            return
        amount, ok2 = QInputDialog.getInt(self, t['transfer'], t['amount'])
        if ok2:
            if atm.transfer(amount):
                message = f"{t['success']}\n{t['card_number']} {card_number}"
                QMessageBox.information(self, "Success", message)
            else:
                QMessageBox.warning(self, "Failed", t['fail'])

    def change_password(self):
        t = translations[atm.language]
        new_pass, ok = QInputDialog.getText(self, t['change_password'], t['new_password'])
        if ok:
            atm.change_password(new_pass)
            QMessageBox.information(self, "Success", t['success'])

class ATMApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.lang_screen = LanguageSelection(self)
        self.pass_screen = PasswordScreen(self)
        self.menu_screen = MenuScreen(self)
        self.addWidget(self.lang_screen)
        self.addWidget(self.pass_screen)
        self.addWidget(self.menu_screen)

app = QApplication(sys.argv)
atm_app = ATMApp()
atm_app.setWindowTitle("ATM")
atm_app.resize(300, 200)
atm_app.show()
sys.exit(app.exec())
