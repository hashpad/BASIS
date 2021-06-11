#!/bin/python
import os
import sys
import subprocess
import re
import socket
import time

#Globals
installerPrompt = "badas ~# "
logo = '''

  ____    _    ____    _    ____  
 | __ )  / \  |  _ \  / \  / ___| 
 |  _ \ / _ \ | | | |/ _ \ \___ \
 | |_) / ___ \| |_| / ___ \ ___) |
 |____/_/   \_\____/_/   \_\____/
                               

 Bliss ARCH+DWM Auto-Installer Script
'''

#Prompt Control
def sudo(cmd):
    return "sudo " + cmd
def wait(timeout, msg):
    print(msg)
    for i in range(timeout, 0, -1):
        sys.stdout.write(str(i)+' ')
        sys.stdout.flush()
        time.sleep(1)
    print("\n")

def clr():
    os.system("clear")
    print(logo)

def get_input(prompt = installerPrompt):
    return input(prompt)
class color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    END = '\033[0m'
def success(msg):
    print(color.GREEN + "[✔] " + msg + color.END)
def log(msg):
    print("[*] " + msg + " ...")
def failed(msg):
    print(color.RED + "[x] " + msg + color.END)
def interactive(msg):
    print("> " + msg)
def press_enter():
    input("Press Enter to continue ...")


#Internet utilities
class network:
    HOST = "one.one.one.one"
    PORT = 80

    def is_connected(self):
      try:
        host = socket.gethostbyname(self.HOST)
        s = socket.create_connection((host, self.PORT), 2)
        s.close()
        return True
      except:
         pass
      return False

    def network_menu(self):
        clr()
        log("Pinging 1.1.1.1")
        while not self.is_connected():
            failed("No Internet Connection Found")
            print('''
                    {1}--Use ethernet (make sure ethernet cable is plugged)
                    {2}--Use WLAN\n
                    ''')
            choice = get_input()
            if choice == "1":
                wait(10, "DHCP: Establishing IP")
                continue
            elif choice == "2":
                interactive("insert wlan name (SSID)")
                ssid = get_input()
                interactive("insert wlan password")
                password = get_input()
                self.connect_wlan(ssid, password)
            else:
                failed("Option not listed")
        self.finish_up()

    def connect_wlan(self, ssid, password):
        self.ssid = ssid
        self.password = password
        os.system("iwctl --passphrase " + password + " station device connect " + ssid)
        wait(10, "Waiting for the connection to establish, sleeping for 10 Seconds")

    def finish_up(self):
        success("connection has been established successfully")
        wait(2, "Next step in ...")
        press_enter()

