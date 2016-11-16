import os
import sys
import subprocess
from lxml import etree
from subprocess import Popen

def create():
	return
def start():
	return
def stop():
	return
def destroy():
	return

parametros_comando = sys.argv
opciones_disponibles = ["create", "start", "stop", "destroy", "-h"]
orden = ""
parametro = ""
ejecutar = False
#Comienzo de ejecucion

#Lectura del comando
if len(parametros_comando) == 2:
	orden = parametros_comando[1]
	parametro = "serie"
	if opciones_disponibles.count(orden):
		print("funciona")
	else: 
		print("fallo2")
	
else:
	print("fallo1")
	