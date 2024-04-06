#from ctypes import windll, c_int64
import ctypes
import datetime
import math
ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_int64(-4))
lastError = ctypes.windll.kernel32.GetLastError()
print(lastError)

import json
import yaml
import threading
import numpy as np
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.text import Label
from kivymd.theming import ThemeManager
from kivymd.uix.button import MDFlatButton, MDIconButton, MDFloatingActionButton, MDRaisedButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivy.uix.image import Image, AsyncImage
from kivymd.uix.fitimage import FitImage
from kivy.uix.recycleview import RecycleView, RecycleDataAdapter, RecycleViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivymd.uix.segmentedcontrol import MDSegmentedControl, MDSegmentedControlItem
from kivy.clock import Clock
from functools import partial


from kivy.uix.scatter import Scatter
from kivy.uix.stencilview import StencilView
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.transformation import Matrix
from kivy.uix.popup import Popup
from kivymd.toast import toast
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.properties import ObjectProperty, StringProperty
from kivy.factory import Factory
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineAvatarIconListItem, IconLeftWidget, ThreeLineIconListItem, TwoLineIconListItem, OneLineIconListItem
from kivymd.uix.selection.selection import MDSelectionList
from kivymd.uix.selectioncontrol import MDSwitch, MDCheckbox


from kivy.metrics import Metrics


from kivy.config import Config
Config.set('input', 'mouse', 'mouse,disable_multitouch,disable_on_activity')



import configparser
import os
import sys
import glob
#import xmltodict
import time

import cvLibrary
from results import HeroResults
import usb_camera
import circular_progress_bar
import torchvision.ops.boxes as bops
import torch

#Screen adjustments
###############################################################################################

# add the following 2 lines to solve OpenGL 2.0 bug
from kivy import Config
Config.set('graphics', 'resizeable', 0)
Config.set('graphics', 'fullscreen', 1)
Config.set('graphics', 'always_on_top', 1)

from kivy.core.window import Window
Window.size = (1920, 1080)
Window.top = 1
Window.left = 1

#############################################################################################


#Config
############################################################################################
#Assume we need 2 sections in the config file, let's call them USERINFO and SERVERCONFIG
config_object = configparser.ConfigParser()
config_object["USERINFO"] = {
    "admin": "admin",
    "supervisor": "supervisor",
    "operator": ""
}
config_object["APPINFO"] = {
    "style": "Light",
    "palette": "Gray",
    
}
config_object["SERVERCONFIG"] = {
    "host": "192.168.0.12",
    "port": "8080",
    "ipaddr": "8.8.8.8"
}
        
    



class VisionApp(MDApp):
    theme_cls = ThemeManager()
    appBar = any
    screen = any
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #Configurations 
        try:
            config_object.read("config.ini")
            themestyle = config_object["APPINFO"]
        except:
            with open('config.ini', 'w') as conf:
                config_object.write(conf)
            config_object.read("config.ini")
            themestyle = config_object["APPINFO"]
        

        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.theme_style = themestyle["style"] #"Light" #"Dark"
        self.theme_cls.primary_palette = themestyle["palette"] # "Gray" #"LightBlue"
    
    def build(self):
        self.title = "DIGIBOARD VISION AI"
        self.screen = MDScreen()
        self.screen.md_bg_color = "white"
       
        
         #App bar
        self.appBar = MDTopAppBar(type_height="small", type="top",
                    headline_text=f"Headline small",
                    left_action_items=[],
                    right_action_items=[
                        ["account-circle",  lambda x: x],
                        ["theme-light-dark", lambda x: self.theme_change()],
                        ["dots-vertical", lambda x: x],
                    ],
                    title="Digiboard Vision AI", specific_text_color = "blue" if self.theme_cls.theme_style == 'Light' else 'white')
        box = MDBoxLayout(orientation = "vertical", md_bg_color = "silver", spacing = 5)
        box.add_widget(self.appBar)
        box.add_widget(MainLayout())
        self.screen.add_widget(box)
        
        return self.screen
    
    

    def configupdate(self):
        try:
            config_object["APPINFO"]["style"] = self.theme_cls.theme_style
            config_object["APPINFO"]["palette"] = self.theme_cls.primary_palette
            with open('config.ini', 'w') as conf:
                config_object.write(conf)
            
            os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 
        except:
            pass

    def theme_change(self):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Deseja mudar padrão de cor?",
                text="Isso fechará o aplicativo e usará as novas configurações na proxima abertura.",
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.theme_change_cancel
                    ),
                MDFlatButton(
                    text="SIM",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.theme_change_confirmed
                    ),
                ],
            )
        
        self.dialog.open()

    def theme_change_cancel(self, *args):
        self.dialog.dismiss(force=True)

    def theme_change_confirmed(self, *args):
        if(self.theme_cls.theme_style == "Light"):
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Blue"  
        else:
            self.theme_cls.theme_style = "Light"
            self.theme_cls.primary_palette = "Gray" 

        self.configupdate()
        
        


