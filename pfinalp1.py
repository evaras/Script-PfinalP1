import os
import sys
import subprocess
from lxml import etree
from subprocess import Popen

#Lista de configuración
#Lectura de las solicitudes de ejecucion
parametros_comando = sys.argv
#Lista de opciones disponibles en los parametros de ejecucion
opciones_disponibles = ["create", "start", "stop", "destroy", "-h"]
opciones_parametros = ["1","2","3","4","5"]
orden = ""
parametro = ""
parametro_num = 0;
#Variable de ejecucion
ejecutar = False
#Variables create
servidores_creados = []

#Funciones principales de ejecucion
def create():
	#Comprobacion y creacion de c1
	if os.path.exists("/mnt/tmp/pfinal/c1.qcow2"):
		return 
	else:
		creacion("c1")
	#comprobacion y creacion de lb
	if os.path.exists("/mnt/tmp/pfinal/lb.qcow2"):
		return 
	else:
		creacion("lb")
	#comprobacion y creacion de servidores
	checkServers()

def start():
	return
def stop():
	return
def destroy():
	return

#Funciones auxiliares
def creacion(name1):
	os.system('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 '+name1+'.qcow2')
	os.system('cp plantilla-vm-p3.xml '+name1+'.xml')
	tree = etree.parse('/mnt/tmp/pfinal/'+name1+'.xml')
	root = tree.getroot()
	doc = etree.ElementTree(root)
	name = root.find("name")
	source = root.find("./devices/disk/source")
	interface = root.find("./devices/interface/source")
	name.text = name2
	source.set("file", "/mnt/tmp/pfinal/"+name1+".qcow2")
	if name1 == 'c1':
		interface.set("bridge", "LAN1")
	elif name1 == 'lb':
		interface.set("bridge", "LAN1")
		interface2 = root.find("devices")
		writeinterface2 = etree.SubElement(interface2, 'interface', type='bridge')
		writesource2 = etree.SubElement(writeinterface2, 'source', bridge='LAN2')
		writemodel2 = etree.SubElement(writesource2, 'model', type='virtio')
	else:
		interface.set("bridge", "LAN2")




#Comienzo de ejecucion

#Lectura del comando:
if len(parametros_comando) == 2: #Si solo se define la orden sin introducir parametros
	orden = parametros_comando[1]
	parametro = "serie"
	if opciones_disponibles.count(orden):
		ejecutar = True
elif len(parametros_comando) == 3: #Si se define la orden y los parametros correctamente
	orden = parametros_comando[1]
	parametro = parametros_comando[2]
	if opciones_disponibles.count(orden):
		print (parametro)
		if opciones_parametros.count(parametro):
			ejecutar=True
			parametro_num=int(parametro)
			print("Va bien")
		else:
			print("Parametro incorrecto")
	else:
		print("Orden no disponible")		
else:
	print("Para ejecutar el script debe definir una orden entre las posibles, para mas info opcion -h")

#Si el comando es correcto, comenzamos la ejecución
if (ejecutar == True):
	if orden=="create":
		create(parametro_num)
	elif orden=="start":
		start(parametro_num)
	elif orden=="stop":
		stop(parametro_num)
	elif orden=="destroy":
		destroy(parametro_num)
	elif orden=="-h":
		ayuda()
else:
	print("fallo comando")

