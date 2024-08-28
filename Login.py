import wx
from Database import DataBase
import AppInterface
import re

db = DataBase()


class Login(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        
        self.InitUI()

    def InitUI(self):
        pnl = wx.Panel(self)
        wx.StaticText(pnl, label = "Login", pos = (175, 10))

        wx.StaticText(pnl, label = "Email", pos=(25, 30))
        self.email = wx.TextCtrl(pnl, pos = (125, 30), size=(250, 25))

        wx.StaticText(pnl, label = "Password", pos=(25, 60))
        self.password = wx.TextCtrl(pnl, pos = (125, 60), size=(250, 25), style=wx.TE_PASSWORD)

        btn1 = wx.Button(pnl, label = "Log in", pos = (160, 90), size = (125, -1))
        btn1.Bind(wx.EVT_BUTTON, self.log)

        wx.StaticText(pnl, label = "New user?", pos = (200, 130))
        btn2= wx.Button(pnl, label = "Register", pos= (160, 150), size = (125, -1))
        btn2.Bind(wx.EVT_BUTTON, self.register)
        
        self.SetSize((450, 225))
        self.SetTitle("Log in")
        self.Center()
        self.Show(True)

    def log(self, e):
        email = self.email.GetValue()
        password = self.password.GetValue()

        if db.check_log_in(email, password) == -1:
            wx.MessageBox('No user with such email!', 'Error', wx.OK | wx.ICON_ERROR)
        elif db.check_log_in(email, password) == 0:
            wx.MessageBox("Wrong Password!", 'Error', wx.OK | wx.ICON_ERROR)
        else:
            user_id = db.get_logged_user_id(email)
            AppInterface.MainFrame(user_id)
            self.Close(True)
            
    def register(self, e):
        self.Close(True)
        Register(None)
        



class Register(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(Register, self).__init__(*args, **kwargs)
        self.InitUI()  
        
    def InitUI(self):
        pnl = wx.Panel(self)
        wx.StaticText(pnl, label = "Register", pos = (175, 10))

        wx.StaticText(pnl, label = "First name", pos=(25, 30))
        self.first_name = wx.TextCtrl(pnl, pos = (125, 30), size=(250, 25))

        wx.StaticText(pnl, label = "Last name", pos=(25, 60))
        self.second_name=wx.TextCtrl(pnl, pos = (125, 60), size=(250, 25))

        wx.StaticText(pnl, label = "Email", pos=(25, 90))
        self.email = wx.TextCtrl(pnl, pos = (125, 90), size=(250, 25))

        wx.StaticText(pnl, label = "Password", pos=(25, 120))
        self.password_1 = wx.TextCtrl(pnl, pos = (125, 120), size=(250, 25), style = wx.TE_PASSWORD)

        wx.StaticText(pnl, label = "Confirm password", pos=(25, 150))
        self.password_2 = wx.TextCtrl(pnl, pos = (125, 150), size=(250, 25), style = wx.TE_PASSWORD)

        btn1 = wx.Button(pnl, label = "Register", pos = (160, 180), size = (125, -1))
        btn1.Bind(wx.EVT_BUTTON, self.register)

        wx.StaticText(pnl, label = "Already have an account?", pos = (160, 220))
        btn2= wx.Button(pnl, label = "Log in", pos= (160, 240), size = (125, -1))
        btn2.Bind(wx.EVT_BUTTON, self.login)
        
        self.SetSize((450, 325))
        self.SetTitle("Register")
        self.Center()
        self.Show(True)

    def register(self, e):
        first_name = self.first_name.GetValue()
        second_name = self.second_name.GetValue()
        email = self.email.GetValue()
        password = self.password_1.GetValue()

        if self.check_register_info():
           user_id = db.register(first_name, second_name,email, password)
           AppInterface.MainFrame(user_id)
           self.Close(True)


    def check_register_info(self):

        regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        regex_password = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$'
        
        if not re.match(regex_email, self.email.GetValue()):
          wx.MessageBox('Invalid email!', 'Error', wx.OK | wx.ICON_ERROR)
          return False
        
        if self.password_1.GetValue()!=self.password_2.GetValue():
            wx.MessageBox('Passwords not matching!', 'Error', wx.OK | wx.ICON_ERROR)
            return False

        if not re.match(regex_password, self.password_1.GetValue()):
            wx.MessageBox('''Invalid password! Password must contain: \n 
                        At least one uppercase letter\n 
                        At least one lowercase letter \n 
                        At least one digit. \n
                        At least 8 characters.''', 'Error', wx.OK | wx.ICON_ERROR)
            return False
                
        if not db.is_user_registered(self.email.GetValue()):
            wx.MessageBox('User with this email already exists!', 'Error', wx.OK | wx.ICON_ERROR)
            return False
        
        return True
    
    
    def login(self, e):
        self.Close(True)
        Login(None)
        

   