class keyboard:
    LAYOUTS = {
            "us": "USA",
            "ad":"Andorra",
            "af":"Afghanistan",
            "ara":"Arabic",
            "al":"Albania",
            "am":"Armenia",
            "az":"Azerbaijan",
            "by":"Belarus",
            "be":"Belgium",
            "bd":"Bangladesh",
            "in":"India",
            "ba":"Bosnia and Herzegovina",
            "br":"Brazil",
            "bg":"Bulgaria",
            "ma":"Morocco",
            "mm":"Myanmar",
            "ca":"Canada",
            "cd":"Congo, Democratic Republic of the",
            "cn":"China",
            "hr":"Croatia",
            "cz":"Czechia",
            "dk":"Denmark",
            "nl":"Netherlands",
            "bt":"Bhutan",
            "ee":"Estonia",
            "ir":"Iran",
            "iq":"Iraq",
            "fo":"Faroe Islands",
            "fi":"Finland",
            "fr":"France",
            "gh":"Ghana",
            "gn":"Guinea",
            "ge":"Georgia",
            "de":"Germany",
            "gr":"Greece",
            "hu":"Hungary",
            "is":"Iceland",
            "il":"Israel",
            "it":"Italy",
            "jp":"Japan",
            "kg":"Kyrgyzstan",
            "kh":"Cambodia",
            "kz":"Kazakhstan",
            "la":"Laos",
            "lata":"Latin American",
            "lt":"Lithuania",
            "lv":"Latvia",
            "mao":"Maori",
            "me":"Montenegro",
            "mk":"Macedonia",
            "mt":"Malta",
            "mn":"Mongolia",
            "no":"Norway",
            "pl":"Poland",
            "pt":"Portugal",
            "ro":"Romania",
            "ru":"Russia",
            "rs":"Serbia",
            "si":"Slovenia",
            "sk":"Slovakia",
            "es":"Spain",
            "se":"Sweden",
            "ch":"Switzerland",
            "sy":"Syria",
            "tj":"Tajikistan",
            "lk":"Sri Lanka",
            "th":"Thailand",
            "tr":"Turkey",
            "tw":"Taiwan",
            "ua":"Ukraine",
            "gb":"United Kingdom",
            "uz":"Uzbekistan",
            "vn":"Vietnam",
            "kr":"Korea, Republic of",
            "ie":"Ireland",
            "pk":"Pakistan",
            "mv":"Maldives",
            "za":"South Africa",
            "epo":"Esperanto",
            "np":"Nepal",
            "ng":"Nigeria",
            "et":"Ethiopia",
            "sn":"Senegal",
            "brai":"Braille",
            "tm":"Turkmenistan",
            "ml":"Mali",
            "tz":"Tanzania",
            }
    def keyboard_menu(self):
        clr()
        def print_layouts():
            interactive("Please enter the number that corresponds your keyboard layout")
            for k, v in self.LAYOUTS.items():
                index = list(self.LAYOUTS.keys()).index(k)
                print ('{' + str(index) + '}--' + v)
        print_layouts()
        while True:
            choice = int(get_input())
            if(choice > len(self.LAYOUTS) or choice < 0):
                failed("Layout out of range")
            else:
                self.set_layout(list(self.LAYOUTS.values())[choice])
                break
        self.finish_up()

    def set_layout(self, layout):
        os.system("loadkeys " + layout)

    def finish_up(self):
        success("Layout changed successfully")
        wait(2, "Next step in ...")
        press_enter()

 
class bootmode:
    DIR = "/sys/firmware/efi/efivars"
    def is_efi(self):
        return os.path.isdir(self.DIR)
    def __init__(self):
        if not self.is_efi() :
            failed("script doesn't support legacy boot (yet)")
            log("script will be exited")
            exit()

class disk:
    def __init__(self):
        p = subprocess.getoutput(sudo("fdisk -l"))
        compiler = re.compile('Disk (/dev/[a-z0-9]*): ([0-9]*.[0-9]* [G|M]iB).*\n.*: ([a-zA-Z0-9 _-]*)')
        self.devices = compiler.findall(p)

    def list_disks(self):
        for l in self.devices:
            i = self.devices.index(l)
            print ('''{''' + str(i) + '''}--''' + l[2] + '''->''' + l[0] + ''':''' + l[1])
        print('\n{99}--show the output of lsblk for more details')

    def disk_menu(self):
        clr()
        interactive("Please enter the number that corresponds the device, on which you wish to install")
        self.list_disks()
        while True:
            choice = int(get_input())
            if(choice >= len(self.devices) or choice < 0) and (choice != 99):
                failed("Option not found")
            elif choice == 99:
                os.system("lsblk")
                continue
            else:
                self.installation_disk = self.devices[choice]
                self.auto_patition()
                break
            
    def auto_patition(self):
        def parted():
            failed("not yet implemented")
        failed("not yet implemented")
#Installer
class badas:
    bootmode = bootmode()
    network = network()
    keyboard = keyboard()
    disk = disk()
    def __init__(self):
        clr()
        self.keyboard.keyboard_menu()

        self.network.network_menu()

        self.disk.disk_menu()

        # self.partition()

        # self.mount_file_system()

            # self.pactrap() // Kernel options

            # self.genfstab()

            # self.chroot()

            # self.timezone()

            # self.hwclock()
            
            # self.locale_gen()

            # self.hostname()

            # self.hosts()

            # self.initramfs()

        # self.users()

        # self.extras()

        # self.bootloader()

badas = badas()
