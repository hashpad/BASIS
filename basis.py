#!/bin/python
import os
import sys
import subprocess
import re
import socket
import time

#Globals
installerPrompt = "basis ~# "
logo = '''

oooooooooo      o       oooooooo8 ooooo  oooooooo8  
 888    888    888     888         888  888         
 888oooo88    8  88     888oooooo  888   888oooooo  
 888    888  8oooo88           888 888          888 
o888ooo888 o88o  o888o o88oooo888 o888o o88oooo888
                               

 Bliss ARCH Simple Installer Script
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
def print_list_parallel(l):
    range_end = int(len(l) / 2) if int(len(l)) % 2 == 0  else int(len(l) / 2) + 1
    for i in range(0, range_end):
        s1 = '''{''' + str(i) + '''}--''' + l[i]
        if((range_end + i < int(len(l)))):
            s2 = '''{''' + str(range_end + i) + '''}--''' + l[range_end + i]
        else:
            s2 = ""
        print('{0:30}  {1}'.format(s1, s2))



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
            "fr":"France",
            "de":"Germany",
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
                self.set_layout(list(self.LAYOUTS.keys())[choice])
                break
        self.finish_up()

    def set_layout(self, layout):
        os.system("loadkeys " + layout)
        self.layout = layout
    def get_layout(self):
        return self.layout


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
    ONE_MIB = 1048576
    BOOT_SIZE_MiB = 512
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
                interactive("Please enter a swap size in mib (example: for 8GB swap enter 8096)")
                swap_size = int(get_input())

                device_size_bytes = int(subprocess.getoutput("lsblk -bd -o SIZE " + self.installation_disk[0] + " | tail -n -1"))
                while (swap_size * self.ONE_MIB >= (device_size_bytes - self.BOOT_SIZE_MiB * self.ONE_MIB)):
                    failed("swap size is too large")
                    swap_size = int(get_input())

                self.auto_patition(self.installation_disk[0], swap_size)
                self.format_disks(self.installation_disk[0])
                self.mount_file_system(self.installation_disk[0])

                break
        self.finish_up()

            
    def format_disks(self, device):
        log("Formatting the disks")
        os.system("mkfs.ext4 " + device + "3")
        os.system("mkfs.vfat -F32  " + device + "1")
        os.system("mkswap " + device + "2")
        os.system("swapon " + device + "2")
        success("Disk formatting has been successfull")

    def auto_patition(self, device, swap_size):
        def parted(device, swap_size):
            return ("parted --script -a optimal " + device + " \
            unit mib \
            mklabel gpt \
            mkpart primary 1 " + str(self.BOOT_SIZE_MiB) + " \
            mkpart primary "   + str(self.BOOT_SIZE_MiB) + " " + str(self.BOOT_SIZE_MiB + swap_size) + " \
            mkpart primary " + str(self.BOOT_SIZE_MiB + swap_size) + " 100% set 1 boot on")

        os.system(parted(device, swap_size).strip())
        success("Disk partitioning has been successfull")

    def mount_file_system(self, device):
        os.system("mount " + device + "3 /mnt")
        os.system("mkdir /mnt/boot")
        os.system("mount " + device + "1 /mnt/boot")
        success("Systemfiles mounted successfully")

    def finish_up(self):
        success("Disk configuration has been successfull")
        wait(2, "Next step in ...")
        press_enter()

class configure_and_install:
    def install(self):
        os.system("pacstrap /mnt base linux linux-firmware")
        success("base, linux and linux-firmware have been installed successfully")
    def gen_fstab(self):
        os.system("genfstab -U /mnt >> /mnt/etc/fstab")
        success("fstab has been generated")
    def chroot(self, cmd):
        os.system("arch-chroot /mnt " + cmd)
        log("running " + cmd + " in chroot mode")
    def list_continent(self):
        get_continents = subprocess.getoutput('find /usr/share/zoneinfo -maxdepth 1 -type d -printf "%P\n" | tail -n +2')
        self.continents = get_continents.splitlines()
        print_list_parallel(self.continents)
            
    def list_cities(self, chosen_continent):
        get_cities = subprocess.getoutput('find /usr/share/zoneinfo/' + chosen_continent + ' -maxdepth 1 -type f -printf "%P\n"')
        self.cities = get_cities.splitlines()
        print_list_parallel(self.cities)

            


    def time_zone(self):
        clr()
        interactive("Please choose a continent from the list bellow")
        self.list_continent()
        choice = 0
        while True:
            choice = int(get_input())
            if(choice >= len(self.continents) or choice < 0):
                failed("Continent number is not in the list")
                continue
            break
        self.continent = self.continents[choice]

        interactive("Please choose a country from the list bellow")
        self.list_cities(self.continent)
        while True:
            choice = int(get_input())
            if(choice >= len(self.cities) or choice < 0):
                failed("city number is not in the list")
                continue
            break
        self.city = self.cities[choice]

        self.chroot("ln -sf /usr/share/zoneinfo/" + self.continent + "/" + self.city + " /etc/localtime")
        success("timezone was set successfully")

    def hw_clock(self):
        self.chroot("hwclock --systohc")
        log("Hardware clock set to system clock")

    def interactive_install_template(self):
        # self.install()
        # self.gen_fstab()
        self.time_zone()
        self.hw_clock()

    def __init__(self, keyboard):
        clr()
        self.keyboard = keyboard


#Installer
class basis:
    bootmode = bootmode()
    network = network()
    keyboard = keyboard()
    disk = disk()
    cai = configure_and_install(keyboard)
    def __init__(self):
        clr()
        # self.keyboard.keyboard_menu()

        # self.network.network_menu()

        # self.disk.disk_menu()

        self.cai.interactive_install_template()


            
            # self.locale_gen()

            # self.hostname()

            # self.hosts()

            # self.initramfs()

        # self.users()

        # self.extras()

        # self.bootloader()

basis = basis()
