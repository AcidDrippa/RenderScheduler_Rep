import re
import os
import sys
import socket
import signal
import threading

#from PySide import QtGui
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtCore import *

import Utils

class RemoteServer:
    def __init__(self):
        self.HOST = ""
        self.PORT = 1500
        self.mayahost = "localhost"
        self.mayaport = 1000
    
    def ShutDown(self):
        print "Shutting the server down..."
                
        self.serverSocket.close()
        print "..done\r\n"
        
    def SetPort(self, port):
        self.PORT = port
        
    def Activate(self):
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serverSocket.bind((self.HOST, self.PORT))
        self.serverSocket.listen(1)

        while True:
            print "Server listening on %s %s" % (self.HOST, str(self.PORT))
            try:
                sock, addr = self.serverSocket.accept()
                    
                cfile = sock.makefile('rw', 0)
                line = cfile.readline()
                    
                line = line.rstrip('\n')

                if line=="quit":
                    self.ShutDown()
                    break

                res = self.ParseAndExecuteResponse(line)
                cfile.write(res)

                cfile.close()
                #sock.close()
                    
                print line
                    
            except KeyboardInterrupt:
                self.ShutDown()
                
    def ParseAndExecuteResponse(self, line):
        res = self.SendInfo(self.mayahost, self.mayaport, line)
        return res
    
    def SendInfo(self, host, port, mayapacket):
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #sock.settimeout(60)
        try:
            # Connect to server and send data
            sock.connect((host, port))
            sock.sendall(mayapacket)
            #sock.sendall("polyCube;")
            # Receive data from the server and shut down
            received = sock.recv(16384)

        except socket.error:
            print "Socket connect error: Maya commandPort not open? \n"
            return
        finally:
            sock.close()
        return received
                  
def SendQuit(port):
        # Create a socket (SOCK_STREAM means a TCP socket)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Connect to server and send data
            sock.connect((rserver.HOST, port))
            sock.sendall("quit\n")

            # Receive data from the server and shut down
            received = sock.recv(16384)
        except socket.error:
            print "Socket connect error..\r\n"
            return
        finally:
            sock.close()
        #time.sleep(5)
        print received
        
rserver = RemoteServer()

class ServerThread(QtCore.QThread):
        
    def run(self):
        rserver.Activate()
        
class RSUI(QtGui.QDialog):
    def __init__(self, parent=None):
        super(RSUI, self).__init__(parent)
        
        self.serverthread = ServerThread()
        
        self.initUI()
        
    def initUI(self):
        self.initSubElements()
        self.setGeometry(QtCore.QRect(600, 300, 550, 350))
        self.setWindowTitle('Remote Server')
        
        
    def initSubElements(self):
        self.portLabel = QtGui.QLabel()
        self.portLabel.setText("Port :")
        self.portField = QtGui.QLineEdit()
        self.portField.setText(str(rserver.PORT))
        self.hostLabel = QtGui.QLabel()
        self.hostLabel.setText("Host :")
        self.hostField = QtGui.QLineEdit()
        self.hostField.setText(Utils.FindMyIP())

        self.startButton = QtGui.QPushButton("Start")
        self.startButton.clicked.connect(self.OnStart)

        self.stopButton = QtGui.QPushButton("Stop")
        self.stopButton.clicked.connect(self.OnStop)

        self.stopButton.setEnabled(False)
        
        self.vLayout = QtGui.QVBoxLayout()
        self.hLayout = QtGui.QHBoxLayout()
        self.hLayoutB = QtGui.QHBoxLayout()
        self.hLayoutH  = QtGui.QHBoxLayout()
        self.hLayout.addStretch(1)
        self.hLayout.addWidget(self.portLabel)
        self.hLayout.addWidget(self.portField)
        self.hLayoutB.addWidget(self.startButton)
        self.hLayoutB.addWidget(self.stopButton)
        self.hLayoutH.addWidget(self.hostLabel)
        self.hLayoutH.addWidget(self.hostField)

        self.vLayout.addLayout(self.hLayout)
        self.vLayout.addLayout(self.hLayoutH)
        self.vLayout.addLayout(self.hLayoutB)
        self.vLayout.setAlignment(Qt.AlignTop)
        self.setLayout(self.vLayout)
        
    def OnStart(self):
        # Activate the server on a separate thread
        self.stopButton.setEnabled(True)
        self.startButton.setEnabled(False)
        rserver.HOST = self.hostField.text()
        rserver.SetPort(int(self.portField.text()))
        #threading.Thread(target=rserver.Activate).start()
        self.serverthread.start()

    def OnStop(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        threading.Thread(target=SendQuit, args=(int(self.portField.text()),)).start()
    
def main():

    app = QtGui.QApplication(sys.argv)

    s = RSUI()
    s.setModal(True)
    s.show()

    app.setStyle("plastique")
    app.setPalette(QtGui.QPalette(QtGui.QColor(52, 52, 52), QtGui.QColor(52, 52, 52)) )
    
    sys.exit(app.exec_())


if __name__=='__main__':
    main()
    