#Design login scrren
class LoginLayout(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.md_bg_color = "#FFFFFF"
        self.orientation = "vertical"
        self.add_widget(MDLabel(text='DIGIBOARD VISION AI', halign='center', font_style='H2'))
        self.username = MDTextField(hint_text='Enter your username')
        self.password = MDTextField(hint_text='Enter your password', password=True)
        self.add_widget(self.username)
        self.add_widget(self.password)
        self.login_button = MDFlatButton(text='LOGIN', on_press=self.login)
        self.add_widget(self.login_button)
        
    def login(self, instance):
        username = self.username.text
        password = self.password.text
        print(f"Username: {username} \nPassword: {password}")

#Design main layout
class MainLayout(MDBoxLayout):
    menuCard = any
    appBar = any
    screenManager = any
    btnHome =None
    btnProduction = None
    btnTeach = None
    btnConfig = None
    btnAbout = None
    config_object = any

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.md_bg_color = "silver"
        self.spacing = 10
        self.size_hint_y = 0.8
        
        #
       
        
        appbox = MDBoxLayout(orientation = "horizontal", md_bg_color = "silver", spacing = 5)
        self.add_widget(appbox)

        #Menu card components
        self.menuCard = MDCard( spacing = 15, padding = 5, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", elevation = 2, size_hint_x=0.04)

        menubox = MDFloatLayout(   size_hint_y=1, pos_hint={'center_x':0.5, 'center_y':0.5})
        

        

        #logo
        self.btnHome = MDIconButton(icon = "view-dashboard-outline", theme_icon_color="Custom", icon_size = "46sp", pos_hint={'center_x':0.5, 'center_y':0.93}, on_release = self.showDashboard) 
        self.btnProduction = MDIconButton(icon = "flag-checkered", theme_icon_color="Custom",  icon_size = "46sp", pos_hint={'center_x':0.5, 'center_y':0.8}, on_press = self.showProduction)
        self.btnTeach = MDIconButton(icon = "human-male-board", theme_icon_color="Custom", icon_size = "46sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.showTeach)
        self.btnConfig = MDIconButton(icon = "table-cog", theme_icon_color="Custom", icon_size = "46sp", pos_hint={'center_x':0.5, 'center_y':0.54}, on_press = self.showConfig)
        self.btnAbout = MDIconButton(icon = "information-variant", theme_icon_color="Custom", icon_size = "46sp", pos_hint={'center_x':0.5, 'center_y':0.05})
        menubox.add_widget(self.btnHome)
        menubox.add_widget(self.btnProduction)
        menubox.add_widget(self.btnTeach)
        menubox.add_widget(self.btnConfig)
        menubox.add_widget(self.btnAbout)
        
        self.menuCard.add_widget(menubox)

        

        #Manager for screen changes
        self.screenManager = MDScreenManager(size_hint_y = 1, size_hint_x=0.85)
        dashScreen = dashboardScreen(name='dashboard')
        teachView = teachScreen(name='teach')
        configView = configScreen(name='config')
        productionView = productionScreen(name='production')
        self.screenManager.add_widget(dashScreen)
        self.screenManager.add_widget(teachView)
        self.screenManager.add_widget(configView)
        self.screenManager.add_widget(productionView)
        self.screenManager.current = 'dashboard'

        appbox.add_widget(self.menuCard)
        appbox.add_widget(self.screenManager)
        
        
        
    def login(self, instance):
        username = self.username.text
        password = self.password.text
        print(f"Username: {username} \nPassword: {password}")

    def showDashboard(self, *args):
        self.screenManager.current = 'dashboard'
        self.btnProduction.disabled = False
        self.btnConfig.disabled = False
        self.btnAbout.disabled = False
        self.btnTeach.disabled = False
        self.btnHome.md_bg_color = 'blue'
        self.btnProduction.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnTeach.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnConfig.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'

    def showTeach(self, *args):
        self.screenManager.current = 'teach'
        self.btnProduction.disabled = True
        self.btnConfig.disabled = True
        self.btnAbout.disabled = True
        self.btnTeach.disabled = False
        self.btnHome.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnConfig.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnProduction.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnTeach.md_bg_color = 'blue'


    def showConfig(self, *args):
        self.screenManager.current = 'config'
        self.btnProduction.disabled = True
        self.btnConfig.disabled = False
        self.btnAbout.disabled = True
        self.btnTeach.disabled = True
        self.btnHome.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnProduction.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnTeach.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnConfig.md_bg_color = 'blue'

    
    def showProduction(self, *args):
        self.screenManager.current = 'production'
        self.btnProduction.disabled = False
        self.btnConfig.disabled = True
        self.btnAbout.disabled = True
        self.btnTeach.disabled = True
        self.btnHome.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnConfig.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnTeach.md_bg_color =  'white' if config_object["APPINFO"]["style"] == 'Light' else 'black'
        self.btnProduction.md_bg_color = 'blue'



class dashboardScreen(MDScreen):
    boxLayout = MDBoxLayout()

    def __init__(self, **kwargs):
        super(dashboardScreen, self).__init__(**kwargs)
        self.boxLayout.orientation = "horizontal"
        self.boxLayout.md_bg_color = "silver"
        self.boxLayout.spacing = 10

        #boxes right and left
        leftBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.60)
        rightBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.20)

        #Center screen components
        centerCard = MDCard( padding = 1, size_hint_y = 0.64, size_hint_x = 1, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", radius = 10)
        img = Image(allow_stretch=True, keep_ratio=False, anim_delay = 0.1)
        img.source = source=config_object["APPINFO"]["mainGIF"]
        centerCard.add_widget(img)
        #centerCard.add_widget(MDLabel(text='VISION AI - Projeto desenvolvido com recursos da lei de informatica - SUFRAMA', halign='center', font_style='H2', theme_text_color='Custom', text_color='blue'))
        
        topBox = MDBoxLayout(orientation = "horizontal", spacing = 10, size_hint_x = 1, size_hint_y=0.2)
        rightCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=0.5, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        leftCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=0.5, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        leftCard.add_widget(Image(source=config_object["APPINFO"]["customerLogo"], allow_stretch=True, keep_ratio=True))
        rightCard.add_widget(Image(source=config_object["APPINFO"]["companyLogo"], allow_stretch=True, keep_ratio=True))

        topBox.add_widget(leftCard)
        topBox.add_widget(rightCard)

        leftBox.add_widget(topBox)
        leftBox.add_widget(centerCard)

        #Right screen components
        rightCard = MDCard( size_hint_x=0.20, size_hint_y = 0.99, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", pos_hint={'center_x':0.5, 'center_y':0.5})

        self.boxLayout.add_widget(leftBox)
        self.boxLayout.add_widget(rightCard)
        
        self.add_widget(self.boxLayout)

class FileChoosePopup(Popup):
    load = ObjectProperty()

class SaveDialog(MDFloatLayout):
    save = ObjectProperty(None)
    filename = ObjectProperty(None)
    cancel = ObjectProperty(None)

class LoadDialog(MDFloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

from kivy.lang import builder
Builder.load_file('filepopup.kv')
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('SaveDialog', cls=SaveDialog)






class IconLabel(MDBoxLayout):
    def __init__(self, icon_left, label_text, icon_right, **kwargs):
        super(IconLabel, self).__init__(**kwargs)
        
        # Create widgets
        self.icon_left = MDIcon(icon=icon_left)
        self.label = MDLabel(text=label_text)
        self.icon_right = MDIcon(icon=icon_right)
        
        # Add widgets to layout
        self.add_widget(self.icon_left)
        self.add_widget(self.label)
        self.add_widget(self.icon_right)

import myrecycleview
import horrecycleview


from pyModbusTCP.client import ModbusClient

class controllerTCP():
    SERVER_HOST = "10.0.0.5"
    SERVER_PORT = 502
    CLIENT = None
    MEMS = []
    INPUTS = []
    OUTPUTS = []
    REGS = []
    thOnline = None
    thRegs = []
    thValues = [] 
    thStop = False

    def startClient(self, host, port):
        self.SERVER_HOST = host
        self.SERVER_PORT = port


        try:
            # init modbus client
            self.CLIENT = ModbusClient(host=self.SERVER_HOST, port=self.SERVER_PORT, debug=False, auto_open=True)
            
            return True

        except:
            self.CLIENT = None
            return False
    
    def refreshPlcData(self, *args):
        if(not self.CLIENT):
            return False
        
        try:
            inputs = self.CLIENT.read_discrete_inputs(1024, 8)
            outputs = self.CLIENT.read_coils(1280, 8)
            mems = self.CLIENT.read_discrete_inputs(2048, 100)
            regs = self.CLIENT.read_holding_registers(4096, 100)

            if(inputs):
                self.INPUTS = inputs
            if(outputs):
                self.OUTPUTS = outputs
            if(mems):
                self.MEMS = mems
            if(regs):
                self.REGS = regs

            return True

        except:
            #self.MEMS = []
            #self.INPUTS = []
            #self.OUTPUTS = []
            return False
    
    def setMEM(self, m, state):
        if(not self.CLIENT):
            return False
        
        try:
            self.CLIENT.write_single_coil(2048+m, state)
            self.MEMS[m] = state
            return True
        except:
            return False


    def setREG(self, r, state):
        if(not self.CLIENT):
            return False
        
        try:
            
            w = self.CLIENT.write_single_register(4096+r, state)
            if w:
                self.REGS[r] = state
                return True
            else:
                return False
        except:
            return False

    def start_online_mode(self):
        if self.thOnline:
            return False
        
        self.thOnline = threading.Thread(target=self.online_mode)
        self.thOnline.daemon = True
        self.thStop = False
        self.thOnline.start()

    
    def online_mode(self):
        err_cont = 0
        loop_cont = 0
        if not self.setREG(6, 1):
            return False

        while not self.thStop:
            
            #refresh PLC data
            if not self.refreshPlcData():
                err_cont += 1
            else:
                err_cont = 0

                #heartbeat 
                if loop_cont >= 3:
                    loop_cont = 0
                    if self.REGS[99] == 0:
                        self.setREG(99, 1)
                        pass#Clock.schedule_once( partial(self.setREG), 0)
                    else:
                        self.setREG(99, 0)
                        pass#Clock.schedule_once( partial(self.setREG), 0)


                #write new values from thReg[] and thValues[]
                if len(self.thRegs) > 0:
                    pass

            if err_cont > 10:
                self.thStop = True

            
            loop_cont += 1
            time.sleep(.5)







class configScreen(MDScreen):
    boxLayout = MDBoxLayout()
    plc = controllerTCP()

    def on_pre_enter(self, *args):
        
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
                
        return super().on_enter(*args)           

    def manual_action(self, btn, *args):
        m = -1
        if btn.id == "sw_ok":
            m = 0
        elif btn.id == "ilum_red":
            m = 1
        elif btn.id == "ilum_yel":
            m = 2
        elif btn.id == "ilum_gre":
            m = 3
        elif btn.id == "prod_ok":
            m = 4
        elif btn.id == "inspect_finish":
            m = 5
        elif btn.id == "product_ok":
            m = 6
        elif btn.id == "product_ng":
            m = 7
        elif btn.id == "bypass":
            m = 10
        elif btn.id == "board_in":
            m = 11
        elif btn.id == "board_out":
            m = 12
        elif btn.id == "actuator_i":
            m = 13
        elif btn.id == "actuator_ii":
            m = 14
        elif btn.id == "actuator_iii":
            m = 15
        elif btn.id == "online":
            m = -1 
            if not self.plc.thOnline:
                self.plc.start_online_mode()
            else:
                self.plc.thStop = True   
                time.sleep(1)
                self.plc.thOnline = None         
        else:
            m = -1 


        #if self.plc.setMEM(m, not self.plc.MEMS[m]):
        #    self.plc.refreshPlcData()
        #    if self.plc.MEMS[m] == True:
        #        btn.md_bg_color = 'green'
        #    else:
        #        btn.md_bg_color = 'red'
        

    
    def plc_connect(self, *args):
        try:
            if not self.plc.CLIENT:
                if self.plc.startClient(self.tfcontroller.text, int( config_object['CONTROLLER']['port'] ) ):
                    self.plc.refreshPlcData()
                    self.btnConnectPLC.md_bg_color = "yellowgreen"
                    toast("Controlador conectado!!!", background=(0,1,0,.7))
                else:
                    toast("Falha ao tentar conectar com controlador!", background=(1,0,0,.7))   
                    self.plc.CLIENT = None
                    self.btnConnectPLC.md_bg_color = 'red'
            else:
                self.CLIENT.close()
                self.plc.CLIENT = None
        except:
            toast("Falha ao tentar conectar com controlador!", background=(1,0,0,.7))   
            self.plc.CLIENT = None
            self.btnConnectPLC.md_bg_color = 'red'

    def config_save(self, *args):
        config_object['CONTROLLER']['host'] = self.tfcontroller.text
        if config_object['CONTROLLER']['port'] == '':
            config_object['CONTROLLER']['port'] = '502'
        
        if config_object['CONTROLLER']['refresh'] == '':
            config_object['CONTROLLER']['refresh']= '500'

        try:
            
            with open('config.ini', 'w') as conf:
                config_object.write(conf)     
        except:
            pass
        

    def plc_refresh(self, *args):
        try:
            self.plc.refreshPlcData()

            #Command buttons
            self.btnSetM0.md_bg_color = 'red' if not self.plc.MEMS[0] else 'green'
            self.btnSetM1.md_bg_color = 'red' if not self.plc.MEMS[1] else 'green'
            self.btnSetM2.md_bg_color = 'red' if not self.plc.MEMS[2] else 'green'
            self.btnSetM3.md_bg_color = 'red' if not self.plc.MEMS[3] else 'green'
            self.btnSetM4.md_bg_color = 'red' if not self.plc.MEMS[4] else 'green'
            self.btnSetM5.md_bg_color = 'red' if not self.plc.MEMS[5] else 'green'
            self.btnSetM6.md_bg_color = 'red' if not self.plc.MEMS[6] else 'green'
            self.btnSetM7.md_bg_color = 'red' if not self.plc.MEMS[7] else 'green'
            self.btnSetM10.md_bg_color = 'red' if not self.plc.MEMS[10] else 'green'
            self.btnSetM11.md_bg_color = 'red' if not self.plc.MEMS[11] else 'green'
            self.btnSetM12.md_bg_color = 'red' if not self.plc.MEMS[12] else 'green'
            self.btnSetM13.md_bg_color = 'red' if not self.plc.MEMS[13] else 'green'
            self.btnSetM14.md_bg_color = 'red' if not self.plc.MEMS[14] else 'green'
            self.btnSetM15.md_bg_color = 'red' if not self.plc.MEMS[15] else 'green'
            self.btnSetM16.md_bg_color = 'red' if not self.plc.REGS[5] else 'green'

            #Input
            self.input0.active = False if not self.plc.INPUTS[0] else True
            self.input1.active = False if not self.plc.INPUTS[1] else True
            self.input2.active = False if not self.plc.INPUTS[2] else True
            self.input3.active = False if not self.plc.INPUTS[3] else True
            self.input4.active = False if not self.plc.INPUTS[4] else True
            self.input5.active = False if not self.plc.INPUTS[5] else True
            self.input6.active = False if not self.plc.INPUTS[6] else True
            self.input7.active = False if not self.plc.INPUTS[7] else True

            #Output \
            self.output0.active = False if not self.plc.OUTPUTS[0] else True
            self.output1.active = False if not self.plc.OUTPUTS[1] else True
            self.output2.active = False if not self.plc.OUTPUTS[2] else True
            self.output3.active = False if not self.plc.OUTPUTS[3] else True
            self.output4.active = False if not self.plc.OUTPUTS[4] else True
            self.output5.active = False if not self.plc.OUTPUTS[5] else True
            self.output6.active = False if not self.plc.OUTPUTS[6] else True
            self.output7.active = False if not self.plc.OUTPUTS[7] else True
        
        except:

            pass


    def __init__(self, **kwargs):
        super(configScreen, self).__init__(**kwargs)
        self.boxLayout.orientation = "horizontal"
        self.boxLayout.md_bg_color = "silver"
        self.boxLayout.spacing = 10

        #Lef and right boxes
        leftBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.70)
        rightBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.25)

        self.add_widget(self.boxLayout)

        #PLC card
        plcCard = MDCard(padding = 15, size_hint_y = 1,  focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        rightBox.add_widget(plcCard)
        #Layout for PLC card
        plcLayout = MDFloatLayout()

        plcLabel = MDLabel(text='Controlador da máquina', font_size=10, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .98})
        self.tfcontroller = MDTextField(hint_text="Endereço IP", helper_text="Endereço do controlador do equipamento", helper_text_mode="on_focus",  pos_hint={"center_x": .5, "center_y": .92}) 
        self.tfcontroller.text = config_object['CONTROLLER']['host']


        self.btnConnectPLC = MDFloatingActionButton(icon="connection",   pos_hint={"center_x": .25, "center_y": .85}, on_press = self.plc_connect)
        btnSaveConfig = MDFloatingActionButton(icon="content-save-settings-outline",   pos_hint={"center_x": .5, "center_y": .85}, on_press = self.config_save)
        btnRefreshStatus = MDFloatingActionButton(icon="refresh",   pos_hint={"center_x": .75, "center_y": .85}, on_press = self.plc_refresh)

        memCard = MDCard(padding = 15, size_hint_y = .25,  focus_behavior = False,  unfocus_color = "darkgrey", pos_hint={"center_x": .5, "center_y": .65}, line_color=(0, 0, 0, 0.8), style="outlined")
        inputCard = MDCard(padding = 15, size_hint_y = .49, size_hint_x = 0.48, focus_behavior = False,  unfocus_color = "darkgrey", pos_hint={"center_x": .25, "center_y": .25}, line_color=(0, 0, 0, 0.8), style="outlined")
        outputCard = MDCard(padding = 15, size_hint_y = .49, size_hint_x = 0.48,  focus_behavior = False,  unfocus_color = "darkgrey", pos_hint={"center_x": .75, "center_y": .25}, line_color=(0, 0, 0, 0.8), style="outlined")
        
        self.btnSetM0 = MDRaisedButton(id='sw_ok', text="Software Ok (M0)   ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .15, "center_y": .92}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM1 = MDRaisedButton(id='ilum_red', text="Ilum. Vermelha (M1)", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .5, "center_y": .92}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM2 = MDRaisedButton(id='ilum_yel', text="Ilum. Amarela (M2) ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .85, "center_y": .92}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM3 = MDRaisedButton(id='ilum_gre', text="Ilum. Verde (M3)   ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .15, "center_y": .72}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM4 = MDRaisedButton(id='prod_ok', text="Produção Ok (M4)   ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .5, "center_y": .72}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM5 = MDRaisedButton(id='inspect_finish', text="Inspeção Fim (M5)  ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .85, "center_y": .72}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM6 = MDRaisedButton(id='product_ok', text="Produto OK (M6)    ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .15, "center_y": .52}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM7 = MDRaisedButton(id='product_ng', text="Produto NG (M7)    ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .5, "center_y": .52}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM10 = MDRaisedButton(id='bypass', text="Bypass (M10)       ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .85, "center_y": .52}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM11 = MDRaisedButton(id='board_in', text="Entrada placa(M11) ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .15, "center_y": .32}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM12 = MDRaisedButton(id='board_out', text="Saida placa(M12)   ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .5, "center_y": .32}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM13 = MDRaisedButton(id='actuator_i', text="Cilindro I(M13)    ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .85, "center_y": .32}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM14 = MDRaisedButton(id='actuator_ii', text="Cilindro II(M14)   ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .15, "center_y": .12}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM15 = MDRaisedButton(id='actuator_iii', text="Cilindro III(M15)  ", size_hint_x = .2, size_hint_y = .2, pos_hint={"center_x": .5, "center_y": .12}, font_size = "10sp", halign = 'left', on_press = self.manual_action)
        self.btnSetM16 = MDRaisedButton(id='online', text="Online", size_hint_x = .25, size_hint_y = .2, pos_hint={"center_x": .85, "center_y": .12}, font_size = "10sp", halign = 'left', on_press = self.manual_action)

        plcbuttonsbox = MDFloatLayout()
        memCard.add_widget(plcbuttonsbox)

        plcbuttonsbox.add_widget(self.btnSetM0)
        plcbuttonsbox.add_widget(self.btnSetM1)
        plcbuttonsbox.add_widget(self.btnSetM2)
        plcbuttonsbox.add_widget(self.btnSetM3)
        plcbuttonsbox.add_widget(self.btnSetM4)
        plcbuttonsbox.add_widget(self.btnSetM5)
        plcbuttonsbox.add_widget(self.btnSetM6)
        plcbuttonsbox.add_widget(self.btnSetM7)
        plcbuttonsbox.add_widget(self.btnSetM10)
        plcbuttonsbox.add_widget(self.btnSetM11)
        plcbuttonsbox.add_widget(self.btnSetM12)
        plcbuttonsbox.add_widget(self.btnSetM13)
        plcbuttonsbox.add_widget(self.btnSetM14)
        plcbuttonsbox.add_widget(self.btnSetM15)
        plcbuttonsbox.add_widget(self.btnSetM16)

        plcLayout.add_widget(plcLabel)
        plcLayout.add_widget(self.tfcontroller)
        plcLayout.add_widget(self.btnConnectPLC)
        plcLayout.add_widget(btnSaveConfig)
        plcLayout.add_widget(btnRefreshStatus)
        plcLayout.add_widget(memCard)
        plcLayout.add_widget(inputCard)
        plcLayout.add_widget(outputCard)
        plcCard.add_widget(plcLayout)

       
        self.boxLayout.add_widget(leftBox)
        
        self.input0 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .82}, widget_style = 'ios', width = 200)
        self.input1 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .72}, widget_style = 'ios')
        self.input2 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .62}, widget_style = 'ios')
        self.input3 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .52}, widget_style = 'ios')
        self.input4 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .42}, widget_style = 'ios')
        self.input5 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .32}, widget_style = 'ios')
        self.input6 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .22}, widget_style = 'ios')
        self.input7 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.25, "center_y": .12}, widget_style = 'ios')
        inputLabel0 = MDLabel(text='X0', pos_hint={"center_x": 1, "center_y": .82} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel1 = MDLabel(text='X1', pos_hint={"center_x": 1, "center_y": .72} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel2 = MDLabel(text='X2', pos_hint={"center_x": 1, "center_y": .62} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel3 = MDLabel(text='X3', pos_hint={"center_x": 1, "center_y": .52} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel4 = MDLabel(text='X4', pos_hint={"center_x": 1, "center_y": .42} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel5 = MDLabel(text='X5', pos_hint={"center_x": 1, "center_y": .32} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel6 = MDLabel(text='X6', pos_hint={"center_x": 1, "center_y": .22} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        inputLabel7 = MDLabel(text='X7', pos_hint={"center_x": 1, "center_y": .12} ,font_size=16, theme_text_color="Hint", font_style="Overline")


        inputBox = MDFloatLayout()
        inputBox.add_widget(self.input0)
        inputBox.add_widget(inputLabel0)
        inputBox.add_widget(self.input1)
        inputBox.add_widget(inputLabel1)
        inputBox.add_widget(self.input2)
        inputBox.add_widget(inputLabel2)
        inputBox.add_widget(self.input3)
        inputBox.add_widget(inputLabel3)
        inputBox.add_widget(self.input4)
        inputBox.add_widget(inputLabel4)
        inputBox.add_widget(self.input5)
        inputBox.add_widget(inputLabel5)
        inputBox.add_widget(self.input6)
        inputBox.add_widget(inputLabel6)
        inputBox.add_widget(self.input7)
        inputBox.add_widget(inputLabel7)

        inputCard.add_widget(inputBox)
        


        self.output0 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .82}, widget_style = 'ios', width = 200)
        self.output1 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .72}, widget_style = 'ios')
        self.output2 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .62}, widget_style = 'ios')
        self.output3 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .52}, widget_style = 'ios')
        self.output4 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .42}, widget_style = 'ios')
        self.output5 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .32}, widget_style = 'ios')
        self.output6 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .22}, widget_style = 'ios')
        self.output7 = MDSwitch(track_color_inactive = 'red', track_color_active = 'yellowgreen', pos_hint={"center_x": 0.35, "center_y": .12}, widget_style = 'ios')
        outputLabel0 = MDLabel(text='Y0', pos_hint={"center_x": 1.1, "center_y": .82} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel1 = MDLabel(text='Y1', pos_hint={"center_x": 1.1, "center_y": .72} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel2 = MDLabel(text='Y2', pos_hint={"center_x": 1.1, "center_y": .62} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel3 = MDLabel(text='Y3', pos_hint={"center_x": 1.1, "center_y": .52} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel4 = MDLabel(text='Y4', pos_hint={"center_x": 1.1, "center_y": .42} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel5 = MDLabel(text='Y5', pos_hint={"center_x": 1.1, "center_y": .32} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel6 = MDLabel(text='Y6', pos_hint={"center_x": 1.1, "center_y": .22} ,font_size=16, theme_text_color="Hint", font_style="Overline")
        outputLabel7 = MDLabel(text='Y7', pos_hint={"center_x": 1.1, "center_y": .12} ,font_size=16, theme_text_color="Hint", font_style="Overline")


        outputBox = MDFloatLayout()
        outputBox.add_widget(self.output0)
        outputBox.add_widget(outputLabel0)
        outputBox.add_widget(self.output1)
        outputBox.add_widget(outputLabel1)
        outputBox.add_widget(self.output2)
        outputBox.add_widget(outputLabel2)
        outputBox.add_widget(self.output3)
        outputBox.add_widget(outputLabel3)
        outputBox.add_widget(self.output4)
        outputBox.add_widget(outputLabel4)
        outputBox.add_widget(self.output5)
        outputBox.add_widget(outputLabel5)
        outputBox.add_widget(self.output6)
        outputBox.add_widget(outputLabel6)
        outputBox.add_widget(self.output7)
        outputBox.add_widget(outputLabel7)

        outputCard.add_widget(outputBox)




        self.boxLayout.add_widget(rightBox)
        
class configScreen2(MDScreen):
    boxLayout = MDBoxLayout()
    img = any
    controller = any


    def on_pre_enter(self, *args):
        
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        return super().on_enter(*args)


    def __init__(self, **kwargs):
        super(configScreen, self).__init__(**kwargs)
        self.boxLayout.orientation = "vertical"
        self.boxLayout.md_bg_color = "silver"
        self.boxLayout.spacing = 10






class productionScreen(MDScreen):
    boxLayout = MDBoxLayout()
    img = any
    imageScatter = any
    imageCard = any
    boardsResults = any
    visionLib = cvLibrary.vision()
    isDemo = True
    plc = controllerTCP()
    tinference1 = any
    tinference2 = any
    source1 = any
    source2 = any
    programInfo1 = None
    programInfo2 = None
    cam1 = any
    cam2 = any
    production_total = 0
    production_ok = 0
    production_ng = 0
    product1_total = 0
    product1_ok = 0
    product1_ng = 0
    product2_total = 0
    product2_ok = 0
    product2_ng = 0
    data_results = []
    image_results = []
    positives = []
    falsepositives = []
    negatives = []
    homography = None

    def on_pre_enter(self, *args):
        
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.productionOK_progress_bar._draw()
        self.productionNG_progress_bar._draw()
        self.production_progress_bar._draw()
        self.product1Total_progress_bar._draw()
        self.product1OK_progress_bar._draw()
        self.product1NG_progress_bar._draw()
        self.product2Total_progress_bar._draw()
        self.product2OK_progress_bar._draw()
        self.product2NG_progress_bar._draw()

        self.loadBoardsResults("")
        

        #self.do_layout()
        return super().on_enter(*args)


    def img_scatter_actions(self, *args):
        #get touch
        for a in args:
            try:
                if(a.type_id == 'touch'):
                    touch = a
            except:
                pass

        if(touch):        
            if(not((touch.psx > 0.05 and touch.psx < 0.75)and(touch.psy<0.88))):
                self.imageScatter.collide_point(touch.pos[0],touch.pos[0])
                return

            # Override Scatter's `on_touch_down` behavior for mouse scroll
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    if self.imageScatter.scale < 10:
                        mat = Matrix().scale(1.04, 1.04, 1.04)
                        self.imageScatter.apply_transform(mat, anchor=touch.pos)
                elif touch.button == 'scrollup':
                    if self.imageScatter.scale > 0.5:
                        mat = Matrix().scale(0.96, 0.96, 0.96)
                        self.imageScatter.apply_transform(mat, anchor=touch.pos)
            
                
            
                
            else:
                if touch.button == 'right':
                    mat = Matrix().scale(1.0, 1.0, 1.0)
                    self.imageScatter.transform = mat
                                    


    def xon_touch_move(self, touch, *args):
       self.imageScatter.pos = (touch.x + args[0].dx, touch.y + args[0].dy)


    def __init__(self, **kwargs):
        super(productionScreen, self).__init__(**kwargs)
        self.boxLayout.orientation = "vertical"
        self.boxLayout.md_bg_color = "silver"
        self.boxLayout.spacing = 10

        #Lef and right boxes
        titleBox = MDFloatLayout(size_hint_y = 0.07)
        programLabel = MDLabel(text='Máquina', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .85})
        #loteQtyLabel = MDLabel(text='Lote', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .75, "center_y": .85})
        self.programRun = MDLabel(text='P&D Prototipo - Linha Motherboard ', font_style="Body1", pos_hint={"center_x": .5, "center_y": .45})
        #self.programLote = MDLabel(text='100000', font_style="Body1", pos_hint={"center_x": .75, "center_y": .45})
        
        productionQtyLabel = MDLabel(text='Produção', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.1, "center_y": .85})
        self.productionQtyRun = MDLabel(text='000', font_style="Body1", pos_hint={"center_x": 1.1, "center_y": .45})
      
        productionOkLabel = MDLabel(text='Aprovados', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.25, "center_y": .85})
        self.productionOkRun = MDLabel(text='000', font_style="Body1", pos_hint={"center_x": 1.25, "center_y": .45})
      
        productionFailLabel = MDLabel(text='Reprovados', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.4, "center_y": .85})
        self.productionFailRun = MDLabel(text='000', font_style="Body1", pos_hint={"center_x": 1.4, "center_y": .45})
      

        
                   
        self.production_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.production_progress_bar.pos_hint = {'center_x': 1.05,'center_y': 0.42}
        self.production_progress_bar.set_widget_size(75)
        self.production_progress_bar.progress_colour = (1, 1, 1, 1)
        self.production_progress_bar.background_colour = (0, 0, 0, .2)
        self.production_progress_bar.value = 0
        


        self.productionOK_progress_bar = circular_progress_bar.CircularProgressBar( )
        self.productionOK_progress_bar.pos_hint = {'center_x': 1.20,'center_y': 0.42}
        self.productionOK_progress_bar.set_widget_size(75)
        self.productionOK_progress_bar.progress_colour = (0, 1, 0, 1)
        self.productionOK_progress_bar.background_colour = (0, 0, 0, .2)
        self.productionOK_progress_bar.value = 0
        self.productionOK_progress_bar._refresh_text()

        self.productionNG_progress_bar = circular_progress_bar.CircularProgressBar( )
        self.productionNG_progress_bar.pos_hint = {'center_x': 1.35,'center_y': 0.42}
        self.productionNG_progress_bar.set_widget_size(75)
        self.productionNG_progress_bar.progress_colour = (1, 0, 0, 1)
        self.productionNG_progress_bar.background_colour = (0, 0, 0, .2)
        self.productionNG_progress_bar.value = 0

        #titleBox.add_widget(self.production_progress_bar)
        titleBox.add_widget(self.productionOK_progress_bar)
        titleBox.add_widget(self.productionNG_progress_bar)
        titleBox.add_widget(programLabel)
        #titleBox.add_widget(loteQtyLabel)
        titleBox.add_widget(self.programRun)
        #titleBox.add_widget(self.programLote)
        titleBox.add_widget(productionQtyLabel)
        titleBox.add_widget(self.productionQtyRun)
        titleBox.add_widget(productionOkLabel)
        titleBox.add_widget(self.productionOkRun)
        titleBox.add_widget(productionFailLabel)
        titleBox.add_widget(self.productionFailRun)
       

        #content
        contentBox = MDBoxLayout(orientation = "vertical", md_bg_color="silver", spacing = 10, size_hint_y = 0.93)
        
        topBox = MDBoxLayout(orientation = "horizontal", spacing = 5, size_hint_y = 0.7, size_hint_x = 1)
        bottomBox = MDBoxLayout(orientation = "horizontal", md_bg_color="silver", spacing = 10, size_hint_y = 0.35, size_hint_x = 1)
        sideBox = MDBoxLayout(orientation = "vertical", spacing = 1, size_hint_y = 1, size_hint_x = 0.2)
        
        imagesBox = MDBoxLayout(orientation = "vertical", md_bg_color="silver", spacing = 10, size_hint_y = 0.99)
        
        topCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=.45, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        topBox.add_widget(topCard)
        
        #Bottom card
        botCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=.45, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        bottomBox.add_widget(botCard)

        botbox = MDFloatLayout(  size_hint_y = 0.99)

        self.resultCard = MDCard( padding = 15, size_hint_y = .9, size_hint_x=0.3, pos_hint= {'center_x': .85,'center_y': 0.5}, line_color='black', line_width=3, md_bg_color = "silver")
        self.resultLabel = MDLabel(text='', halign='center')
        self.resultCard.add_widget(self.resultLabel)
        botbox.add_widget(self.resultCard)

        resultsProductsCard = MDCard( padding = 15, size_hint_y = .96, size_hint_x=0.69, pos_hint= {'center_x': .35,'center_y': 0.5}, md_bg_color = "silver")
        botbox.add_widget(resultsProductsCard)
        botCard.add_widget(botbox)

        

        #Status cards
        statusCard = MDCard( padding = 1, size_hint_y = 1, size_hint_x=1, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        sideBox.add_widget(statusCard)
        
        #top card controls and stats
        topBox.add_widget(sideBox)
        cntr_stat_box = MDBoxLayout(orientation = "horizontal",  spacing = 10, size_hint_y = 0.99)
        
        controlBox = MDCard( padding = 15, size_hint_x=0.25,  size_hint_y = 1, focus_behavior = False, shadow_softness = 2, shadow_offset=(0,1), md_bg_color = "#f8f5f4", line_color=(0.2, 0.2, 0.2, 0.8),  unfocus_color = "darkgrey")
        #statsBox = MDCard( padding = 1, size_hint_y = 1, size_hint_x=0.65, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        cntr_stat_box.add_widget(controlBox)
        #cntr_stat_box.add_widget(statsBox)

        buttonsBox = MDGridLayout(cols=3, padding=4, spacing=80)
        self.btnStart = MDFloatingActionButton( icon='play', type='large', size_hint_x=.2, md_bg_color='silver', icon_color='#311021', padding=2, disabled = True, on_press=self.start_production)
        self.btnStop = MDFloatingActionButton( icon='stop', type='large', md_bg_color='silver', icon_color='#311021', padding=2, disabled = True, on_press=self.stop_production)
        btnReset = MDFloatingActionButton( icon='recycle', type='large', md_bg_color='silver', icon_color='#311021', padding=2, on_press=self.resetProduction)
        btnDemo = MDFloatingActionButton( icon='folder-play-outline', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        btnCamTop = MDFloatingActionButton( icon='camera', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        btnCamBot = MDFloatingActionButton( icon='camera', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        
        btnLoadProgram = MDFloatingActionButton( icon='cogs', type='large', md_bg_color='silver', icon_color='#311021', padding=2, on_press=self.open_program1)
        self.btnSaveDefects = MDFloatingActionButton( icon='image-broken', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        self.btnSavePositives = MDFloatingActionButton( icon='image-check', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        self.btnCheckVisual = MDFloatingActionButton( icon='eye-check', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        self.btnCheckall = MDFloatingActionButton( icon='check-all', type='large', md_bg_color='silver', icon_color='#311021', padding=2)
        self.btnClearStats = MDFloatingActionButton( icon='refresh', type='large', md_bg_color='silver', icon_color='#311021', padding=2, text='teste')
        
        buttonsBox.add_widget(self.btnStart)
        buttonsBox.add_widget(self.btnStop)
        buttonsBox.add_widget(btnReset)
        buttonsBox.add_widget(btnDemo)
        buttonsBox.add_widget(btnCamTop)
        buttonsBox.add_widget(btnCamBot)
        buttonsBox.add_widget(btnLoadProgram)
        buttonsBox.add_widget(self.btnSaveDefects)
        buttonsBox.add_widget(self.btnSavePositives)
        buttonsBox.add_widget(self.btnCheckVisual)
        buttonsBox.add_widget(self.btnCheckall)
        buttonsBox.add_widget(self.btnClearStats)

        controlBox.add_widget(buttonsBox)

        
        #Time card
        side_resultsBox = MDBoxLayout(orientation = "vertical",  spacing = 5, size_hint_y = 1, size_hint_x = .55)
        productsBox = MDBoxLayout(orientation = "horizontal",  spacing = 5, size_hint_y = .3, size_hint_x = 1)
        
        product1Card = MDCard( padding = 15, size_hint_y = 1, size_hint_x = .5, md_bg_color = "silver", style= 'elevated')
        product2Card = MDCard( padding = 15, size_hint_y = 1, size_hint_x = .5, md_bg_color = "silver", style= 'elevated')
        resultsCard = MDCard( padding = 15, md_bg_color = "silver", size_hint_y = .7, style= 'elevated')
        productsBox.add_widget(product1Card)
        productsBox.add_widget(product2Card)
        side_resultsBox.add_widget(productsBox)


        programe1box = MDFloatLayout(  size_hint_y = 0.99)
        programe2box = MDFloatLayout(  size_hint_y = 0.99)
        resultsViewBox = MDFloatLayout()
        product1Card.add_widget(programe1box)
        product2Card.add_widget(programe2box)
        resultsCard.add_widget(resultsViewBox)

        #box product #1
        program1Label = MDLabel(text='Produto #1', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .97})
        self.program1Model = MDLabel(text='(Vazio)', font_size=8, font_style="Body1", pos_hint={"center_x": .5, "center_y": .85})
        program1CycleLabel = MDLabel(text='Ciclo(s)', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .17})
        program1TotalLabel = MDLabel(text='Total >>', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .17})
        self.program1CycleTime = MDLabel(text='0.0s', font_size=8, font_style="Body1", pos_hint={"center_x": .5, "center_y": .05})
        btnLoadProgram1 = MDFloatingActionButton( icon='folder-arrow-down-outline', type='small', md_bg_color='silver', icon_color='#311021', pos_hint={"center_x": .93, "center_y": .83}, on_press=self.open_program1)
        btnFolderImages1 = MDFloatingActionButton( icon='folder-multiple-image', type='small', md_bg_color='silver', icon_color='#311021', pos_hint={"center_x": .93, "center_y": .4}, on_press=self.open_program1)
        programe1box.add_widget(btnLoadProgram1)
        #programe1box.add_widget(btnFolderImages1)
        programe1box.add_widget(program1Label)
        programe1box.add_widget(self.program1Model)
        programe1box.add_widget(program1CycleLabel)
        programe1box.add_widget(self.program1CycleTime)

        self.product1Total_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product1Total_progress_bar.pos_hint = {'center_x': .55,'center_y': 0.75}
        self.product1Total_progress_bar.set_widget_size(90)
        self.product1Total_progress_bar.progress_colour = (1, 1, 1, 1)
        self.product1Total_progress_bar.background_colour = (0, 0, 0, .2)
        self.product1Total_progress_bar.value = 0

        self.product1OK_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product1OK_progress_bar.pos_hint = {'center_x': .8,'center_y': 0.65}
        self.product1OK_progress_bar.set_widget_size(90)
        self.product1OK_progress_bar.progress_colour = (0, 1, 0, 1)
        self.product1OK_progress_bar.background_colour = (0, 0, 0, .2)
        self.product1OK_progress_bar.value = 0

        self.product1NG_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product1NG_progress_bar.pos_hint = {'center_x': 1.05,'center_y': 0.65}
        self.product1NG_progress_bar.set_widget_size(90)
        self.product1NG_progress_bar.progress_colour = (1, 0, 0, 1)
        self.product1NG_progress_bar.background_colour = (0, 0, 0, .2)
        self.product1NG_progress_bar.value = 0
        #programe1box.add_widget(self.product1Total_progress_bar)
        programe1box.add_widget(self.product1OK_progress_bar)
        programe1box.add_widget(self.product1NG_progress_bar)

        self.productStatusInfo1 = MDLabel(text='Aguardando programa...', font_size=8, font_style='Overline', pos_hint={'center_x': 0.77,'center_y': 0.05})
        programe1box.add_widget(self.productStatusInfo1)

        #box product #2
        program2Label = MDLabel(text='Produto #2', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .97})
        self.program2Model = MDLabel(text='(Vazio)', font_size=8, font_style="Body1", pos_hint={"center_x": .5, "center_y": .85})
        program2CycleLabel = MDLabel(text='Ciclo(s)', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .17})
        self.program2CycleTime = MDLabel(text='0.0s', font_size=8, font_style="Body1", pos_hint={"center_x": .5, "center_y": .05})
        btnLoadProgram2 = MDFloatingActionButton( icon='folder-arrow-down-outline', type='small', md_bg_color='silver', icon_color='#311021', pos_hint={"center_x": .93, "center_y": .83}, on_press=self.open_program2)
        btnFolderImages2 = MDFloatingActionButton( icon='folder-multiple-image', type='small', md_bg_color='silver', icon_color='#311021', pos_hint={"center_x": .93, "center_y": .4}, on_press=self.open_program2)
        #btnDemoImage2 = MDSwitch(pos_hint={"center_x": .73, "center_y": .1}, thumb_color_inactive = "red", thumb_color_active = "white", icon_active = "check", icon_active_color = "green", icon_inactive_color = "white", icon_inactive = "close")
        #programe2box.add_widget(btnDemoImage2)
        programe2box.add_widget(btnLoadProgram2)
        #programe2box.add_widget(btnFolderImages2)
        programe2box.add_widget(program2Label)
        programe2box.add_widget(self.program2Model)
        programe2box.add_widget(program2CycleLabel)
        programe2box.add_widget(self.program2CycleTime)

        self.product2Total_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product2Total_progress_bar.pos_hint = {'center_x': .55,'center_y': 0.75}
        self.product2Total_progress_bar.set_widget_size(90)
        self.product2Total_progress_bar.progress_colour = (1, 1, 1, 1)
        self.product2Total_progress_bar.background_colour = (0, 0, 0, .2)
        self.product2Total_progress_bar.value = 0

        self.product2OK_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product2OK_progress_bar.pos_hint = {'center_x': .8,'center_y': 0.65}
        self.product2OK_progress_bar.set_widget_size(90)
        self.product2OK_progress_bar.progress_colour = (0, 1, 0, 1)
        self.product2OK_progress_bar.background_colour = (0, 0, 0, .2)
        self.product2OK_progress_bar.value = 0

        self.product2NG_progress_bar = circular_progress_bar.CircularProgressBar(  )
        self.product2NG_progress_bar.pos_hint = {'center_x': 1.05,'center_y': 0.65}
        self.product2NG_progress_bar.set_widget_size(90)
        self.product2NG_progress_bar.progress_colour = (1, 0, 0, 1)
        self.product2NG_progress_bar.background_colour = (0, 0, 0, .2)
        self.product2NG_progress_bar.value = 0
        #programe2box.add_widget(self.product2Total_progress_bar)
        programe2box.add_widget(self.product2OK_progress_bar)
        programe2box.add_widget(self.product2NG_progress_bar)

        self.productStatusInfo2 = MDLabel(text='Aguardando programa...', font_size=8, font_style='Overline', pos_hint={'center_x': 0.77,'center_y': 0.05})
        programe2box.add_widget(self.productStatusInfo2)
        self.state1 = 0
        self.state2 = 0

        #Box view results
        resultsViewLabel = MDLabel(text='Resultados', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .5, "center_y": .99})
        resultsViewBox.add_widget(resultsViewLabel)

        results1imagesSegment = MDSegmentedControl(
            MDSegmentedControlItem(
                        text="Superior",
                        on_active = self.on_active
                    ),
                    MDSegmentedControlItem(
                        text="Inferior"
                    ),
                    MDSegmentedControlItem(
                        text="Ambos"
                    ),
                    pos_hint={"center_x": 0.52, "center_y": .96},
                    segment_panel_height = "32dp"
                )
        


        #Positive list
        positivesViewLabel = MDLabel(text='Aprovados', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .61, "center_y": .87})
        self.positivesQtyViewLabel = MDLabel(text='Qtd.:', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .77, "center_y": .87})
        resultsPositivesScrollBox = MDScrollView(self.positives, md_bg_color = "yellowgreen", do_scroll_x=False, do_scroll_y=True, size_hint_x = .3, size_hint_y = 0.85, pos_hint={"center_x": .15, "center_y": .42}, radius = 12)
        self.positivesList = MDList( radius = 12, spacing = 10)
        resultsPositivesScrollBox.add_widget(self.positivesList)

        #Negative list
        negativesViewLabel = MDLabel(text='Reprovados', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": .96, "center_y": .87})
        self.negativesQtyViewLabel = MDLabel(text='Qtd.:', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.12, "center_y": .87})
        resultsNegativesScrollBox = MDScrollView(self.positives, md_bg_color = "red", do_scroll_x=False, do_scroll_y=True, size_hint_x = .3, size_hint_y = 0.85, pos_hint={"center_x": .5, "center_y": .42}, radius = 12)
        self.negativesList = MDList( radius = 12, spacing = 10)
        resultsNegativesScrollBox.add_widget(self.negativesList)

        #FalsePositive list
        falsepositivesViewLabel = MDLabel(text='Outros', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.33, "center_y": .87})
        self.falsepositivesQtyViewLabel = MDLabel(text='Qtd.:', font_size=8, theme_text_color="Hint", font_style="Overline", pos_hint={"center_x": 1.45, "center_y": .87})
        resultsFalsePositivesScrollBox = MDScrollView(self.positives, md_bg_color = "lightblue", do_scroll_x=False, do_scroll_y=True, size_hint_x = .3, size_hint_y = 0.85, pos_hint={"center_x": .85, "center_y": .42}, radius = 12)
        self.falsepositivesList = MDList( radius = 12, spacing = 10)
        resultsFalsePositivesScrollBox.add_widget(self.falsepositivesList)

        resultsViewBox.add_widget(positivesViewLabel)
        resultsViewBox.add_widget(negativesViewLabel)
        resultsViewBox.add_widget(falsepositivesViewLabel)
        resultsViewBox.add_widget(self.falsepositivesQtyViewLabel)
        resultsViewBox.add_widget(self.positivesQtyViewLabel)
        resultsViewBox.add_widget(self.negativesQtyViewLabel)

        resultsViewBox.add_widget(results1imagesSegment)
        resultsViewBox.add_widget(resultsPositivesScrollBox)
        resultsViewBox.add_widget(resultsNegativesScrollBox)
        resultsViewBox.add_widget(resultsFalsePositivesScrollBox)


        side_resultsBox.add_widget(resultsCard)
        cntr_stat_box.add_widget(side_resultsBox)

        

        #Results card
        self.resultsContent = MDBoxLayout()
        self.boardsResults = MDBoxLayout(id='boardsResults', size_hint_y = 1)
        self.boardsHistoryScroll = MDScrollView(self.boardsResults,md_bg_color = "white", do_scroll_x=True, do_scroll_y=False, size_hint_x = 1, size_hint_y = 0.8)

        self.resultsHistory = MDSelectionList( selected_mode=True, id='results', height=self.boardsHistoryScroll.height)

        self.resultsContent.add_widget(self.boardsHistoryScroll)
        
        self.loadBoardsResults( "")

        
        resultsProductsCard.add_widget(self.resultsContent)


        topCard.add_widget(cntr_stat_box)

        #image card top - Status 
        self.imageCardPA = MDCard( padding = 1, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        imagesBox.add_widget(self.imageCardPA)

        self.imgPA = Image(size_hint_y = 1, size_hint_x=1, allow_stretch = True, keep_ratio = False)
        self.imgPA.source = 'not-found-image.jpg'

        self.imageScatter = Scatter( do_rotation=False, auto_bring_to_front=True )
        #self.imageScatter.add_widget(self.img)

        stencil = StencilView()
        stencil.add_widget(self.imageScatter)
        self.imageCardPA.add_widget(self.imgPA)


        #image card bottom
        self.imageCardPB = MDCard( padding = 1, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")        
        imagesBox.add_widget(self.imageCardPB)
        
        self.imgPB = Image(size_hint_y = 1, size_hint_x=1, allow_stretch = True, keep_ratio = False)
        self.imgPB.source = 'not-found-image.jpg'

        self.imageScatterPB = Scatter( do_rotation=False, auto_bring_to_front=True, size_hint_x=1, size_hint_y=1 )
        #self.imageScatterPB.add_widget(self.imgPB)


        stencilB = StencilView(size_hint=(1.0,1.0), pos_hint={"center_x": .5, "center_y": .5})
        stencilB.add_widget(self.imageScatterPB)
        self.imageCardPB.add_widget(self.imgPB)


        #######################


        contentBox.add_widget(topBox)
        
  
        contentBox.add_widget(bottomBox)

        statusCard.add_widget(imagesBox)

        self.boxLayout.add_widget(titleBox)
        self.boxLayout.add_widget(contentBox)
        
        self.add_widget(self.boxLayout)


    def on_active(
        self,
        segmented_control: MDSegmentedControl,
        segmented_item: MDSegmentedControlItem,
    ) -> None:
        '''Called when the segment is activated.'''

    def loadBoardsResults(self, components):
        self.resultsHistory.clear_widgets()
        lis_id = 0                       
        
        
        try:
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg', 'result': 'NG', 'text':'teste1', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg', 'result': 'OK','text':'teste2', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg',  'result': 'OK','text':'teste3', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg',  'result': 'NG','text':'teste4', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg',  'result': 'OK','text':'teste1', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg',  'result': 'OK','text':'teste2', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg', 'result': 'OK', 'text':'teste3', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           # data.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg', 'result': 'NG','text':'teste4', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           pass
        except:
            toast("Falha!", background=(1,1,0,.7))    

        self.rv = horrecycleview.HRV(self.data_results) 
        self.rv.width = self.resultsContent.width
        self.rv.height = self.resultsContent.height
        self.rv.name = 'boardsResults'   
        self.resultsHistory.add_widget( self.rv)
        self.show_results()



    def show_results(self, *args):
        self.resultsContent.clear_widgets()
        self.boardsHistoryScroll.clear_widgets()
        self.boardsHistoryScroll = MDScrollView(self.resultsHistory)
        self.resultsContent.add_widget(self.boardsHistoryScroll)
        self.activeView = 'results'
        

    


    state1 = 0
    State2 = 0
    def resetProduction(self, *args):
        if(self.state1 < 2 and self.state2 < 2):
            self.btnStart.disabled = True
            self.btnStop.disabled = True
            self.program1Model.text = "(Vazio)"
            self.program2Model.text = "(Vazio)"
            self.programInfo1 = None
            self.programInfo2 = None

            self.product1Total_progress_bar.value = 0
            self.product1OK_progress_bar.value = 0
            self.product1NG_progress_bar.value = 0
            self.product2Total_progress_bar.value = 0
            self.product2OK_progress_bar.value = 0
            self.product2NG_progress_bar.value = 0
            self.production_progress_bar.value = 0
            self.productionOK_progress_bar.value = 0
            self.productionNG_progress_bar.value = 0
            
            self.state1 = 0
            self.state2 = 0

            self.data_results = []
        else:
            toast("Reset só é possível com produção parada...", background=(1,0,0,.7))



    #open program file
    file_path = StringProperty("No file chosen")
    the_popup = ObjectProperty(None)
    program_side = 0
    def open_program1(self, *args):     
        self.program_side = 1
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Abrir programa", content=content,
                            size_hint=(0.7, 0.5))
        self._popup.open()

    def open_program2(self, *args):
        self.program_side = 2     
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Abrir programa", content=content,
                            size_hint=(0.7, 0.5))
        self._popup.open()


    def load(self, path, filename):
        try:
            self.progFile = filename[0]
            if self.program_side == 1:
                with open(self.progFile, 'r') as prog_file:
                    self.programInfo1 = json.load(prog_file)
                #refresh program info
                self.program1Model.text = self.programInfo1['name']
                self.btnStart.disabled = False
                self.productStatusInfo1.text = 'Aguardando inicio...'
                self.state1 = 1
            elif self.program_side == 2:
                with open(self.progFile, 'r') as prog_file:
                    self.programInfo2 = json.load(prog_file)
                #refresh program info
                self.program2Model.text = self.programInfo2['name']
                self.btnStart.disabled = False
                self.productStatusInfo2.text = 'Aguardando inicio...'
                self.state2 = 1

            self._popup.dismiss()

        except Exception as ex:
            self.programInfo1 = None
            self.programInfo2 = None
            self.jsonFile = ''
            self.progFile = ''
            self._popup.dismiss()
            toast("Falha ao tentar abrir o arquivo...", background=(1,0,0,.7))


    def loadComponents(self, components):
        self.modelsComponents.clear_widgets()
        lis_id = 0                       
        data = []
        for sm in components:
            #active icon
            if sm['inspect'] == True:
                inspect_icon = 'images/enabled.png'
            else:
                inspect_icon = 'images/disabled.png'


            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #polarity
            if sm['polarity'] != '':
                pol_icon = 'images/polarity.png'
            else:
                pol_icon = ''

            try:
                data.append({'active_icon':inspect_icon, 'left_icon': pol_icon, 'text':sm['pose'], 'right_icon':type_icon, 'status_icon':'' })
            except:
                toast(sm, background=(1,1,0,.7))    

        self.rv = myrecycleview.RV(data) 
        self.rv.height = self.modelsContent.height
        self.rv.name = 'components'   
        self.modelsComponents.add_widget( self.rv)


    def dismiss_dialog(self, *args):
        self.dialog.dismiss()
        toast("Ação cancelada pelo usuário...", background=(0,1,1,.7))

    def dismiss_popup(self, *args):
        self._popup.dismiss()
        toast("Ação cancelada pelo usuário...", background=(0,1,1,.7))
    

    def threadViewupdate(self, side, image, *args):
        if(side == 'top'):
            self.imgPA.texture = self.visionLib.opencv2kivyImage(image) 
        elif(side == 'bot'):
            self.imgPB.texture = self.visionLib.opencv2kivyImage(image) 



    def image_refresh(self, side, image):
        #Load Objects
        try:
            if(side == 'top'):
                objects_comp = self.programInfo1['board']['components']
                #objects_box = self.results1[0].boxes
            elif(side == 'bot'):
                objects_comp = self.programInfo2['board']['components']

        except:
            objects = []
              
        if(len(objects_comp)>0):
            if(side == 'top'):
                drawingImage = image.copy()
                self.visionLib.drawObjects(drawingImage, objects_comp, False, 0, 0, 0, self.homography)
            
                #nodes = self.modelsContent.children[0].children[0].children[0].children[0].selected_nodes
                #if(len(nodes) > 0):
                #    self.visionLib.drawSelectedObject(drawingImage, objects_comp[nodes[0]])
                #self.visionLib.image = drawingImage
                Clock.schedule_once(partial( self.threadViewupdate, side, drawingImage) )  
            
            elif(side == 'bot'):
                drawingImage = image.copy()
                self.visionLib.drawObjects(drawingImage, objects_comp, False, 0, 0, 0, self.homography)
            
                #nodes = self.modelsContent.children[0].children[0].children[0].children[0].selected_nodes
                #if(len(nodes) > 0):
                #    self.visionLib.drawSelectedObject(drawingImage, objects_comp[nodes[0]])
                #self.visionLib.image = drawingImage
                Clock.schedule_once(partial( self.threadViewupdate, side, drawingImage) )  

        else:
            if(side == 'top'):
                self.imgPA.texture = self.visionLib.opencv2kivyImage(image)
            elif(side == 'top'):
                self.imgPB.texture = self.visionLib.opencv2kivyImage(image)




    def image_next(self, side, *args):
        try:
            if(side == 'top'):
                self.productStatusInfo1.text = "Carregando imagem..."
                #self.state1 = 3

            elif(side == 'bot'):
                self.productStatusInfo2.text = "Carregando imagem..."
                #self.state2 = 3
            

            extensions = [ '*.jpg', '*.jpeg', '*.bmp'] #config.images_ext#('Images/*.png', 'Images/*.jpg')
            files_list = []
            for ext in extensions:
                files_list.extend(glob.glob( config_object["APPINFO"]["imagespath"] + ext))

            dir = files_list#glob.glob(config_object["APPINFO"]["imagespath"])
            
            if(side == 'top'):
                if(self.dirSelectedImage1 >= len(dir)-1):
                    self.dirSelectedImage1 = 0
                else:
                    self.dirSelectedImage1 += 1  
                imageSource = dir[self.dirSelectedImage1]  
            elif(side == 'bot'):
                if(self.dirSelectedImage2 >= len(dir)-1):
                    self.dirSelectedImage2 = 0
                else:
                    self.dirSelectedImage2 += 1    
                imageSource = dir[self.dirSelectedImage2]
            
            #cv image
            #self.cvImage = self.visionLib.read_image(self.imageSource)
            #self.mainImageLoad(self.imageSource)
            _image = self.visionLib.read_image(imageSource) 
            self.image_refresh(side, _image)
            return _image
            #self.image_refresh()

            #self.dialog.dismiss()

        except Exception as ex:
            self.imageSource = ''

    def start_production(self, *args):
        if self.isDemo:
            self.start_demo_production()
        else:
            self.start_real_production()



    def manual_action(self, btn, *args):
        m = -1
        if btn.id == "sw_ok":
            m = 0
        elif btn.id == "ilum_red":
            m = 1
        elif btn.id == "ilum_yel":
            m = 2
        elif btn.id == "ilum_gre":
            m = 3
        elif btn.id == "prod_ok":
            m = 4
        elif btn.id == "inspect_finish":
            m = 5
        elif btn.id == "product_ok":
            m = 6
        elif btn.id == "product_ng":
            m = 7
        elif btn.id == "bypass":
            m = 10
        elif btn.id == "board_in":
            m = 11
        elif btn.id == "board_out":
            m = 12
        elif btn.id == "actuator_i":
            m = 13
        elif btn.id == "actuator_ii":
            m = 14
        elif btn.id == "actuator_iii":
            m = 15
        else:
            m = -1 


        if self.plc.setMEM(m, not self.plc.MEMS[m]):
            self.plc.refreshPlcData()
            if self.plc.MEMS[m] == True:
                btn.md_bg_color = 'green'
            else:
                btn.md_bg_color = 'red'
        

    
    def plc_connect(self, *args):
        try:
            if not self.plc.CLIENT:
                if self.plc.startClient(config_object['CONTROLLER']['host'], int( config_object['CONTROLLER']['port'] ) ):
                    self.plc.refreshPlcData()
                    #self.btnConnectPLC.md_bg_color = "yellowgreen"
                    toast("Controlador conectado!!!", background=(0,1,0,.7))
                else:
                    toast("Falha ao tentar conectar com controlador!", background=(1,0,0,.7))   
                    self.plc.CLIENT = None
                    #self.btnConnectPLC.md_bg_color = 'red'
            else:
                self.CLIENT.close()
                self.plc.CLIENT = None
        except:
            toast("Falha ao tentar conectar com controlador!", background=(1,0,0,.7))   
            self.plc.CLIENT = None
            #self.btnConnectPLC.md_bg_color = 'red'


        

    def heart_beat(self, *args):
        if(self.plc.MEMS[0] == False):
            self.plc.setMEM(0, True)
        else:
            self.plc.setMEM(0, False)






    def start_real_production(self, *args):
        #reset state
        if(self.state1 > 1):
            self.state1 = 1
        if(self.state2 > 1):
            self.state2 = 1
        
        #connect to controler
        if not self.plc.CLIENT:
            self.plc_connect()
            

        #Interface relay
        if(self.plc.CLIENT):
            self.plc.refreshPlcData()
            self.plc.setMEM(0, True)
            
        else:
            return False

        self.plc.refreshPlcData()

        if((self.state1 == 1 or self.state2 == 1) and self.plc.INPUTS[0] == True and self.plc.INPUTS[2] == False and self.plc.OUTPUTS[0] == True and self.plc.CLIENT != None):
            Clock.schedule_interval(self.production_status, 0.5)
            Clock.schedule_interval(self.heart_beat, 2)

            #counters
            self.product1total = 0
            self.product1OK = 0
            self.product1NG = 0
            self.product2total = 0
            self.product2OK = 0
            self.product2NG = 0

            if(self.state1 == 1):
                self.state1 = 2 #Start production
            
            if(self.state2 == 1):
                self.state2 = 2

            #if(self.state1 != 2 or self.state2 != 2):

            #self.dirSelectedImage1 = 0
            #self.dirSelectedImage2 = 0
            
            #Connect cameras
            if(self.state1 == 2):
                if not self.initialize_cam(1, config_object['CAMERA']['cam1_name'], config_object['CAMERA']['cam1_type']):
                    self.stop_production()
                    return False
                self.state1 = 3 #Camera ok

            if(self.state2 == 2):
                if not self.initialize_cam(2, config_object['CAMERA']['cam2_name'], config_object['CAMERA']['cam2_type']):
                    self.stop_production()
                    return False
                self.state2 = 3 #camera ok

            try:

                #load image
                #product 1
                if(self.programInfo1 != None or self.programInfo2 != None):
                    self.production1th = threading.Thread(target=self.run_production, name='both', args=[self.plc, self.cam1, self.tinference2, self.source2])
                    self.production1th.start()
                    self.btnStart.disabled = True
                    self.btnStop.disabled = False
            
            except:
                pass
                

            try:
                #product 2
                #if(self.programInfo2 != None):
                #    self.production2th = threading.Thread(target=self.run_production, name='bot', args=[self.plc, self.cam2, self.tinference1, self.source1])
                #    self.production2th.start()
                #    self.btnStart.disabled = True
                #    self.btnStop.disabled = False
                pass
            
            except:
                pass

        elif(self.plc.INPUTS[0] != True):
            toast("Não é possível iniciar produção com equipamento com emergência acionado!", background=(1,0,0,.7)) 
        
        elif(self.plc.INPUTS[2] != False):
            toast("Placa no processo, favor remover e tentar novamente!", background=(1,0,0,.7)) 

        elif(self.plc.CLIENT == None):
            toast("Placa no processo, sem comunicação com controlador!", background=(1,0,0,.7)) 


    def initialize_cam(self, num_cam, name, type):
        if(num_cam == 1):
            if(type == 'basler'):
                self.cam1 = usb_camera.UsbCam()
                self.cam1.initialize()
                if self.cam1.connect(name):
                    return True
                else: 
                    return False
            else:
                try:
                    self.cam1 = self.visionLib.usb_cam_initialize( int(name) )
                    return True
                
                except:
                    return False
        elif(num_cam == 2):
            if(type == 'basler'):
                self.cam2 = usb_camera.UsbCam()
                self.cam2.initialize()
                if self.cam2.connect(name):
                    return True
                else: 
                    return False
            else:
                try:
                    self.cam2 = self.visionLib.usb_cam_initialize( int(name) )
                    return True
                
                except:
                    return False
        




    def take_picture(self, cam):
        
        if cam.camera.IsOpen:
            im = cam.acquire_image()
           
            return im
        else:
            return None


   # def take_picture(self, *args):
   #     if config_object['CAMERA']['cam1_type'] == 'basler':
   #         try:
   #             self.cam = usb_camera.UsbCam()
   #             self.cam.initialize()
   #             if self.cam.connect(config_object['CAMERA']['cam1_name']):
   #                 self.im = self.cam.acquire_image()
   #                 self.visionLib.image = self.im
   #                 self.image_refresh()
   #         except:
   #             toast("Falha ao tentar capturar imagem de camera BASLER!", background=(1,0,0,.7))  
   #     else:
   #         try:
   #             self.im = self.visionLib.usb_cam_capture( int(config_object['CAMERA']['cam1_name']) )
   #             self.visionLib.image = self.im
   #             self.image_refresh()
   #         except:
   #             toast("Falha ao tentar capturar imagem de camera BASLER!", background=(1,0,0,.7)) 




    def start_demo_production(self, *args):
        if(self.state1 == 1 or self.state2 == 1):
            Clock.schedule_interval(self.production_status, 0.5)

            #counters
            self.product1total = 0
            self.product1OK = 0
            self.product1NG = 0
            self.product2total = 0
            self.product2OK = 0
            self.product2NG = 0

            if(self.state1 == 1):
                self.state1 = 2 #Start production
            
            if(self.state2 == 1):
                self.state2 = 2

            self.dirSelectedImage1 = 0
            self.dirSelectedImage2 = 0
            
            try:

                #load image
                #source = self.production_load_image('file', 'top')
                #product 1
                if(self.programInfo1 != None):
                    self.production1th = threading.Thread(target=self.run_production_demo, name='top', args=[self.state1, self.source1])
                    self.production1th.start()
                    self.btnStart.disabled = True
                    self.btnStop.disabled = False
            
            except:
                pass
                

            try:
                #product 2
                if(self.programInfo2 != None):
                    self.production2th = threading.Thread(target=self.run_production_demo, name='bot', args=[self.state2, self.source2])
                    self.production2th.start()
                    self.btnStart.disabled = True
                    self.btnStop.disabled = False
            
            except:
                pass

    def production_load_image(self, type, side): #type => file, usb, basler
        if(type == 'file'):
            source = self.image_next(side)
            
        return source
    



    def production_load_model(self, side):
        #load model AI
        if(side == 'top'):
            model = self.programInfo1['annotation_file']#"best (1).pt"#"Yolo-Weights/datasets/digAOIv8-010523-full.pt"
        else:
             model = self.programInfo2['annotation_file']
        return model

    def production_showresults(self, tinference, source, side, *args):
        self.main_status = "Inferencia realizada com sucesso!!! tempo >> "+str(tinference)
        #self.loadResults(self.results, self.classes)


        #draw results
        if(self.results1 or self.results2):
            #check results
            if(side == 'top'):
                source1, self.positives, self.falsepositives, self.negatives = self.visionLib.check_program(source, self.results1, side, self.programInfo1, self.classes)
                Clock.schedule_once((partial(self.load_production_results, source1, self.results1,  self.classes, side)))
                self.visionLib.draw_inference_results(source1, self.results1, self.classes)
            else:
                source2, self.positives, self.falsepositives, self.negatives = self.visionLib.check_program(source, self.results2, side, self.programInfo2, self.classes)
                Clock.schedule_once((partial(self.load_production_results, source2, self.results2,  self.classes, side)))
                self.visionLib.draw_inference_results(source2, self.results2, self.classes)

            

        #if(side == 'top'):
        #    self.imgPA.texture = self.visionLib.opencv2kivyImage(source)
        #    self.program1CycleTime.text = str(tinference)

        #elif(side == 'bot'):
        #    self.imgPB.texture = self.visionLib.opencv2kivyImage(source)
        #    self.program2CycleTime.text = str(tinference)
