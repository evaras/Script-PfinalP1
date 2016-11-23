import os
import sys
import subprocess
from lxml import etree
from subprocess import Popen
import os.path
import time
from string import Template


#Lista de configuracion
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
servidores_acrear = []
#Variables Start
servidores_arrancados = []
servidores_a_arrancar = []

#Funciones principales de ejecucion
def create(numerodemaquinas):
	print ("Dentro del create, el parametro que le pasamos es ", numerodemaquinas)
	numerodeservers = numerodemaquinas
	checkServers(numerodeservers)
	print ("Esto es el array servidores creados", servidores_creados)
	print ("Esto es el array servidores_acrear", servidores_acrear)
	
	for i in servidores_acrear:
		creacion(i)
		numerodemaquinas = numerodemaquinas -1
	return

def start(numerodemaquinas):	#Configuracion de host
	configuracionEscenario()
	#Comprobacion de existencia de las maquinas
	checkServers(numerodemaquinas)
	c1_lb_exist = False
	servidores_exist = False
	if servidores_creados.count("c1") and servidores_creados.count("lb"):
		c1_lb_exist = True
	if not len(servidores_creados)-2 < numerodemaquinas:
		servidores_exist = True
	if c1_lb_exist == True and servidores_exist == True:
		arrancar(numerodemaquinas)
	else:
		print ("No se dan las condiciones correctas para arrancar las maquinas solicitadas")



def stop():
	return
def destroy():
	return

#Funciones auxiliares
def checkServers(numerodeservers):
	print ("Esta es la variable numero de servers en la funcion numero de servers ", numerodeservers)
	numero = numerodeservers
	numerocreados = 0
	#Comprobacion de c1
	if os.path.exists("/mnt/tmp/pfinal/c1.qcow2"):
		servidores_creados.append("c1")
	else:
		servidores_acrear.append("c1")

	#comprobacion de lb
	if os.path.exists("/mnt/tmp/pfinal/lb.qcow2"): 
		servidores_creados.append("lb")
	else:
		servidores_acrear.append("lb")

	#Comprobacion de servidores ya creados
	for i in opciones_parametros:
		if os.path.exists("/mnt/tmp/pfinal/S"+i+".qcow2"):
			servidores_creados.append('S'+i)
			numerocreados = numerocreados +1
	numero = numero - numerocreados
	if numero > 0:
		while numero > 0:
			for i in opciones_parametros:
				if not servidores_creados.count("S"+i):
					servidores_acrear.append('S'+i)
					numero = numero-1
				if numero == 0:
					break
	return

#Funciones auxiliares CREATE
def creacion(name):
	os.system('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 '+name+'.qcow2')
	os.system('cp plantilla-vm-p3.xml '+name+'.xml')
	modificarXML(name)
	return
def modificarXML(name):
	print("Entramos en la funcion de modificarXML")
	tree = etree.parse(name+".xml")
	root = tree.getroot()
	doc = etree.ElementTree(root)

	name1 = root.find("name")
	name1.text = name

	source = root.find("./devices/disk/source")
	source.set("file", "/mnt/tmp/pfinal/"+name+".qcow2")

	interface = root.find("./devices/interface/source")
	
	if name == 'c1':
		interface.set("bridge", "LAN1")
	elif name == 'lb':
		interface.set("bridge", "LAN1")
		interface2 = root.find("devices")
		writeinterface2 = etree.SubElement(interface2, 'interface', type='bridge')
		writesource2 = etree.SubElement(writeinterface2, 'source', bridge='LAN2')
		writemodel2 = etree.SubElement(writesource2, 'model', type='virtio')
	else:
		interface.set("bridge", "LAN2")
	outFile = open(name+".xml","w")
	doc.write(outFile)
	return
#Funciones auxiliares start
def configuracionEscenario():
	os.system("sudo brctl addbr LAN1")
	os.system("sudo brctl addbr LAN2")
	os.system("sudo ifconfig LAN1 up")
	os.system("sudo ifconfig LAN2 up")
	os.system("sudo ifconfig LAN1 10.0.1.3/24")
	os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")
	os.system('HOME=/mnt/tmp sudo virt-manager')
	return
def arrancada(hostname):
	if os.system("sudo virsh list | grep -q "+hostname) == 0:
		return 1
	else:
		return 0
'''def checkArrancados(numeroaarrancar): #Rellena una lista con los servidores que ya han sido arrancados
	numero = numeroaarrancar
	numeroserversarrancados = 0
	for i in servidores_creados:
		if os.system("sudo virsh list | grep -q "+i) == 0:
			return
		else:
			servidores_a_arrancar.append(i)
	return
def servidoresAArrancar(numerodemaquinas): #Rellena una lista con los nombres de los servidores que faltan por arrancar
	numeroarrancados = len(servidores_arrancados) - 2
	numeroservsaarrancar = numerodemaquinas - numeroarrancados
	numeroauxiliar = 1
	while numeroservaarrancar>0:
		for i in servidores_creados:
			if servidores_arrancados.count(i):
				numeroauxiliar = numeroauxiliar + 1
			else:
				servidores_a_arrancar.append(i)
				numeroservacrear = numeroservacrear - 1
	return'''