###############################################################################################################


    def calculate_iou(self, box_1, box_2):
        iou = bops.box_iou(box_1, box_2)
        return iou
    
    def check_comp(self, res, comp):
        box1 = torch.tensor([comp], dtype=torch.float)
        box2 = torch.tensor([res], dtype=torch.float)
        iou = float(self.calculate_iou(box2, box1))
        _iou = float(self.calculate_iou(box1, box2))
        return _iou

    


    



##############################################################################################################


    def load_production_results(self, source, results,  classes, side, *args):
        #self.modelsResultsMatches.clear_widgets()
        lis_id = 0                       
        data = []
        type_icon = ''
        for sm in self.positives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #result            
            result_icon = 'images/checkmark.png'
            f = float(sm['conf'])
            text = sm['pose']+' << '+f'{f:.2f}'+' >> '
            #try:
            #    data.append({'active_icon':type_icon, 'left_icon': '', 'text':text, 'right_icon':result_icon, 'status_icon':'' })
            #except:
            #    toast(sm, background=(1,1,0,.7))    



        for sm in self.falsepositives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #result            
            result_icon = 'images/error.png'
            f = float(sm['conf'])
            text = sm['pose']+' << '+f'{f:.2f}'+' >> '
            #try:
            #    data.append({'active_icon':type_icon, 'left_icon': '', 'text':text, 'right_icon':result_icon, 'status_icon':'' })
            #except:
            #    toast(sm, background=(1,1,0,.7))    



        for sm in self.negatives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''


        #result            
        result_icon = 'not-found-image.jpg'
        product_name = str(time.time())
        try:
            if (self.visionLib.write_image(source, config_object['APPINFO']['resultspath']+'prod_'+product_name+'NG.jpg')):
                result_icon =  config_object['APPINFO']['resultspath']+'prod_'+str(time.time())+'NG.jpg'
        except Exception as ex:
            pass
            
            #try:
            #    data.append({'active_icon':type_icon, 'left_icon': '', 'text':sm['pose'], 'right_icon':result_icon, 'status_icon':'' })
            #except:
            #    toast(sm, background=(1,1,0,.7))    


        if(len(self.positives) > 10):
            result_label = 'OK'
        else:
            result_label = 'NG'

        #Result history
        try:
           #self.data_results.append({'active_icon':'images/Image__2022-09-23__19-59-27.jpg', 'result': 'NG', 'text':'teste1', 'right_icon':'images/green.png', 'status_icon':'images/green.png' })
           self.data_results.append({'active_icon':result_icon, 'result': result_label, 'text':product_name, 'side':side, 'status_icon':'images/green.png', 'positives': str(len(self.positives)), 'negatives':str(len(self.negatives)), 'falsepositives':str(len(self.falsepositives)) })
           #self.image_results.append(self.source1)
        except:
            toast("Falha!", background=(1,1,0,.7))  

        
        #Results list
        try:
            if(side == 'top'):
                ori = self.source1.copy()
            else:
                ori = self.source2.copy()

            #Positives
            self.positivesList.clear_widgets()
            self.positivesQtyViewLabel.text = str(len(self.positives))
            for c in self.positives:
                card = HeroResults()
                
                card.set_comp(c['pose'])
                card.set_conf("%.2f" % c['conf'])
                card.set_model(c['model'])
                
                x = c['x']
                y = c['y']
                a = c['a']
                boxX = c['box_x']
                boxY = c['box_y']
                
                try:
                    cut = self.visionLib.cut_comp(ori.copy(), x, y, a, boxX, boxY)
                    img_txt = self.visionLib.opencv2kivyImage( cut.copy() )
                except:
                    img_txt = Image(source="not-found-image.jpg").texture

                
                card.set_texture(img_txt)

                self.positivesList.add_widget(card)


            #Negatives
            self.negativesList.clear_widgets()
            self.negativesQtyViewLabel.text = str(len(self.negatives))
            for c in self.negatives:
                card = HeroResults()
                
                card.set_comp(c['pose'])
                card.set_conf("%.2f" % c['conf'])
                card.set_model(c['model'])
                
                x = c['x']
                y = c['y']
                a = c['a']
                boxX = c['box_x']
                boxY = c['box_y']
                
                try:
                    cut = self.visionLib.cut_comp(ori.copy(), x, y, a, boxX, boxY)
                    img_txt = self.visionLib.opencv2kivyImage( cut.copy() )
                except:
                    img_txt = Image(source="not-found-image.jpg").texture

                
                card.set_texture(img_txt)

                self.negativesList.add_widget(card)

            
            #False Positives
            self.falsepositivesList.clear_widgets()
            self.falsepositivesQtyViewLabel.text = str(len(self.falsepositives))
            for c in self.falsepositives:
                card = HeroResults()
                
                card.set_comp(c['pose'])
                card.set_conf("%.2f" % c['conf'])
                card.set_model(c['model'])
                
                x = c['x']
                y = c['y']
                a = c['a']
                boxX = c['box_x']
                boxY = c['box_y']
                
                try:
                    cut = self.visionLib.cut_comp(ori.copy(), x, y, a, boxX, boxY)
                    img_txt = self.visionLib.opencv2kivyImage( cut.copy() )
                except:
                    img_txt = Image(source="not-found-image.jpg").texture

                
                card.set_texture(img_txt)

                self.falsepositivesList.add_widget(card)

        except Exception as ex:
            pass




        






    def on_good_result(self, *args):
        pass


    def on_bad_result(self, *args):
        pass 



    def production_status(self, side, *args):
       #Side top
        if(self.state1 == 1):
            self.productStatusInfo1.text = 'Aguardando inicio da produção'
        elif(self.state1 == 2):
            self.productStatusInfo1.text = 'Iniciando produção...'
        elif(self.state1 == 3):
            self.productStatusInfo1.text = 'Iniciando processo CAM/MAQ...'    
        elif(self.state1 == 5):
            self.productStatusInfo1.text = 'Carregando modelos IA...'
        elif(self.state1 == 4):
            self.productStatusInfo1.text = 'Aguardando equipamento OK...'
        elif(self.state1 == 6):
            self.productStatusInfo1.text = 'Solicitando entrada/produto...' 
        elif(self.state1 == 7):
            self.productStatusInfo1.text = 'Aguardando produto/imagem...'
        elif(self.state1 == 8):
            self.productStatusInfo1.text = 'Executando inferência no produto...'
        elif(self.state1 == 9):
            self.productStatusInfo1.text = 'Executando leitura de serial do produto...'
        elif(self.state1 == 10):
            self.productStatusInfo1.text = 'Atualizando resultados...'
            self.production_showresults(self.tinference1, self.source1.copy(), 'top') 
            self.state1 = 11
            #Image
            try:
                self.imgPA.texture = self.visionLib.opencv2kivyImage(self.source1)
                self.image_refresh('top', self.source1)

            except Exception as ex:
                pass

           
        elif(self.state1 == 11):
            self.productStatusInfo1.text = 'Aguardando saida/produto...'
        elif(self.state1 == 0):
            self.productStatusInfo1.text = 'Parado sem programa.'
        else:
            self.productStatusInfo1.text = 'Estado indefinido...'

        #side bot
        if(self.state2 == 1):
            self.productStatusInfo2.text = 'Aguardando inicio da produção'
        elif(self.state2 == 2):
            self.productStatusInfo2.text = 'Iniciando produção...'
        elif(self.state2 == 3):
            self.productStatusInfo2.text = 'Iniciando processo CAM/MAQ...'
        elif(self.state2 == 5):
            self.productStatusInfo2.text = 'Carregando modelos IA...'
        elif(self.state2 == 4):
            self.productStatusInfo2.text = 'Aguardando equipamento OK...'
        elif(self.state2 == 6):
            self.productStatusInfo2.text = 'Solicitando entrada/produto...'    
        elif(self.state2 == 7):
            self.productStatusInfo2.text = 'Aguardando produto/imagem...'
        elif(self.state2 == 8):
            self.productStatusInfo2.text = 'Executando inferência no produto...'
        elif(self.state2 == 9):
            self.productStatusInfo2.text = 'Executando leitura de serial do produto...'
        elif(self.state2 == 10):
            self.productStatusInfo2.text = 'Atualizando resultados...'
            self.production_showresults( self.tinference2, self.source2.copy(), 'bot' )
            self.state2 = 11
            #Image
            try:
               
                self.imgPB.texture = self.visionLib.opencv2kivyImage(self.source2)
                self.image_refresh('bot', self.source2)
            except:
                pass
            self.state2 = 11
        elif(self.state2 == 11):
            self.productStatusInfo2.text = 'Aguardando saida/produto...'
        elif(self.state2 == 0):
            self.productStatusInfo2.text = 'Parado sem programa.'
        else:
            self.productStatusInfo2.text = 'Estado indefinido...'


        try:
        #counter
            self.productionQtyRun.text = str(self.production_total)
            self.productionOkRun.text = str(self.production_ok)
            self.productionFailRun.text = str(self.production_ng)

            self.product1Total_progress_bar.set_value( (self.product1total) )
            self.product1OK_progress_bar.set_value( int(self.product1OK/(self.product1total)*100)) 
            self.product1NG_progress_bar.set_value( int(self.product1NG/(self.product1total)*100))

            self.product2Total_progress_bar.value = self.product2total
            self.product2OK_progress_bar.value = self.product2OK
            self.product2NG_progress_bar.value = self.product2NG
        except Exception as ex:
            pass
        #controller
        self.plc.refreshPlcData()

        #History
        try:
            if(len(self.rv.data) != len(self.data_results)and(len(self.data_results)>0)):
                
                if(self.data_results[len(self.data_results)-1]['result'] == 'NG'):
                    self.loadBoardsResults('')

                    self.resultCard.md_bg_color = 'red'
                    self.resultLabel.text = 'REPROVADO'
                    if(self.data_results[len(self.data_results)-1]['side']=='top'):
                        self.product1NG += 1
                    else:
                        self.product2NG += 1
                else:
                    self.loadBoardsResults('')

                    self.resultCard.md_bg_color = 'lime'
                    self.resultLabel.text = 'APROVADO'
                    if(self.data_results[len(self.data_results)-1]['side'] == 'top'):
                        self.product1OK += 1
                    else:
                        self.product2OK += 1
        except:
            pass

        


    def run_production(self, *args):
        th_plc = args[0] 
        th_cam = args[1]
        th_inf = args[2]
        th_source = args[3]
        

        if(self.state1 == 3 or self.state2 == 3):
            
            
            side = threading.current_thread().name
            
            if(self.state1 == 3 ):
                self.state1 = 4 #load model
            if(self.state2 == 3 ):
                self.state2 = 4
            
            if(self.state1 == 4):
                model1 = "best (1).pt"#"Yolo-Weights/datasets/digAOIv8-010523-full.pt"
                self.state1 = 5#program loaded
            
            if(self.state2 == 4):
                model2 = "best (1).pt"
                self.state2 = 5#program loaded


            #Set initial 
            if((self.state1 == 5 or self.state2 == 5) and self.plc.OUTPUTS[0] == True):
                th_plc.setMEM(22, False)
                th_plc.setMEM(4, False)
                th_plc.setMEM(20, True) #Production initialize command
               
            else:
                return False

            emergency_ok = th_plc.INPUTS[0]
            interface_ok = th_plc.OUTPUTS[0]
            client_ok = th_plc.CLIENT != None

            if(self.state1 == 5 and config_object['CAMERA']['cam1_type'] != 'basler'):
                self.cam1.grab()

            if(self.state2 == 5 and config_object['CAMERA']['cam2_type'] != 'basler'):
                self.cam2.grab()

            ttotal = 0.0
            while((not self.btnStop.disabled) and  emergency_ok == True and interface_ok == True and client_ok != None):
                #Clock.schedule_once(partial( th_plc.refreshPlcData))  #self.plc.refreshPlcData()

                #th_plc.refreshPlcData()
                

                if(th_plc.MEMS[21] == True and self.state1 == 5):
                    self.state1 = 6 #Ready to inspect
                elif(th_plc.MEMS[21] == True and self.state2 == 5):
                    self.state2 = 6 #Ready to inspect
                
                if(self.state1 >= 6 or self.state2 >= 6):
                    tlocal = time.time()

                    #Board request
                    if((self.state1 == 6 or self.state1 < 3) and (self.state2 == 6 or self.state2 < 3) and th_plc.INPUTS[1] == True and th_plc.MEMS[4] == False ):
                        #th_plc.setMEM(22, False)#Board to inspect
                        th_plc.setMEM(22, False)#Board to inspect
                        th_plc.setMEM(5, False)#Inspection finished
                        th_plc.setMEM(6, False)#Board OK
                        th_plc.setMEM(7, False)#Board NG
                        th_plc.setMEM(4, True)#Request board
                        if(self.state1 == 6):
                            tstart1 = time.time()
                            self.state1 = 7#waitting board to inspect
                        if(self.state2 == 6):
                            tstart2 = time.time()
                            self.state2 = 7#waitting board to inspect
                    


                    #take picture
                    if( th_plc.MEMS[22] == True):
                        if((self.state1 == 7)):
                            tinspect1 = time.time()
                            if(config_object['CAMERA']['cam1_type'] == 'basler'):
                                self.source1 = self.take_picture(self.cam1)
                            else:
                                self.cam1.grab()
                                self.source1 = self.cam1.retrieve()[1]
                            self.state1 = 8
                            tgrab1 = time.time()

                            
                        if((self.state2 == 7)):
                            tinspect2 = time.time()
                            if(config_object['CAMERA']['cam2_type'] == 'basler'):
                                self.source2 = self.take_picture(self.cam2)
                            else:
                                self.cam2.grab()
                                self.source2 = self.cam2.retrieve()[1]
                                
                            tgrab2 = time.time()
                            self.state2 = 8
                            
                        
                    #elif(self.state1 == 7 and self.state2 == 7):
                    #    time.sleep(1)

                      

                    #execute inference model Yolov8    
                    if(self.state1 == 8):
                        tinf_start1 = time.time()
                        self.results, self.classes, tmodel, tinference, ttotal = self.visionLib.inference_ai_model(model1, self.source1.copy(), self.classes)
                        self.state1 = 9#inference
                        self.tinference1 = tinference
                        tinf_finish1 = time.time()

                    elif(self.state2 == 8):
                        tinf_start2 = time.time()
                        self.results, self.classes, tmodel, tinference, ttotal = self.visionLib.inference_ai_model(model2, self.source2.copy(), self.classes)
                        self.state2 = 9#inference
                        self.tinference2 = tinference
                        tinf_finish2 = time.time()

                    if(self.state1 == 9):
                        tcode_start1 = time.time()
                        #self.visionLib.decode(th_source) #look for codes on the image
                        self.state1 = 10 #traceability
                        tcode_finish1 = time.time()
                    elif(self.state2 == 9):
                        tcode_start2 = time.time()
                        #self.visionLib.decode(th_source)
                        self.state2 = 10 #traceability
                        tcode_finish2 = time.time()

                   
                    

                    #time.sleep(3)
                    if((self.state1 == 11 or self.state1 < 3) and (self.state2 == 11 or self.state2 < 3) and th_plc.MEMS[5] == False):     
                        

                        if(self.state1 == 11 or self.state1 < 3)and (self.state2 == 11 or self.state2 < 3):               

                            th_plc.MEMS[5] = True
                           
                            th_plc.setMEM(23, False)
                            time.sleep(.1)
                            th_plc.setMEM(6, True)
                            th_plc.setMEM(5, True)
                            time.sleep(.1)
                            
                            
                            
                            
                            

            
                
                    if((self.state1 == 11 or self.state1 < 3) and (self.state2 == 11 or self.state2 < 3) and th_plc.MEMS[23] == True):
                        if(self.state1 == 11 or self.state1 < 3) and (self.state2 == 11 or self.state2 < 3):
                            
                            if(self.state1 == 11 or self.state2 == 11):
                                tfinish = time.time()
                                th_plc.setMEM(23, False)
                                if(self.state1 == 11):
                                    self.state1 = 6 #waiting product/image
                                    ttotal = (tfinish-tinspect1)
                                    self.program1CycleTime.text = "{:.2f}".format(ttotal)
                                    self.product1total += 1
                                    self.product1OK += 1
                                if(self.state2 == 11):
                                    self.state2 = 6
                                    ttotal = (tfinish-tinspect2)
                                    self.program2CycleTime.text = "{:.2f}".format(ttotal)
                                    self.product2total += 1
                                    self.product2OK += 1
                                self.production_total += 1
                                time.sleep(.1)
                                th_plc.MEMS[23] = False

                   
                    
                        
                #else:
                #    time.sleep(1)
            try:
                if(self.state1 > 0):
                    if(config_object['CAMERA']['cam1_type'] != 'basler'):
                        self.cam1.release()
                    else:
                        self.cam1. camera_close()

                if(self.state2 > 0):
                    if(config_object['CAMERA']['cam2_type'] != 'basler'):
                        self.cam2.release()
                    else:
                        self.cam2.camera_close()
            
            except:
                pass
        

    
    


    def run_production_demo(self, *args):
        if(self.state1 == 2 or self.state2 == 2):
            
            
            side = threading.current_thread().name
            
            if(self.state1 == 2 and side == 'top'):
                self.state1 = 3 #load model
            if(self.state2 == 2 and side == 'bot'):
                self.state2 = 3
            
            if(side == 'top'):
                model1 = self.production_load_model(threading.current_thread().name)
            elif(side == 'bot'):
                model2 = self.production_load_model(threading.current_thread().name)

            self.results1 = []
            self.results2 = []
            while(not self.btnStop.disabled):
                
                
                if(side == 'top' and (self.state1 == 3 or self.state1 == 4)):
                    self.state1 = 4 #waiting product/image
                    tlocal = time.time()
                    #load image
                    self.source1 = self.production_load_image('file', side)
                elif(side == 'bot' and (self.state2 == 3 or self.state2 == 4)):
                    self.state2 = 4 #waiting product/image
                    tlocal = time.time()
                    #load image
                    self.source2 = self.production_load_image('file', side)

                
               
                if(side == 'top' and self.state1 == 4):
                    self.state1 = 5 #inference   
                elif(side == 'bot' and self.state2 == 4):
                    self.state2 = 5 #inference   

                #execute inference model Yolov8    
                if(side == 'top' and self.state1 == 5):
                    self.results1, self.classes, tmodel, tinference, ttotal = self.visionLib.inference_ai_model(model1, self.source1.copy(), self.classes)
                elif(side == 'bot' and self.state2 == 5):
                    self.results2, self.classes, tmodel, tinference, ttotal = self.visionLib.inference_ai_model(model2, self.source2.copy(), self.classes)
               
                if(side == 'top' and self.state1 == 5):
                    self.state1 = 6 #traceability
                elif(side == 'bot' and self.state2 == 5):
                    self.state2 = 6 #traceability

                #look for codes on the image
                #self.visionLib.decode(source)

                if(side == 'top' and self.state1 == 6):
                    self.state1 = 7 #show results
                elif(side == 'bot' and self.state2 == 6):
                    self.state2 = 7 #show results

                #check results
                if ((self.results1 != None or self.results2 != None))and(self.state1 == 7 or self.state2 == 7):
                    if(self.state1 == 7):
                        self.state1 = 10
                    if(self.state2 == 7):
                        self.state2 = 10
                    #self.production_showresults(tinference, source, side )  
                else:
                   # Clock.schedule_once( partial( toast("Inferëncia não encontrou candidatos!!! tempo >> "+str(time.time()-tlocal), background=(1,1,1,.7)) ))
                    pass
        

                #time.sleep(3)
                if((self.state1 == 11 or self.state2 == 11)):
                    if(side == 'top'):   
                        self.program1CycleTime.text = "{:.2f}".format(ttotal)
                        self.product1total += 1
                        self.state1 = 4 #waiting product/image
                    elif(side == 'bot'):
                        self.program2CycleTime.text = "{:.2f}".format(ttotal)
                        self.product2total += 1
                        self.state2 = 4 #waiting product/image
                        

                    time.sleep(10)



    def stop_production(self, *args):
        self.btnStop.disabled = True
        self.btnStart.disabled = False

        try:
            if(self.programInfo1 != None):
                self.state1 = 1 #Waiting to start
        except:
            self.state1 = 0

        try:
            if(self.programInfo2 != None):
                self.state2 = 1 #Waiting to start
        except:
            self.state2 = 0


class teachScreen(MDScreen):
    boxLayout = MDBoxLayout()
    visionLib = cvLibrary.vision()
    imagesource = ''
    dirSelectedImage = 0
    img = any
    jsonFile = ''
    progFile = ''
    componentsObjects = []
    modelsObjects = []
    annotationObjects = []
    programInfo = []
    imageScatter = any
    imageCard = any
    modelsComponents = None
    modelsAnnotations = None
    modelsModels = None
    modelsScroll = None
    modelsContent = None
    viewAnnotations = False
    component_node = []
    dialog = None
    _popup = None
    classes = []
    ori_x = 0
    ori_y = 0
    ori_a = 0
    product_results = None
    product_classes = None
    homography = None

    def on_pre_enter(self, *args):
        
        return super().on_pre_enter(*args)

    def on_enter(self, *args):
        self.img.width = self.imageCard.width
        self.img.height = self.imageCard.height
        
        return super().on_enter(*args)


    def img_scatter_actions(self, *args):
        #get touch
        for a in args:
            try:
                if(a.type_id == 'touch'):
                    touch = a
            except:
                pass

        if(touch):        
            if(not((touch.psx > 0.05 and touch.psx < 0.75)and(touch.psy<0.88))):
                self.imageScatter.collide_point(touch.pos[0],touch.pos[0])
                return

            # Override Scatter's `on_touch_down` behavior for mouse scroll
            if touch.is_mouse_scrolling:
                if touch.button == 'scrolldown':
                    if self.imageScatter.scale < 10:
                        mat = Matrix().scale(1.04, 1.04, 1.04)
                        self.imageScatter.apply_transform(mat, anchor=touch.pos)
                elif touch.button == 'scrollup':
                    if self.imageScatter.scale > 0.5:
                        mat = Matrix().scale(0.96, 0.96, 0.96)
                        self.imageScatter.apply_transform(mat, anchor=touch.pos)
            
                
            
                
            else:
                if touch.button == 'right':
                    mat = Matrix().scale(1.0, 1.0, 1.0)
                    self.imageScatter.transform = mat
                
                   
                        
                    


    def xon_touch_move(self, touch, *args):
       self.imageScatter.pos = (touch.x + args[0].dx, touch.y + args[0].dy)




    def __init__(self, **kwargs):
        super(teachScreen, self).__init__(**kwargs)
        self.boxLayout.orientation = "horizontal"
        self.boxLayout.md_bg_color = "silver"
        self.boxLayout.spacing = 10

        #Lef and right boxes
        leftBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.70)
        rightBox = MDBoxLayout(orientation = "vertical", spacing = 10, size_hint_x = 0.25)

       
        

      
        

        #actions top box
        actionsBox = MDBoxLayout(orientation = "horizontal", size_hint_y = 0.08, spacing = 10)#, pos_hint={'center_x':0.5, 'center_y':.67})
        
        #actions card and buttons
        cam_actionsCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=.31, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        cam_actionsBox = MDBoxLayout(orientation = "horizontal", spacing = 10, size_hint_x = 1)
        cam_actionsCard.add_widget(cam_actionsBox)

        btnPhoto = MDIconButton(icon = "camera", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.take_picture)
        lblPhoto = MDLabel(text='Capturar', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxPhoto =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxPhoto.add_widget(btnPhoto)
        boxPhoto.add_widget(lblPhoto)

        btnImageSave = MDIconButton(icon = "file-jpg-box", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.save_picture)
        lblImageSave = MDLabel(text='Salvar', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxImageSave =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxImageSave.add_widget(btnImageSave)
        boxImageSave.add_widget(lblImageSave)

        btnImagePrevious = MDIconButton(icon = "arrow-left-circle-outline", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.image_previous)
        lblImagePrevious = MDLabel(text='Anterior', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxImagePrevious =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxImagePrevious.add_widget(btnImagePrevious)
        boxImagePrevious.add_widget(lblImagePrevious)

        btnImageNext = MDIconButton(icon = "arrow-right-circle-outline", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.image_next)
        lblImageNext = MDLabel(text='Proximo', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxImageNext =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxImageNext.add_widget(btnImageNext)
        boxImageNext.add_widget(lblImageNext)

        #btnCamLive = MDIconButton(icon = "video-outline", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.cam_live)
        

        cam_actionsBox.add_widget(boxPhoto)
        cam_actionsBox.add_widget(boxImageSave)
        cam_actionsBox.add_widget(boxImagePrevious)
        cam_actionsBox.add_widget(boxImageNext)
        #cam_actionsBox.add_widget(btnCamLive)
        #

        actionsBox.add_widget(cam_actionsCard)

        

        #actions inspection card and buttons
        inspect_actionsCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=.31, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        inspect_actionsBox = MDBoxLayout(orientation = "horizontal", spacing = 5, size_hint_x = 1)
        inspect_actionsCard.add_widget(inspect_actionsBox)

        btnInspectProgram = MDIconButton(icon = "target-variant", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.65}, on_press = self.inspect_fid)
        lblInspect = MDLabel(text='Localizar', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxInspect =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxInspect.add_widget(btnInspectProgram)
        boxInspect.add_widget(lblInspect)

        btnInspectProduct = MDIconButton(icon = "file-question-outline", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.inspect_product)
        lblInspectProduct = MDLabel(text='Reconhecer', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxInspectProduct =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxInspectProduct.add_widget(btnInspectProduct)
        boxInspectProduct.add_widget(lblInspectProduct)

        #btnInspectModel = MDIconButton(icon = "human-male-board", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.save_picture)
        #btnRunGood = MDIconButton(icon = "human-male-board", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.image_previous)
        #btnRunBad = MDIconButton(icon = "human-male-board", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.image_next)
        
        btnExecuteModel = MDIconButton(icon='head-flash-outline', icon_size = "40sp",pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.inference_model)
        lblExecuteModel = MDLabel(text='Inferencia', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxExecuteModel =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxExecuteModel.add_widget(btnExecuteModel)
        boxExecuteModel.add_widget(lblExecuteModel)

        btnExecuteAll = MDIconButton(icon='flag-checkered', icon_size = "40sp",pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.check_program)  
        lblExecuteAll = MDLabel(text='Real & IA', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxExecuteAll =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxExecuteAll.add_widget(btnExecuteAll)
        boxExecuteAll.add_widget(lblExecuteAll)

        inspect_actionsBox.add_widget(boxInspect)
        
        inspect_actionsBox.add_widget(boxInspectProduct)

        #inspect_actionsBox.add_widget(btnInspectModel)
        inspect_actionsBox.add_widget(boxExecuteModel)
        inspect_actionsBox.add_widget(boxExecuteAll)

        actionsBox.add_widget(inspect_actionsCard)

        #actions card and buttons
        product_actionsCard = MDCard( padding = 15, size_hint_y = 1, size_hint_x=.31, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey")
        product_actionsBox = MDBoxLayout(orientation = "horizontal", spacing = 10, size_hint_x = 1)
        product_actionsCard.add_widget(product_actionsBox)
    
        btnProgramTarget = MDIconButton(icon = "aspect-ratio", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.train_fid)
        lblProgramTarget = MDLabel(text='Localizador', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxProgramTarget =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxProgramTarget.add_widget(btnProgramTarget)
        boxProgramTarget.add_widget(lblProgramTarget)

        btnImageModelSave = MDIconButton(icon = "star-shooting-outline", theme_icon_color="Custom", icon_size = "40sp", pos_hint={'center_x':0.5, 'center_y':.67}, on_press = self.append_image_product)
        lblImageModelSave = MDLabel(text='adicionar', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxImageModelSave =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxImageModelSave.add_widget(btnImageModelSave)
        boxImageModelSave.add_widget(lblImageModelSave)

        btnTrainProduct = MDIconButton(icon = "refresh-auto", theme_icon_color="Custom", icon_size = "40sp",pos_hint={'center_x':0.5, 'center_y':.67},  on_press = self.train_product)
        lblTrainProduct = MDLabel(text='train', size_hint=(1, .01), pos_hint={'center_x':.5, 'y': 0}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="Overline")
        boxTrainProduct =  MDFloatLayout(  size_hint_y = 1, size_hint_x = .18, pos_hint={'center_x':0.09, 'center_y':.5})
        boxTrainProduct.add_widget(btnTrainProduct)
        boxTrainProduct.add_widget(lblTrainProduct)

        product_actionsBox.add_widget(boxProgramTarget)
        product_actionsBox.add_widget(boxImageModelSave)
        product_actionsBox.add_widget(boxTrainProduct)


        actionsBox.add_widget(product_actionsCard)


        leftBox.add_widget(actionsBox) 
        
        #left box components
        imageBox = MDFloatLayout()
        self.imageCard = MDCard( padding = 5, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", pos_hint={'center_x':0.5, 'center_y':0.5})
        self.statusCard = MDCard( padding = 5, focus_behavior = False,  md_bg_color = "white", line_color=(1, 1, 1, 0.8), unfocus_color = "darkgrey", size_hint_y=.4, size_hint_x=.7, pos_hint={'center_x':0.5, 'center_y':0.3}, opacity=0)
        boxStatus = MDFloatLayout()
        
        lblstatusCard = MDLabel(text='Aguarde, executando solicitacao....', size_hint=(1, .01), pos_hint={'center_x':.5, 'center_y': .9}, halign = 'center', theme_text_color= "Custom", text_color = "blue",  font_style="H3")
        self.lblstatusInfo = MDLabel(text='....', size_hint=(1, .01), pos_hint={'center_x':.5, 'center_y': .3}, halign = 'center', theme_text_color= "Custom", text_color = "magenta",  font_style="H5")
        pgrStatusBar = MDProgressBar( type='indeterminate', pos_hint={'center_x':.5, 'center_y': .55}, size_hint=(.8, .2), color='yellowgreen')
        pgrStatusBar.start()
        
        boxStatus.add_widget(lblstatusCard)
        boxStatus.add_widget(pgrStatusBar)
        boxStatus.add_widget(self.lblstatusInfo)
        self.statusCard.add_widget(boxStatus)

        imageBox.add_widget(self.imageCard)
        imageBox.add_widget(self.statusCard)
        leftBox.add_widget(imageBox)

        self.img = Image(size_hint_y = 1, size_hint_x=1, allow_stretch = True, keep_ratio = False)
        self.img.source = 'not-found-image.jpg'

        self.imageScatter = Scatter( do_rotation=False, auto_bring_to_front=True, on_touch_down=self.img_scatter_actions, on_touch_move = self.xon_touch_move )
        self.imageScatter.add_widget(self.img)

        
        

        stencil = StencilView()
        stencil.add_widget(self.imageScatter)
        self.imageCard.add_widget(stencil)

         

        #Right box components
        panelCard = MDCard( size_hint_x=.99, size_hint_y = 0.99, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", radius= 15)
        rightBox.add_widget(panelCard)

        programBox = MDFloatLayout(size_hint_x = .96, size_hint_y = .94, pos_hint={'x':.02, 'y':.02})
        panelCard.add_widget(programBox)

        #label
        label = MDLabel(text='Programa', size_hint=(.5, .06), pos_hint={'x':.02, 'y':.98}, theme_text_color= "Custom", text_color = "blue",  font_style="Button")
        showAnnotation = MDCheckbox( pos_hint={'x':.85, 'y':.9})
        programBox.add_widget(label)
        programBox.add_widget(showAnnotation)

        #Program actions
        programActions = MDBoxLayout(orientation= 'horizontal', spacing = 1, size_hint_x = 1, size_hint_y = .12, pos_hint={'x':0, 'y':.93})
        programBox.add_widget(programActions)

        btnOpenProgram = MDIconButton(icon = "folder-open", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.open_program, valign='top')
        btnNewProgram = MDIconButton(icon = "file-plus", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.new_program)
        btnSaveProgram = MDIconButton(icon = "content-save-check", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.save_program)
        btnDeleteProgram = MDIconButton(icon = "delete-restore", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.delete_program)
        btnUpload = MDIconButton(icon = "cloud-upload", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.upload_program)
        btnDownload = MDIconButton(icon = "brain", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.doTrainModel)
        btnCompare = MDIconButton(icon = "head-snowflake-outline", theme_icon_color="Custom", icon_size = "32sp",  on_press = self.export_annotation)
        
        
        programActions.add_widget(btnOpenProgram)
        programActions.add_widget(btnNewProgram)
        programActions.add_widget(btnSaveProgram)
        programActions.add_widget(btnDeleteProgram)
        programActions.add_widget(btnUpload)
        programActions.add_widget(btnDownload)
        programActions.add_widget(btnCompare)
        
        
        #Program info
        self.txtProgramName = MDTextField(hint_text= "Nome do program", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .06, pos_hint={'x':0.02, 'y':.87}, font_size= "12dp")
        self.txtAnnotationFile = MDTextField(hint_text= "Modelo IA", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .06, pos_hint={'x':0.02, 'y':.8}, font_size= "12dp")
        self.txtPathTrain = MDTextField(hint_text= "Pasta treinamento", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .06, pos_hint={'x':0.02, 'y':.73}, font_size= "12dp")
        self.txtPathValid = MDTextField(hint_text= "Pasta validacao", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .06, pos_hint={'x':0.02, 'y':.66}, font_size= "12dp")
        self.txtPathLib = MDTextField(hint_text= "Ferramentas Vision", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .06, pos_hint={'x':0.02, 'y':.59}, font_size= "12dp")
        
        programBox.add_widget(self.txtProgramName)
        programBox.add_widget(self.txtAnnotationFile)
        programBox.add_widget(self.txtPathTrain)
        programBox.add_widget(self.txtPathValid)
        programBox.add_widget(self.txtPathLib)   

        modelsCard = MDCard( shadow_softness = 12, shadow_offset = (0,2), line_color=(0.2, 0.2, 0.2, 0.8), size_hint_x=.95, size_hint_y = 0.58, focus_behavior = False, focus_color = "grey", unfocus_color = "darkgrey", radius= 15, style= 'outlined', pos_hint={'x':0.02, 'y':0})
        modelsBox = MDFloatLayout( size_hint_x = 1, size_hint_y = 1)
        modelsCard.add_widget(modelsBox)

        modelsMenu = MDBoxLayout(orientation= 'horizontal', spacing = 3, size_hint_x = 1, size_hint_y = 0.1,  pos_hint={'x':0.01, 'y':.9})
        btnNewModelCV = MDIconButton(icon='eye-refresh', on_press=self.image_reload)
        btnEditModelCV = MDIconButton(icon='vector-square-edit', on_press=self.editAction)
        btnRemoveModelCV = MDIconButton(icon='vector-square-remove', on_press=self.removeAction)
        btnImportAnnotations = MDIconButton(icon='swap-vertical', on_press=self.importAction)
        btnNewModelAI = MDIconButton(icon='vector-square-plus', on_press= self.model_ComponentDefine)
        
        btnExecuteModelAI = MDIconButton(icon='flash-red-eye', on_press = self.check_program)
        
        btnExecuteFeature =  MDIconButton(icon='image-check-outline', on_press = self.sift_accept)

        #btnRightMenu = MDIconButton(icon='dots-vertical', halign='right')

        modelsMenu.add_widget(btnNewModelCV)
        modelsMenu.add_widget(btnNewModelAI)
        modelsMenu.add_widget(btnEditModelCV)
        modelsMenu.add_widget(btnRemoveModelCV)
        #modelsMenu.add_widget(btnImportAnnotations)
        
        #modelsMenu.add_widget(btnExecuteModelAI)
        

        modelsBox.add_widget(modelsMenu)

        self.modelsContent = MDBoxLayout(orientation= 'horizontal', spacing = 3, size_hint_x = .9, size_hint_y = 0.8,  pos_hint={'x':0.05, 'y':0.1})
        self.modelsComponents = MDBoxLayout(id='components', size_hint_y = 1)
        self.modelsScroll = MDScrollView(self.modelsComponents)


        self.modelsModels = MDSelectionList(on_touch_up=self.model_selected, selected_mode=True, id='models', size_hint_y = 0.8)
        self.modelsAnnotations = MDSelectionList(on_touch_up=self.component_selected, selected_mode=True, id='annotations', size_hint_y = 0.8)
        self.modelsResults = MDSelectionList(on_touch_up=self.results_selected, selected_mode=True, id='results', height=self.modelsScroll.height)
        self.modelsResultsMatches = MDSelectionList(on_touch_up=self.results_selected, selected_mode=True, id='matches', height=self.modelsScroll.height)

        
        self.modelsContent.add_widget(self.modelsScroll)


        modelsFooter = MDFloatLayout( size_hint_x = 1, size_hint_y = 0.1,  pos_hint={'x':0.0, 'y':.0}, md_bg_color='gray', radius = 10)
        self.btnViewComponents = MDIconButton(icon='focus-field', size_hint_x=.3, pos_hint={'x':0.05, 'y':.0}, on_press = self.show_components)
        self.btnViewResults = MDIconButton(icon='magnify-expand', size_hint_x=.3, pos_hint={'x':0.3, 'y':.0}, on_press = self.show_results)
        self.btnViewMatches = MDIconButton(icon='format-list-checks', size_hint_x=.3, pos_hint={'x':0.55, 'y':.0}, on_press = self.show_results_match)
        self.btnViewModels = MDIconButton(icon='circle-opacity', size_hint_x=.3, pos_hint={'x':0.8, 'y':.0}, on_press = self.show_models)
        modelsFooter.add_widget(self.btnViewComponents)
        modelsFooter.add_widget(self.btnViewResults)
        modelsFooter.add_widget(self.btnViewMatches)
        modelsFooter.add_widget(self.btnViewModels)

        modelsBox.add_widget(self.modelsContent)
        modelsBox.add_widget(modelsFooter)



        programBox.add_widget(modelsCard)

        self.boxLayout.add_widget(leftBox)
        self.boxLayout.add_widget(rightBox)
        
        self.add_widget(self.boxLayout)

    #Train actions
    ###########################################################################################################################

    def append_image_product(self, *args):
        
        try:
        
            if len(self.visionLib.image)>0 and len(self.programInfo)>0:
                path = config_object['PROGRAMMODEL']['path']+'train\\'
                image_file = (self.programInfo['name']+'_'+time.asctime(time.localtime(time.time()))).replace(" ","_").replace(":","_")

                #image
                if self.visionLib.write_image(self.visionLib.image, path+'images\\'+image_file+'.jpg'):
                    #Label
                    with open(path+'labels\\'+image_file+'.txt','w') as f:
                        f.write('0 0.5 0.5 1.0 1.0')
        except:
            pass



    def train_product(self, *args):
        if self.programInfo:
            self.visionLib.train_product_model(config_object['PROGRAMMODEL']['path']+config_object['PROGRAMMODEL']['model_name'], int(config_object['PROGRAMMODEL']['train_epochs']), int(config_object['PROGRAMMODEL']['train_imgsz']), config_object['PROGRAMMODEL']['yaml_file'])
        

          
        
    #Program actions
    ##########################################################################################################################################

    #open program file
    file_path = StringProperty("No file chosen")
    the_popup = ObjectProperty(None)
    def open_program(self, *args):     
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Abrir programa", content=content,
                            size_hint=(0.7, 0.5))
        self._popup.open()

    def load(self, path, filename):
        try:
            self.progFile = filename[0]
            self.programInfo = None
            with open(self.progFile, 'r') as prog_file:
                self.programInfo = json.load(prog_file)


            #refresh program info
            self.txtProgramName.text = self.programInfo['name']
            self.txtAnnotationFile.text = self.programInfo['annotation_file']
            self.jsonFile = self.programInfo['annotation_file']
            self.txtPathTrain.text = self.programInfo['train_path']
            self.txtPathValid.text = self.programInfo['validation_path']
            self.txtPathLib.text = self.programInfo['lib_path']


            self.programInfo['board']['offset_x'] = self.ori_x
            self.programInfo['board']['offset_y'] = self.ori_y
            self.programInfo['board']['offset_a'] = self.ori_a
  
            #refresh annotations from file
            self.loadClassesFile(self.programInfo['annotation_file'])

            #refresh models
            self.loadModels(self.programInfo['models'])


            #refresh annotations
            #self.loadAnnotations(self.annotationObjects['annotation']['object'])
            


           
            #refresh components
            self.loadComponents(self.programInfo['board']['components'])


            if(self._popup):
                self._popup.dismiss()
            else:
                self.dialog.dismiss()
        
        except Exception as ex:
            self.programInfo = []
            self.jsonFile = ''
            self.progFile = ''
            if(self._popup):
                self._popup.dismiss()
            else:
                self.dialog.dismiss()
            toast("Falha ao tentar abrir o arquivo...", background=(1,0,0,.7))

    def loadClassesFile(self, file):
        try:
            dir = os.path.dirname(file)

            yaml_file = dir+'\data.yaml'

            with open(yaml_file) as stream:
                d = yaml.safe_load(stream)
                self.classes = d['names']

        except:
            self.classes = []
    
    def loadAnnotationFile(self, file):
        if(file != ''):
            self.load_pascal_voc() # self.load_json()

    def loadModels(self, models):
        self.modelsModels.clear_widgets()
        lis_id = 0
        for sm in models:
            image = IconLeftWidget(icon='focus-field-horizontal', font_size='10dp')
            items = TwoLineIconListItem(text='[size=12]'+sm['name']+'[/size]', secondary_text='[size=12]'+sm['family']+'[/size]', id=str(lis_id))
            items.add_widget(image)
                
            lis_id += 1
            self.modelsModels.add_widget(items)


    def loadAnnotations(self, objects):
        self.modelsAnnotations.clear_widgets()
        lis_id = 0
        data_annotations=[]
        for sm in objects:
            data_annotations.append({'active_icon':'images/annotation.png', 'left_icon':'images/xml.png', 'text':sm['pose'], 'right_icon':'', 'status_icon':''  })
                

        rv_annotations = myrecycleview.RV(data_annotations) 
        rv_annotations.name = 'annotations'   
        self.modelsAnnotations.add_widget( rv_annotations)


    def loadComponents(self, components):
        self.modelsComponents.clear_widgets()
        lis_id = 0                       
        data = []
        for sm in components:
            #active icon
            if sm['inspect'] == True:
                inspect_icon = 'images/enabled.png'
            else:
                inspect_icon = 'images/disabled.png'


            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #polarity
            if sm['polarity'] != '':
                pol_icon = 'images/polarity.png'
            else:
                pol_icon = ''

            try:
                data.append({'active_icon':inspect_icon, 'left_icon': pol_icon, 'text':sm['pose'], 'right_icon':type_icon, 'status_icon':'' })
            except:
                toast(sm, background=(1,1,0,.7))    

        self.rv = myrecycleview.RV(data) 
        self.rv.height = self.modelsContent.height
        self.rv.name = 'components'   
        self.modelsComponents.add_widget( self.rv)


    def loadResults(self, results, classes):
        self.modelsResults.clear_widgets()
        lis_id = 0                       
        data = []
        for r in results:
            boxes = r.boxes
            self.iaResults = r.boxes
            for sm in boxes:
                #active icon
                if sm.conf[0] > 0.1:
                    inspect_icon = 'images/green.png'
                else:
                    inspect_icon = 'images/disabled.png'


                #type icon
                type_icon = 'images/result_ai.png'#'head-lightbulb'
            
                #polarity
                pol_icon = 'images/checkmark.png'#'crosshairs-question'
            
                try:
                    data.append({'active_icon':inspect_icon, 'left_icon': pol_icon, 'text':classes[int(sm.cls[0])], 'right_icon':type_icon, 'status_icon':'' })
                except:
                    toast("Falha carregando resultados...", background=(1,1,0,.7))    

        self.rv = myrecycleview.RV(data) 
    
        self.rv.height = self.modelsContent.height
        self.rv.name = 'results'   
        self.modelsResults.add_widget( self.rv)



    def loadMatches(self, results, components, classes):
        self.modelsResultsMatches.clear_widgets()
        lis_id = 0                       
        data = []
        for sm in self.positives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #result            
            result_icon = 'images/checkmark.png'
            f = float(sm['conf'])
            text = sm['pose']+' << '+f'{f:.2f}'+' >> '
            try:
                data.append({'active_icon':type_icon, 'left_icon': '', 'text':text, 'right_icon':result_icon, 'status_icon':'' })
            except:
                toast(sm, background=(1,1,0,.7))    



        for sm in self.falsepositives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #result            
            result_icon = 'images/error.png'
            f = float(sm['conf'])
            text = sm['pose']+' << '+f'{f:.2f}'+' >> '
            try:
                data.append({'active_icon':type_icon, 'left_icon': '', 'text':text, 'right_icon':result_icon, 'status_icon':'' })
            except:
                toast(sm, background=(1,1,0,.7))    



        for sm in self.negatives:
            
            #type icon
            if sm['type'] == 'FID':
                type_icon = 'images/fid.png'
            elif sm['type'] == 'COMP':
                type_icon = 'images/electronics.png'
            else:
                type_icon = ''

            #result            
            result_icon = 'images/delete-sign--v3.png'
            
            try:
                data.append({'active_icon':type_icon, 'left_icon': '', 'text':sm['pose'], 'right_icon':result_icon, 'status_icon':'' })
            except:
                toast(sm, background=(1,1,0,.7))    



        self.rv = myrecycleview.RV(data) 
        self.rv.height = self.modelsContent.height
        self.rv.name = 'matches'   
        self.modelsResultsMatches.add_widget( self.rv)






    def treenodeEdit(self, node):

        print("Selecionado!!!")

    def editAction(self, *args):
        if(self.modelsContent.children[0].children[0] == self.modelsComponents):
            nodes = self.modelsContent.children[0].children[0].children[0].children[0].selected_nodes
            if(len(nodes) == 1):
                self.component_selected(nodes)
            else:
                toast("Não é possivél editar varios componentes...favor selecionar apenas um e tentar novamente.", background=(1,0,0,.7))        
        elif(self.modelsContent.children[0].children[0] == self.modelsResults):
            
            if(self.modelsResults.children[0].children[1].selected_item != None):
                node = self.modelsResults.children[0].children[1].selected_item
                self.results_selected(self.results[0].boxes[node])
            else:
                toast("Não é possivél editar varios componentes...favor selecionar apenas um e tentar novamente.", background=(1,0,0,.7))    
        else:
            print("Componente não selecionado!!!")


    def removeAction(self, *args):
        if(self.modelsContent.children[0].children[0] == self.modelsComponents):
            nodes = self.modelsContent.children[0].children[0].children[0].children[0].selected_nodes
            if(len(nodes) == 1):
                self.programInfo['board']['components'].remove(self.programInfo['board']['components'][nodes[0]])
                self.loadComponents(self.programInfo['board']['components'])
            else:
                toast("Não é possivél remover varios componentes...favor selecionar apenas um e tentar novamente.", background=(1,0,0,.7))        
        elif(self.modelsContent.children[0].children[0] == self.modelsResults):
            
            if(self.modelsResults.children[0].children[1].selected_item != None):
               pass
            else:
                toast("Não é possivél editar varios componentes...favor selecionar apenas um e tentar novamente.", background=(1,0,0,.7))    
        else:
            print("Componente não selecionado!!!")

    def train_fid(self, *args):
        if len(self.programInfo)>0 and len(self.visionLib.image)>0:
            pName = self.programInfo['name']
            pClasses = config_object['PROGRAMMODEL']['classes'].replace('\'','').replace(" ",'').replace('[','').replace(']','').split(',')
            pModel = config_object['PROGRAMMODEL']['product_model'].replace('\'','').replace(" ",'').replace('[','').replace(']','').split(',')

            f = pClasses.index(pName)
            if f > -1:
                dlg = self.confirmation_dialog('Programa ja possui modelo, deseja substituir?','Modelo produto')
            else: 
                self.fid_train(f)
    

    def fid_train(self, product):
        #get roi
        roi = self.visionLib.roiSelectModelProduct(self.visionLib.image, True, False, 'Produto')

        #verify roi
        if roi:
            #get roi values

            #cut image
            im = self.visionLib.cut_product(self.visionLib.image, roi[0], roi[1], roi[2], roi[3])

            #file name
            imgFile = 'program\\' + self.programInfo['name'] + '.bmp'
            prgFile = 'program\\' + self.programInfo['name'] + '.json'

            #save image into file
            self.visionLib.write_image(im, imgFile)

            #refresh config file data
            if product == -1:
                pClasses = config_object['PROGRAMMODEL']['classes'].replace('\'','').replace(" ",'').replace('[','').replace(']','').split(',')
                pModel = config_object['PROGRAMMODEL']['product_model'].replace('\'','').replace(" ",'').replace('[','').replace(']','').split(',')
                pProgram = config_object['PROGRAMMODEL']['program_files'].replace('\'','').replace(" ",'').replace('[','').replace(']','').split(',')
                pClasses.append(self.programInfo['name'])
                pModel.append(imgFile)
                pProgram.append(prgFile)
                config_object['PROGRAMMODEL']['classes'] = self.list2str(pClasses) 
                config_object['PROGRAMMODEL']['product_model'] = self.list2str(pModel)
                config_object['PROGRAMMODEL']['program_files'] = self.list2str(pProgram)


                #save config file data
                self.config_save()
                pass

    def list2str(self, list):
        str = "[ "
        c = 0
        for l in list:
            if c !=0:
                str += ","
            str += "'"+l+"'"
            c+=1
        str += " ]"
        return str

    def config_save(self, *args):
        try:
            
            with open('config.ini', 'w') as conf:
                config_object.write(conf)     
        except:
            pass

    def inference_model(self, *args):
        self.statusCard.opacity = 100
        self.statusCard.disabled = False
        self.lblstatusInfo.text = "Detectando componentes do produto utilizando IA... "
        tInference = threading.Thread( target=self.inference_model_exe)
        tInference.start()

    def finish_inference(self, *args):
        self.hide_status()

        if not self.results == None:
            toast("Inferencia realizada com sucesso!!! tempo >> "+str(self.tinference), background=(0,0,1,.7))
            self.loadResults(self.results, self.classes)



            self.visionLib.draw_inference_results(self.source, self.results, self.classes)
            self.img.texture = self.visionLib.opencv2kivyImage(self.source)
        
            #self.image_refresh()
        else:
            toast("Inferëncia não encontrou candidatos!!! tempo >> "+"{:.2f}".format(time.time()-self.tlocal), background=(1,1,1,.7))

        

        time.sleep(3)
        toast("Tempo total do processo >>> "+"{:.2f}".format(self.ttotal), background=(0,1,1,.7))

       

    def inference_model_exe(self, *args):
        tlocal = time.time()
        self.source = self.visionLib.image.copy() #"Yolo-Weights/Image__2022-09-23__19-59-27_bmp.rf.1972034f92c941deca807a2f86f179aa.jpg"
        model = self.programInfo['annotation_file'] #"best (1).pt"#"Yolo-Weights/datasets/digAOIv8-010523-full.pt"

        #execute inference model Yolov8
        self.results, self.classes, tmodel, self.tinference, self.ttotal = self.visionLib.inference_ai_model(model, self.source, self.classes)
        
        #look for codes on the image
        #self.visionLib.decode(source)

        Clock.schedule_once(self.finish_inference, 0)
        
        
    


    def dismiss_dialog(self, *args):
        self.dialog.dismiss()
        toast("Ação cancelada pelo usuário...", background=(0,1,1,.7))

    def dismiss_popup(self, *args):
        self._popup.dismiss()
        toast("Ação cancelada pelo usuário...", background=(0,1,1,.7))


    def confirmation_dialog(self, question, info, *args):
        self.dialog = MDDialog(
        title=question,
        text=info,
        buttons=[
            MDFlatButton(
                text="CANCEL",
                theme_text_color="Custom",
                #text_color= 'white',
                on_press=self.confirm_dismiss,
            ),
            MDFlatButton(
                text="OK",
                theme_text_color="Custom",
                on_press=self.confirm_accept,
                #text_color=self.theme_cls.primary_color,
            ),
        ],
        )

        self.dialog.open()
        #return dialog

    def confirm_accept(self, info):
        self.fid_train(0)
        self.dialog.dismiss()

    def confirm_dismiss(self, *args):
        self.dialog.dismiss()

    def input_dialog(self, _title, field, *args):
        
        self.dlgInput = MDDialog(
            title=_title,
                type="custom",
                
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        theme_text_color="Custom",
                        on_press=self.input_dismiss,
                        #text_color=.primary_color,
                    ),
                    MDFlatButton(
                        text="OK",
                        theme_text_color="Custom",
                        on_press=self.input_accept,
                        #text_color=self.theme_cls.primary_color,
                    ),
                ],
            )
        txtField = MDTextField(hint_text=field, padding=20)
        content_cls=MDBoxLayout( orientation="vertical", spacing="12dp", size_hint_y=None, height="120dp")
        self.dlgInput.add_widget(content_cls)
        self.dlgInput.add_widget(txtField)
        
        self.dlgInput.open()

    def input_dismiss(self, *args):
        self.dlgInput.dismiss()


    


    def input_accept(self, *args):
        try:
            text = self.dlgInput.children[0].text.upper();
            if self.drawingImage.any():
                img = self.drawingImage
            else:
                if(self.visionLib.image.any()):
                    img = self.visionLib.image
                
                    
            rois =   self.visionLib.roiSelectModelCV( img, True, True, 'Novo Componente')  

            if(len(rois) > 0):
                for roi in rois:
                    x = roi[0]#-(roi[2]/4)
                    y =   roi[1]#-(roi[3]/4)
                    try:
                        
                        pts = np.float32([ [int(0),int(0)] ]).reshape(-1,1,2) 
                        pts = self.visionLib.pts_homography(pts,self.homography)
                        pts2 = np.float32([ [int(x),int(y)] ]).reshape(-1,1,2) 
                        pts2 = self.visionLib.pts_homography(pts2,self.homography)
                        x1 = pts[0][0][0]#+(float(roi[2])/2)
                        y1 = pts[0][0][1]#+(float(roi[3])/2)
                        x = x - x1.real#x:945y:809
                        y = y - y1.real#x:3280y:2108
                    except:
                        pass
                    new_comp = {'inspect': True, 'pose': text, 'model': 'None', 'type': 'None', 'polarity': 'None', 'x': x, 'y': y, 'a': 0.0, 'box_x': roi[2], 'box_y': roi[3]}
                    self.programInfo['board']['components'].append(new_comp)
                    self.loadComponents(self.programInfo['board']['components'])
             

        except:
            toast("Falha ao tentar abrir imagem!", background=(1,0,0,.7))   
        
        self.dlgInput.dismiss()



    def sift_accept(self, *args):
        try:
            
            
            img = self.visionLib.image.copy()
                
            self.pcb_pts, self.homography =  self.visionLib.Locate_Object(img, self.product_model)

            self.visionLib.draw_crosshair(img, int(0), int(0), self.homography)
            self.visionLib.draw_aligned_product(img, self.product_results, self.product_classes, self.homography)
        

            self.image_refresh(img)
            
           

        except:
            toast("Falha ao tentar encontrar refer^encia na imagem!", background=(1,0,0,.7))   
        
       



    ########################################################################################################################################
    # Import annotations
    def importAction(self, *args):
        self.dialog = MDDialog(
                        text="Comfirmar importar anotações para lista de componentes?",
                        buttons=[MDFlatButton(text="CANCEL", on_press=self.dismiss_dialog), MDFlatButton(text="Confirmar", on_press=self.doAnnotationImport),],
                    )
        
        self.dialog.open()

    def doAnnotationImport(self, *args):
        try:
            if(self.programInfo['annotation_file'] != ''):
                for a in self.annotationObjects['annotation']['object']:
                    x = (int(a['bndbox']['xmin'])+int(a['bndbox']['xmax']))/2
                    y = (int(a['bndbox']['ymin'])+int(a['bndbox']['ymax']))/2
                    t = 0
                    bbox_x = int(a['bndbox']['xmax'])-int(a['bndbox']['xmin'])
                    bbox_y = int(a['bndbox']['ymax'])-int(a['bndbox']['ymin'])
                    comp = {'pose':a['pose'], 'model':a['name'], 'x':x, 'y':y, 'a':t, 'box_x':bbox_x, 'box_y':bbox_y, 'inspect': True, 'type':'COMP', 'polarity': ''}
                    self.programInfo['board']['components'].append(comp)

                self.loadComponents(self.programInfo['board']['components'])
            else:
                toast("Não encontramos o arquivo de anotações!", background=(1,0,0,.7))        
        except:
            toast("Falha ao tentar realizar importação!", background=(1,0,0,.7))        
        self.dialog.dismiss()




    ########################################################################################################################################

    def parse_models(self):
        try:
            pass

        except:
            toast("Falha ao tentar coletar modelos do programa...")

    #save changes
    def save_program(self, *args):
                  
        self.dialog = MDDialog(
            text="Confirmar salvar alterações no programa?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_press=self.info_cancel
                        
                ),
                MDFlatButton(
                    text="Confirmar",
                    on_press=self.info_2json
                        
                ),
            ],
        )
        
        self.dialog.open()
        
    def info_2json(self, *args):
        try:
            #sync values screen x object
            self.programInfo['name'] = self.txtProgramName.text    
            self.programInfo['annotation_file'] = self.txtAnnotationFile.text    
            self.programInfo['train_path'] = self.txtPathTrain.text    
            self.programInfo['validation_path'] = self.txtPathValid.text    
            self.programInfo['lib_path'] = self.txtPathLib.text
                
            with open(self.progFile, 'w') as json_file:
                json_file.write(json.dumps(self.programInfo))

            toast("Programa salvo com sucesso...", background=(0,1,0,.7))
        except Exception as e:
            toast("Falha ao tentar salvar alterações...", background=(1,0,0,.7))
            
        self.dialog.dismiss()
    
    def info_cancel(self, *args):
        self.dialog.dismiss()


    #save changes
    def train_annotations(self, *args):
                  
        self.dialog = MDDialog(
            text="Confirmar treinar modelo com anotacaoes?",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_press=self.info_cancel
                        
                ),
                MDFlatButton(
                    text="Confirmar",
                    on_press=self.doTrainModel
                        
                ),
            ],
        )
        
        self.dialog.open()

    def doTrainModel(self, *args):
        if not self.programInfo:
            toast("Falha ao tentar treinar anotacoes...", background=(1,0,0,.7))
            return False
        

        stime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        file_model = self.programInfo['annotation_file']
        dir_train = os.path.split( self.programInfo['train_path'] )
        dir_val = os.path.split( self.programInfo['validation_path'] )
        dir_test = os.path.split( self.programInfo['test_path'] )
        database_path = self.programInfo['lib_path']


        try:
            if os.path.isfile(file_model):
                if os.path.exists(database_path) and os.path.isfile(database_path+'\\classes.txt'):
                    #load images path train/val
                    _list = os.scandir(database_path)
                    dir_list = []
                    for obj in _list:
                        if obj.is_dir():
                            dir_list.append(obj.name)

                    
                    
                

                    #load classes
                    classes = open(database_path+'\\classes.txt', 'r').read().splitlines()

                    #create YAML
                    yaml_file, yaml_ext = os.path.splitext( os.path.split(file_model)[1] )
                    yaml_file = database_path+'\\'+yaml_file+'_'+stime+'.yaml'

                    with open(yaml_file, 'w') as f:
                        #path
                        f.write('path: '+database_path+'\n')
                        #train
                        f.write('train: \n')
                        for t in dir_list:
                            f.write(' - '+t+'\images \n')
                       
                        #val
                        f.write('val: '+dir_val[1]+'\images \n')
                        #test
                        #f.write('test: '+dir_test[1]+'\images \n\n\n')
                        #classes
                        f.write('nc: '+str(len(classes))+'\n')
                        f.write('names: [ ')
                        for c in classes:
                            f.write("'"+c+"',")
                        f.write(' ]') 
                    

                    #run re-train
                    result, t1, t2, t3 = self.visionLib.train_models(file_model, yaml_file, config_object['PROGRAMMODEL']['train_epochs'], config_object['PROGRAMMODEL']['train_imgsz'])
                    if result == None:
                        toast("Falha ao tentar treinar modelo...", background=(1,0,0,.7))
        except:
            pass
         

    def new_program(self, *args):
        content = SaveDialog(save=self.save_press, cancel=self.exitSave)
        self._popup = Popup(title="Novo programa", content=content,
                            size_hint=(0.7, 0.5))
        self._popup.open()


    def save_press(self, *args):
        try:
            self.progFile = args[1]+".json"
            #sync values screen x object
            self.programInfo['name'] = self.txtProgramName.text    
            self.programInfo['annotation_file'] = self.txtAnnotationFile.text    
            self.programInfo['train_path'] = self.txtPathTrain.text    
            self.programInfo['validation_path'] = self.txtPathValid.text    
            self.programInfo['lib_path'] = self.txtPathLib.text



            with open(args[1], 'w') as save_file:
                save_file.write(json.dumps(self.programInfo))

        except:
            toast("Falha ao tentar criar novo programa...", background=(1,0,0,.7))

        self._popup.dismiss()
        

    def exitSave(self, *args):
        self._popup.dismiss()
        pass

    def delete_program(self, *args):
        pass


    def upload_program(self, *args):
        pass


    def download_program(self, *args):
        pass


    def compare_program(self, *args):
        pass

    ##########################################################################################################################################
        

    ##########################################################################################################################################
    #Models Actions
    ##########################################################################################################################################

    def inspect_fid(self, *args):
        self.statusCard.opacity = 100
        self.statusCard.disabled = False
        self.lblstatusInfo.text = "Detectando posicionamento do produto na imagem... "
        
        self.sift_accept()
        self.hide_status()


    def hide_status(self, *args):
        self.statusCard.opacity = 0
        self.statusCard.disabled = True


    def inspect_product(self, *args):
        self.statusCard.opacity = 100
        self.statusCard.disabled = False
        self.lblstatusInfo.text = "Detectando modelo do produto utilizando IA... "
        tInspect = threading.Thread( target=self.inspect_product_exe)
        tInspect.start()
        

    def finish_inspection(self, *args):
        self.hide_status()

        if self.program_IA != self.progFile:
            self.dialog = MDDialog(
                text="Deseja abrir programa compativel com produto identificado?",
                buttons=[MDFlatButton(text="CANCEL", on_press=self.dismiss_dialog), MDFlatButton(text="Confirmar", on_press=self.doOpenProductIA),],
            )
        
            self.dialog.open()
    
    def threaded_toast(self, *args):
        toast( self.thToast_msg, self.thToast_color)


    def inspect_product_exe(self, *args):
        try:
            if len(self.visionLib.image) > 0:


                model = config_object['PROGRAMMODEL']['path']+config_object['PROGRAMMODEL']['model_name']
                results, tstart, tinference, ttotal =  self.visionLib.inference_product(model, self.visionLib.image)
                
                rboxes = results[0].boxes.boxes.tolist()
                if len(rboxes) > 0:
                    
                    
                    classes = (config_object['PROGRAMMODEL']['classes']).translate({ord(i): None for i in '[],'''}).replace("'", "").split()
                    drawingImage = self.visionLib.image.copy()
                    #self.visionLib.draw_inference_results_best(drawingImage, results, classes, None)
                    self.product_results = results
                    self.product_classes = classes
                    
                    x, y, w, h = results[0].boxes.xywh[0]
                    self.ori_x = int(x)+(int(w)/2)
                    self.ori_y = int(y)+(int(h)/2)
                    self.ori_a = 0
                    #self.visionLib.draw_crosshair(drawingImage, int(self.ori_x), int(self.ori_y), self.homography)
                    #self.image_refresh(drawingImage)
                    
                    #if not self.dialog:
                    self._popup = None
                    program_files = (config_object['PROGRAMMODEL']['program_files']).translate({ord(i): None for i in '[],'''}).replace("'", "").split()
                    program_models = (config_object['PROGRAMMODEL']['product_model']).translate({ord(i): None for i in '[ ]'''}).replace("'", "").split(",")
                    self.program_IA = program_files[int(rboxes[0][5])]
                    self.product_model = program_models[int(rboxes[0][5])]

                    

                    Clock.schedule_once( self.finish_inspection, 0 )
                else:
                    self.thToast_msg = "Falha ao tentar detectar programa compativel..."
                    self.thToast_color = background=(1,0,0,.7)
                    Clock.schedule_once( self.hide_status, 0 )
                    Clock.schedule_once( self.threaded_toast, 0 )

                    
                
                    
                       

        except Exception as e:
            self.thToast_msg = "Falha ao tentar detectar programa compativel..."
            self.thToast_color = background=(1,0,0,.7)
            Clock.schedule_once( self.hide_status, 0 )
            Clock.schedule_once( self.threaded_toast, 0 )

    
    def doOpenProductIA(self, *args):
        
        self.load("", [self.program_IA])
        self.dialog = None

    def image_reload(self, *args):
        self.image_refresh(None)

    def show_components(self, *args):
        self.modelsContent.clear_widgets()
        self.modelsScroll.clear_widgets()
        self.modelsScroll = MDScrollView(self.modelsComponents)
        self.modelsContent.add_widget(self.modelsScroll)
        self.activeView = 'components'
        self.btnViewComponents.icon_color = (1,1,1,1)

    def show_results(self, *args):
        self.modelsContent.clear_widgets()
        self.modelsScroll.clear_widgets()

        self.modelsScroll = MDScrollView(self.modelsResults)
        self.modelsResults.unselected_all()
        self.modelsContent.add_widget(self.modelsScroll)
        self.activeView = 'results'
        self.btnViewResults.icon_color = (1,1,1,1)
        

    def show_results_match(self, *args):
        self.modelsContent.clear_widgets()
        self.modelsScroll.clear_widgets()

        self.modelsScroll = MDScrollView(self.modelsResultsMatches)
        self.modelsResults.unselected_all()
        self.modelsContent.add_widget(self.modelsScroll)
        self.activeView = 'matches'
        self.btnViewResults.icon_color = (1,1,1,1)
        



    def show_models(self, *args):
        self.modelsContent.clear_widgets()
        self.modelsScroll.clear_widgets()
        self.modelsScroll = MDScrollView(self.modelsModels)
        self.modelsContent.add_widget(self.modelsScroll)
        self.activeView = 'models'
    

    def model_selected(self, instance_selection_list, instance_selection_item):
        if(instance_selection_list.get_selected()):
            items = instance_selection_list.get_selected_list_items()
            if(len(items) == 1):
                model_name = items[0].instance_item.text.split(']')[1].split('[')[0]
                self.modelsContent.clear_widgets()
                self.modelsScroll.clear_widgets()
        
                modelbox = MDFloatLayout(radius = 5, md_bg_color='grey')
                modelbox.add_widget(MDIconButton( icon='arrow-left', on_press=self.show_models, theme_text_color= "Custom", text_color='white' ,pos_hint={'x':0.0, 'y':.0}))
                modelbox.add_widget(MDLabel(text=model_name, pos_hint={'x':0.02, 'y':.35}, theme_text_color= "Custom", text_color='white'))


                self.modelsContent.add_widget(modelbox)
                instance_selection_list.unselected_all()
                self.component_index = -1
            else:
                toast("Só é possível selecionar apenas um item de cada vez...", background=(0,1,1,.7))
                instance_selection_list.unselected_all()
                self.component_index = -1




    def component_selected(self,  instance_selection_item):
        items = instance_selection_item
        if(len(items) == 1):
            self.component_index = items[0]
            if(self.viewAnnotations):
                pos_name = self.annotationObjects['annotation']['object'][items[0]]['pose'] +'_'+ str(items[0])

                self.modelsContent.clear_widgets()
                self.modelsScroll.clear_widgets()
        
                modelbox = MDFloatLayout(radius = 5, md_bg_color='grey')
                modelbox.add_widget(MDIconButton( icon='arrow-left', on_press=self.show_models, theme_text_color= "Custom", text_color='white' ,pos_hint={'x':0.0, 'y':.0}))
                modelbox.add_widget(MDLabel(text=pos_name, pos_hint={'x':0.02, 'y':.35}, theme_text_color= "Custom", text_color='white'))


                self.modelsContent.add_widget(modelbox)
                instance_selection_item.unselected_all()
                self.component_index = -1

            else:
                self.component_node = items[0]
                pos_name = self.programInfo['board']['components'][items[0]]['pose'] +'_'+ str(items[0])
                self.loadEditComponent(self.programInfo['board']['components'][items[0]], items[0])

            
            
        else:
            toast("Só é possível selecionar apenas um item de cada vez...", background=(0,1,1,.7))

    
    def results_selected(self, instance_selection_item, *args):
        
        
        if(instance_selection_item != None):
            try:
            
                pos_name = self.classes[ int(instance_selection_item.cls[0]) ]

                self.modelsContent.clear_widgets()
                self.modelsScroll.clear_widgets()
        
                resultbox = MDFloatLayout(radius = 5, md_bg_color='grey')
                resultbox.add_widget(MDIconButton( icon='arrow-left', on_press=self.show_results, theme_text_color= "Custom", text_color='white' ,pos_hint={'x':0.0, 'y':.0}))
                resultbox.add_widget(MDLabel(text=pos_name, pos_hint={'x':0.02, 'y':.35}, theme_text_color= "Custom", text_color='white'))


                self.modelsContent.add_widget(resultbox)

            except:
                #toast("Falha ao tentar editar...")
                pass
        else:
            toast("Selecionar um item antes de editar...", background=(0,1,1,.7))


    def loadEditComponent(self, comp, index):
        self.modelsContent.clear_widgets()
        self.modelsScroll.clear_widgets()
        
        modelbox = MDFloatLayout(radius = 5, md_bg_color='grey')
        modelbox.add_widget(MDIconButton( icon='arrow-left', on_press=self.show_components, theme_text_color= "Custom", text_color='white' ,pos_hint={'x':0.0, 'y':.0}))
        #modelbox.add_widget(MDLabel(text=comp['pose'], pos_hint={'x':0.02, 'y':.35}, theme_text_color= "Custom", text_color='white'))

        self.tfComp_name = MDTextField( hint_text= "Nome do componente", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .14, pos_hint={'x':0.02, 'y':.84}, font_size= "12dp", line_color_focus='blue' , text= comp['pose'])
        self.tfComp_model = MDTextField( hint_text= "Modelo", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .95, size_hint_y = .14, pos_hint={'x':0.02, 'y':.68}, font_size= "12dp", text= comp['model']) 
        self.tfComp_type = MDTextField( hint_text= "Tipo", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .45, size_hint_y = .14, pos_hint={'x':0.02, 'y':.52}, font_size= "12dp", text= comp['type'])
        self.tfComp_pol = MDTextField( hint_text= "Polaridade", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .45, size_hint_y = .14, pos_hint={'x':0.52, 'y':.52}, font_size= "12dp", text= comp['polarity'])
        self.tfComp_posx = MDTextField( hint_text= "Pos X", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .30, size_hint_y = .14, pos_hint={'x':0.02, 'y':.37}, font_size= "12dp", text= str(comp['x']))
        self.tfComp_posy = MDTextField( hint_text= "Pos Y", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .30, size_hint_y = .14, pos_hint={'x':0.35, 'y':.37}, font_size= "12dp", text= str(comp['y']))
        self.tfComp_posa = MDTextField( hint_text= "Pos A", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .30, size_hint_y = .14, pos_hint={'x':0.68, 'y':.37}, font_size= "12dp", text= str(comp['a']))
        self.tfComp_boxx = MDTextField( hint_text= "Box X", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .30, size_hint_y = .14, pos_hint={'x':0.02, 'y':.22}, font_size= "12dp", text= str(comp['box_x']))
        self.tfComp_boxy = MDTextField( hint_text= "Box Y", helper_text = "Sem caracteres especias", helper_text_mode= "on_error", mode= "fill", size_hint_x = .30, size_hint_y = .14, pos_hint={'x':0.52, 'y':.22}, font_size= "12dp", text= str(comp['box_y']))

        modelbox.add_widget( self.tfComp_name )
        modelbox.add_widget( self.tfComp_model )
        modelbox.add_widget( self.tfComp_type )
        modelbox.add_widget( self.tfComp_pol )
        modelbox.add_widget( self.tfComp_posx )
        modelbox.add_widget( self.tfComp_posy )
        modelbox.add_widget( self.tfComp_posa )
        modelbox.add_widget( self.tfComp_boxx )
        modelbox.add_widget( self.tfComp_boxy )

        modelbox.add_widget( MDFloatingActionButton(icon='content-save-check', on_press=self.saveComponentChanges, md_bg_color='blue', size_hint_x = .10, size_hint_y = .10, pos_hint={'x':0.80, 'y':.03}))


        self.modelsContent.add_widget(modelbox)


    def saveComponentChanges(self, *args):
        try:
            cmp = { 'inspect': True, 'pose': self.tfComp_name.text, 'model': self.tfComp_model.text, 'type': self.tfComp_type.text, 'polarity': self.tfComp_pol.text, 'x': float(self.tfComp_posx.text), 'y': float(self.tfComp_posy.text), 'a': float(self.tfComp_posa.text), 'box_x': float(self.tfComp_boxx.text), 'box_y': float(self.tfComp_boxy.text)}
            self.programInfo['board']['components'][self.component_index] = cmp
            toast("Alterações salvas com sucesso!", background=(0,1,0,.7)) 

            self.loadComponents(self.programInfo['board']['components'])
        except:
            toast("Falha ao tentar salvar alterações!", background=(1,0,0,.7))   


    def model_ComponentDefine(self, *args):
        self.input_dialog('Adicionar componentes', 'Posição')
        
    ##########################################################################################################################################


    def calculate_iou(self, box_1, box_2):
        #poly_1 = Polygon(box_1)
        #poly_2 = Polygon(box_2)
        #iou = poly_1.intersection(poly_2).area / poly_1.union(poly_2).area
        iou = bops.box_iou(box_1, box_2)
        return iou
    
    def check_comp(self, res, comp):
        box1 = torch.tensor([comp], dtype=torch.float)
        box2 = torch.tensor([res], dtype=torch.float)
        iou = float(self.calculate_iou(box2, box1))
        _iou = float(self.calculate_iou(box1, box2))
        return _iou


    def pts2homo(self, x1, y1, w, h, homo):
       
        try:
            pts = np.float32([ [int(x1),int(y1)] ]).reshape(-1,1,2)
            pts = self.visionLib.pts_homography(pts,homo)
            x1 = pts[0][0][0]-(float(w)/2)
            y1 = pts[0][0][1]-(float(h)/2)
            x2 = pts[0][0][0]+(float(w)/2)
            y2 = pts[0][0][1]+(float(h)/2)
        except:
            pass

        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        return x1, y1, x2, y2

    def check_program(self, *args):
        tprogram = time.time()
        programList = self.programInfo['board']['components']
        try:
            self.positives = []
            self.falsepositives = []
            self.negatives = []
            rboxes = self.results[0].boxes.boxes.tolist()
            for c in programList:
                if(c['inspect'] == True):
                    found = False
                    _result = []
                    rem = []
                    iou_min = 0.3
                    iou_max = 0
                    for r in rboxes:
                        x1 = c['x']#-(c['box_x']/2)
                        y1 = c['y']#-(c['box_y']/2)
                        x2 = c['x']+(c['box_x']/2)
                        y2 = c['y']+(c['box_y']/2)

                        x1, y1, x2, y2 = self.pts2homo(x1,y1, c['box_x'], c['box_y'], self.homography)

                        iou = self.check_comp(  [x1,y1,x2,y2], [r[0],r[1],r[2],r[3]])

                        if(iou > iou_max):
                            iou_max = iou


                        if(iou > iou_min or (r[0]<x1 and r[2]>x2 and r[1]<y1 and r[3]>y2 ) ): #intersection
                            _result.append( {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': r[4], 'cover': iou } )
                            rem.append(r)
                            found = True
                            iou_min = iou
                                               
                            
                            

                    if(not found):
                        _result = {'x': c['x'], 'y': c['y'], 'a': c['a'], 'box_x': c['box_x'], 'box_y': c['box_y'], 'pose': c['pose'], 'model': c['model'], 'type': c['type'], 'conf': r[4], 'cover': iou} 
                        self.negatives.append(_result)
                    else:
                        if(len(_result) == 1):
                            if(c['model'] == self.classes[int(rem[0][5])]):
                                self.positives.append(_result[0])
                            else:
                                _result[0]['model'] = self.classes[int(rem[0][5])]
                                self.falsepositives.append(_result[0])
                            rboxes.remove(rem[0])
                        else:
                            cont = 0
                            found = False
                            for rr in _result:
                                if(rr['model'] == self.classes[int(rem[cont][5])]):
                                    self.positives.append(rr)
                                    rboxes.remove(rem[cont])
                                    found = True
                                    break
                                cont+=1
                            
                           
                        
                        
            


                    #self.negatives
            if(len(rboxes)>0):
                for j in rboxes:
                    box_xi = int(j[2]-j[0])
                    box_yi = int(j[3]-j[1])
                    xi1 = int(j[0]+(box_xi/2))
                    yi1 = int(j[1]+(box_yi/2))
                    _result = {'x': xi1, 'y': yi1, 'a': 0, 'box_x': box_xi, 'box_y': box_yi, 'pose': '(???)', 'model': self.classes[int(j[5])], 'type': '', 'conf': r[4], 'cover': 0 } 
                    self.falsepositives.append(_result)


            self.loadMatches(self.results, self.programInfo, self.classes)
            drawingImage = self.visionLib.image.copy()
            self.visionLib.draw_matches( drawingImage, self.positives, self.falsepositives, self.negatives, self.classes, self.homography)
            self.img.texture = self.visionLib.opencv2kivyImage(drawingImage)
            strs = "Resultado de testes  OK >> " + str(len(self.positives)) + "    NG >> " + str(len(self.negatives)) + "   ** >> " + str(len(self.falsepositives))
            #toast( strs, background=(0,1,0,.7))   
        except:
            toast("Falha ao tentar verificar resultados!", background=(1,0,0,.7))   


    def export_annotation(self, *args):
        try:
            
            h = self.homography[0]
            programList = self.programInfo['board']['components']
            _classes = []
            path = config_object['PROGRAMMODEL']['annotation_path']
            stime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            path = path+self.programInfo['name']+'_'+stime+'\\'

            #Folder high level
            if not os.path.exists(path):
                os.mkdir(path)

            #Folder images
            path_images = path+'\images'
            if not os.path.exists(path_images):
                os.mkdir(path_images)
            
            #Folder images
            path_labels = path+'\labels'
            if not os.path.exists(path_labels):
                os.mkdir(path_labels)

            img_comp =   self.visionLib.image.copy()
            filename = self.programInfo['name']+'_'+ stime
            self.visionLib.write_image(img_comp, path_images+'\\'+filename+'.bmp')
            
            with open(path_labels+'\\'+filename+'.txt', "w") as filetxt:
                    filetxt.write("")

            img_h, img_w, d = self.visionLib.image.shape
            for c in programList:
                x = c['x']
                y = c['y']
                a = c['a']
                
                try:
                    pts = np.float32([ [int(x),int(y)] ]).reshape(-1,1,2)
                    pts = self.visionLib.pts_homography(pts,self.homography)
                    x = pts[0][0][0]
                    y = pts[0][0][1]

                except:
                    pass

                x = x/img_w
                y = y / img_h
                w = c['box_x']/img_w
                h = c['box_y']/img_h

                if not c['model'] in _classes:
                    _classes.append(c['model']) 
                    name_class = len(_classes)-1
                else:
                    name_class = _classes.index(c['model'])

                #img_comp =   self.visionLib.image.copy()#self.visionLib.cut_comp(self.visionLib.image, x, y, a, w, h, self.homography)
                
                

                with open(path_labels+'\\'+filename+'.txt', "a") as filetxt:
                    filetxt.write(str(name_class)+(" %.3f" % x)+(" %.3f" % y)+(" %.3f" % w)+(" %.3f\n" % h))
                

            with open(path+'classes.txt', "w") as fileclass:
                for c in _classes:
                    fileclass.write(c+'\n')
            
            toast("Anotacoes exportadas com sucesso!", background=(0,1,0,.7)) 

        except:
            toast("Falha ao tentar verificar resultados!", background=(1,0,0,.7)) 


    ##########################################################################################################################################


    

    def take_picture(self, *args):
        if config_object['CAMERA']['cam1_type'] == 'basler':
            try:
                self.cam = usb_camera.UsbCam()
                #self.cam.initialize()
                if self.cam.connect(config_object['CAMERA']['cam1_name']):
                    self.im = self.cam.acquire_image()
                    self.visionLib.image = self.im
                    self.image_refresh(None)
            except:
                toast("Falha ao tentar capturar imagem de camera BASLER!", background=(1,0,0,.7))  
        else:
            try:
                self.im = self.visionLib.usb_cam_capture( int(config_object['CAMERA']['cam1_name']) )
                self.visionLib.image = self.im
                self.image_refresh(None)
            except:
                toast("Falha ao tentar capturar imagem de camera BASLER!", background=(1,0,0,.7))  



    def save_picture(self, *args):
        pass

    def load_json(self):
        with open(self.jsonFile, 'r') as json_file:
                self.programObjects = json.load(json_file)

    
    def load_pascal_voc(self):
        
        with open(self.jsonFile) as file:
            file_data = file.read() # read file contents
    
        # parse data using package
        #self.annotationObjects = xmltodict.parse(file_data)



    def image_refresh(self, image):
        #Load Objects
        try:
            if(self.viewAnnotations):
                if(self.jsonFile != '' and not self.annotationObjects):
                    self.load_pascal_voc()    
            
                objects = self.annotationObjects
        
            elif(self.modelsContent.children[0].children[0] == self.modelsComponents):
                
                objects = self.programInfo['board']['components']
            
            elif(self.modelsContent.children[0].children[0] == self.modelsResults):
                objects = self.results[0].boxes
            
            else:
                objects = []

        except:
            objects = []

        try:
            if not image:
                self.drawingImage = self.visionLib.image.copy()
        except:
            self.drawingImage = image    


        if self.product_results:     
            try:
                if len(self.homography)>0:
                    self.visionLib.draw_aligned_product(self.drawingImage, self.product_results, self.product_classes, self.homography)
            except:   
                self.visionLib.draw_inference_results_best(self.drawingImage, self.product_results, self.product_classes, None)
        
        if(len(objects)>0):
            if(self.modelsContent.children[0].children[0] == self.modelsComponents):
                
                self.visionLib.drawObjects(self.drawingImage, objects, self.viewAnnotations, self.ori_x, self.ori_y, self.ori_a, self.homography)
            
                nodes = self.modelsContent.children[0].children[0].children[0].children[0].selected_nodes
                if(len(nodes) > 0):
                    self.visionLib.drawSelectedObject(self.drawingImage, objects[nodes[0]], self.ori_x, self.ori_y, self.ori_a, self.homography)

                self.img.texture = self.visionLib.opencv2kivyImage(self.drawingImage)    
            
            elif(self.modelsContent.children[0].children[0] == self.modelsResults):
                #drawingImage = self.visionLib.image.copy()

                self.visionLib.draw_inference_results(self.drawingImage, self.results, self.classes)

                if(self.modelsResults.children[0].children[1].selected_item != None):
                    node = self.modelsResults.children[0].children[1].selected_item
                    self.visionLib.draw_selected_inference(self.drawingImage, self.results[0].boxes[node], self.classes)

                self.img.texture = self.visionLib.opencv2kivyImage(self.drawingImage)

        else:
            self.img.texture = self.visionLib.opencv2kivyImage(self.visionLib.image)

    

    def image_previous(self, *args):
        try:
            extensions = [ '*.jpg', '*.jpeg', '*.bmp'] #config.images_ext#('Images/*.png', 'Images/*.jpg')
            files_list = []
            for ext in extensions:
                files_list.extend(glob.glob( config_object["APPINFO"]["imagespath"] + ext))

            dir = files_list#glob.glob(config_object["APPINFO"]["imagespath"])
            if(self.dirSelectedImage <= 0):
                self.dirSelectedImage = len(dir)-1
            else:
                self.dirSelectedImage -= 1    
            self.imageSource = dir[self.dirSelectedImage]
            
            

            #cv image
            #self.cvImage = self.visionLib.read_image(self.imageSource)
            #self.mainImageLoad(self.imageSource)
            self.visionLib.image = self.visionLib.read_image(self.imageSource) 
            self.image_refresh(None)
            
        except Exception as e:
            self.imageSource = ''

    def showLoadingDialog(self, msg):
        self.dialog = MDDialog(
            text=msg,
            type='simple',
        )
        self.dialog.open()


    def image_next(self, *args):
        try:
            #self.showLoadingDialog("Carregando imagem...")

            extensions = [ '*.jpg', '*.jpeg', '*.bmp'] #config.images_ext#('Images/*.png', 'Images/*.jpg')
            files_list = []
            for ext in extensions:
                files_list.extend(glob.glob( config_object["APPINFO"]["imagespath"] + ext))

            dir = files_list#glob.glob(config_object["APPINFO"]["imagespath"])
            if(self.dirSelectedImage >= len(dir)-1):
                self.dirSelectedImage = 0
            else:
                self.dirSelectedImage += 1    
            self.imageSource = dir[self.dirSelectedImage]
            
            #cv image
            #self.cvImage = self.visionLib.read_image(self.imageSource)
            #self.mainImageLoad(self.imageSource)
            self.visionLib.image = self.visionLib.read_image(self.imageSource) 
            self.image_refresh(None)

            #self.dialog.dismiss()

        except Exception as ex:
            self.imageSource = ''

    def cam_live(self, *args):
        pass




if __name__ == '__main__':
    VisionApp().run()