#Arranca los servidores pendientes 
def arrancar(numerodemaquinas):
	numeroarrancadas = numerodemaquinas
	arranca("host")
	if arrancada("c1") == 1:
		print "Maquina virtual c1 esta arrancada"
	else:
		arranca("c1")
	if arrancada("lb") == 1:
		print "Maquina virtual lb esta arrancada"
	else:
		arranca("lb")
	for i in servidores_creados:
		if arrancada(i) == 1:
			print "Maquina virtual "+i+" esta arrancada"
			numeroarrancadas = numeroarrancadas -1
		else:
			arranca(i)
			numeroarrancadas = numeroarrancadas -1
def arranca(name):
	if (name != "host"):
		os.chdir("/mnt/tmp/pfinal")
		os.system('sudo vnx_mount_rootfs -s -r '+name+'.qcow2 mnt')
		os.chdir("/mnt/tmp/pfinal/mnt/etc")
		dochostname = open("hostname", "w")
		dochostname.write(name)
		dochostname.close()
		hosts(name)
		os.chdir("/mnt/tmp/pfinal/mnt/etc/network")
		interface(name)
		os.chdir("/mnt/tmp/pfinal")
		os.system('sudo vnx_mount_rootfs -u mnt')
		if subprocess.call(["sudo","virsh","create",name+".xml"]) != 0:
			os.chdir("/mnt/tmp/pfinal")
			os.system('sudo virsh create '+name+'.xml')
			terminal = "sudo virsh console "+name
			p1 = Popen(['xterm', '-e', terminal])
	else:
		os.system("sudo ifconfig LAN1 10.0.1.3/24")
		os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")
def hosts(name):
	dochosts = open("hosts", "w")
	dochosts.write("127.0.0.1	localhost"+"\n")
	dochosts.close()
	dochosts = open("hosts", "a")
	dochosts.write("127.0.1.1	"+name+"\n")
	dochosts.write("# The following lines are desirable for IPv6 capable hosts"+"\n")
	dochosts.write("::1     localhost ip6-localhost ip6-loopback"+"\n")
	dochosts.write("ff02::1 ip6-allnodes"+"\n")
	dochosts.write("ff02::2 ip6-allrouters")
	dochosts.close()
def interface(name):
	if  (name != "c1" and name != "lb"):
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.2.1"+str(name[1])+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.2.0"+"\n")
		docinterface2.write("broadcast 10.0.2.255"+"\n")
		docinterface2.write("gateway 10.0.2.1"+"\n")
		docinterface2.close()
	elif name == "c1":
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.1.2"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.1.0"+"\n")
		docinterface2.write("broadcast 10.0.1.255"+"\n")
		docinterface2.write("gateway 10.0.1.1"+"\n")
		docinterface2.close()
	elif name == "lb":
		docinterface = open("interfaces", "w")
		docinterface.write("# The loopback network interface"+"\n")
		docinterface.close()
		docinterface2 = open("interfaces", "a")
		docinterface2.write("auto lo"+"\n")
		docinterface2.write("iface lo inet loopback"+"\n")
		docinterface2.write("# The primary network interface"+"\n")
		docinterface2.write("auto eth0"+"\n")
		docinterface2.write("iface eth0 inet static"+"\n")
		docinterface2.write("address 10.0.1.1"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.1.0"+"\n")
		docinterface2.write("broadcast 10.0.1.255"+"\n")
		docinterface2.write("gateway 10.0.1.1"+"\n")
		docinterface2.write("# The secundary network interface"+"\n")
		docinterface2.write("auto eth1"+"\n")
		docinterface2.write("iface eth1 inet static"+"\n")
		docinterface2.write("address 10.0.2.1"+"\n")
		docinterface2.write("netmask 255.255.255.0"+"\n")
		docinterface2.write("network 10.0.2.0"+"\n")
		docinterface2.write("broadcast 10.0.2.255"+"\n")
		docinterface2.write("gateway 10.0.2.1"+"\n")
		docinterface2.close()
		os.system("sed -i 's/#net.ipv4.ip_forward=1/net.ipv4.ip_forward=1/' /mnt/tmp/pfinal/mnt/etc/sysctl.conf")
	else:
		print "Solamente se pueden arrancar 7 maquinas virtuales como maximo"				
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
	print ("La orden introducida es: "+ orden)
	if opciones_disponibles.count(orden):
		print ("El parametro introducido es: "+ parametro)
		if opciones_parametros.count(parametro):
			ejecutar=True
			parametro_num=int(parametro)
			print ("Y el int convertido es ", parametro_num)
			if os.path.exists("/mnt/tmp/pfinal"):
				os.chdir("/mnt/tmp/pfinal")
			else:
				os.mkdir("/mnt/tmp/pfinal")
				os.chdir("/mnt/tmp/pfinal")
			if not os.path.exists("cdps-vm-base-p3.qcow2.bz2") and not os.path.exists("cdps-vm-base-p3.qcow2"):
				os.system("cp /mnt/vnx/repo/cdps/cdps-vm-base-p3.qcow2.bz2 .")
				os.system("bunzip2 cdps-vm-base-p3.qcow2.bz2")
			os.system("cp /mnt/vnx/repo/cdps/plantilla-vm-p3.xml .")
			if not os.path.exists("/mnt/tmp/pfinal/mnt"):
				os.mkdir("/mnt/tmp/pfinal/mnt")
			print("Va bien")
		else:
			print("Parametro incorrecto")
	else:
		print("Orden no disponible")		
else:
	print("Para ejecutar el script debe definir una orden entre las posibles, para mas info opcion -h")

#Si el comando es correcto, comenzamos la ejecucion
if (ejecutar == True):
	if orden=="create":
		create(parametro_num)
		print ("Maquinas creadas correctamente y fin de ejecucion")
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

