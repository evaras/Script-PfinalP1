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
#Variable que almacena los nombres de los servidores disponibles para arrancar
servidores_creados = []
#Variable auxiliar empleada para almacenar los nombres de los servidores a crear
servidores_acrear = []



#Funciones principales de ejecucion


#Funcion principal de creacion de MVs
def create(numerodemaquinas):

	#Función que comprueba que servidores están creados ya, y cuales faltan añadiendolos a las listas correspondientes
	checkServers(numerodemaquinas)
	
	#En funcion de la informacion obtenida en la funcion checkservers crea las maquinas correspondientes
	for i in servidores_acrear:

		#funcion de creacion de una maquina virtual
		creacion(i)

		numerodemaquinas = numerodemaquinas -1
	return

#Funcion principal de arranque de MVs
def start(numerodemaquinas):	
	
	#Configuracion del escenario, en su apartado se explican los pasos
	configuracionEscenario()

	#Empleamos la funcion checkservers para guardar en una lista los servidores existentes
	checkServers(numerodemaquinas)

	#Variable que almacena la existencia/inexistencia de c1 y lb
	c1_lb_exist = False

	#Variable que almacena la existencia/inexistencia de los servidores que se busca arrancar
	servidores_exist = False

	#Comprobamos que c1 y lb existen
	if servidores_creados.count("c1") and servidores_creados.count("lb"):

		#Si existen modificamos la variable:
		c1_lb_exist = True

	#Comprobamos que existen servidores suficientes para arrancar
	if not len(servidores_creados)-2 < numerodemaquinas:

		#Si existen modificamos la avriable
		servidores_exist = True

	#Si se cumplen todas las condiciones se procede a arrancar las maquinas
	if c1_lb_exist == True and servidores_exist == True:

		#Funcion encargada de arrancar las maquinas
		arrancar(numerodemaquinas)

	#Si no existen se escribe un mensaje de aviso
	else:
		print ("No se dan las condiciones correctas para arrancar las maquinas solicitadas")
		print ("Debe crear las maquinas que desee ejecutar antes mediante la opcion create <num_servidores>")
		print ("Para mas informacion emplee el comando -help")

#Funcion principal de parada de maquinas
def stop():
	return

#Funcion principal de destruccion de maquinas
def destroy():
	return

#Funciones auxiliares


#CHECKSERVERS(): Esta funcion realiza dos funciones:
#1_ Comprueba los servidores existentes y los añade a una lista
#2_ Calcula cuales se deben crear para satisfacer el parametro introducido
def checkServers(numerodeservers):
	
	
	#Variable que representa el numero de servidores a crear, se modifica mas adelante
	numero = numerodeservers

	#Variable auxiliar que almacena el numero de servidores creados
	numerocreados = 0


	#Comprobacion de c1 (explicacion os.path.exists: Devuelve true si el dierctorio/archivo existe y false en caso contrario)
	if os.path.exists("/mnt/tmp/pfinal/c1.qcow2"):
		#Si c1 existe lo añade a la lista de servidores creados (explicacion .append(): añade el elemento entre parentesis a la lista que lo llama)
		servidores_creados.append("c1")
	else:
		#Si c1 no existe lo añade a la lista de pendientes de crear
		servidores_acrear.append("c1")

	#comprobacion de lb
	if os.path.exists("/mnt/tmp/pfinal/lb.qcow2"):
		#Si lb existe lo añade a la lista de servidores creados 
		servidores_creados.append("lb")
	else:
		#Si lb no existe lo añade a la lista de pendientes de crear
		servidores_acrear.append("lb")

	#1_ Comprobacion de servidores, comprueba que servidores existen y los añade a la lista de servidores_creados
	#2_ Por cada servidor que exista incrementa la variable auxiliar servidores creados
	for i in opciones_parametros:

		#Si el servidor comprobado existe
		if os.path.exists("/mnt/tmp/pfinal/S"+i+".qcow2"):

			#Añadimos el servidor a la lista
			servidores_creados.append('S'+i)

			#Incrementamos la variable que cuenta el numero de servidores existentes
			numerocreados = numerocreados +1

	#Calculo de servidores que debemos crear para cumplir con el parametro introducido
	numero = numero - numerocreados

	#Si la variable es mayor que cero debemos crear x servidores
	if numero > 0:

		#Mientras la variable sea >0 debemos seguir creando servidores
		while numero > 0:

			#Recorremos la lista con las opciones de servidores
			for i in opciones_parametros:

				#Si no existe el servidor comprobado
				if not servidores_creados.count("S"+i):

					#Lo añadimos a la lista de pendientes de crear
					servidores_acrear.append('S'+i)

					#Decrementamos la variable de pendientes
					numero = numero-1

				#Cuando la variable llega a 0 salimos del bucle 
				if numero == 0:
					break
	return


#Funciones auxiliares CREATE

#Funcion estricta de creacion:
#1_ Crea la imagen .qcow
#2_ Crea la copia del xml y lo modifica
def creacion(name):

	#Creacion de la imagen .qcow
	os.system('qemu-img create -f qcow2 -b cdps-vm-base-p3.qcow2 '+name+'.qcow2')

	#Copia de la plantilla xml con el nombre adecuado
	os.system('cp plantilla-vm-p3.xml '+name+'.xml')

	#Llamada a la funcion encargada de modificar el xml
	modificarXML(name)
	return

#Funcion de modificación de la informacion del xml
def modificarXML(name):
	print("Entramos en la funcion de modificarXML")

	#Creamos el arbol a partir del documento xml correspondiente
	tree = etree.parse(name+".xml")

	#Obtenemos la raíz
	root = tree.getroot()
	doc = etree.ElementTree(root)

	#Cambiamos el nombre de la maquina (etiqueta name del xml)
	name1 = root.find("name")
	name1.text = name

	#Cambiamos el archivo predeterminado en el que buscar la imagen
	source = root.find("./devices/disk/source")
	source.set("file", "/mnt/tmp/pfinal/"+name+".qcow2")

	#Modificamos el valor de la etiqueta ethernet en funcion de las carcateristicas de la maquina
	interface = root.find("./devices/interface/source")

	#c1 se conecta a la LAN1
	if name == 'c1':
		interface.set("bridge", "LAN1")

	#lb a la 1 y a la 2, eso implica que debemos duplicar el campo interface
	elif name == 'lb':

		#Modificacion del campo interface existente
		interface.set("bridge", "LAN1")
		interface2 = root.find("devices")

		#Creacion del segundo campo interface
		writeinterface2 = etree.SubElement(interface2, 'interface', type='bridge')
		writesource2 = etree.SubElement(writeinterface2, 'source', bridge='LAN2')
		writemodel2 = etree.SubElement(writesource2, 'model', type='virtio')
	
	#Modificacion de lcampo interface de los servidores, estos se conectan exclusivamente a la LAN2
	else:
		interface.set("bridge", "LAN2")

	#Seleccionamos el archivo a reescribir
	outFile = open(name+".xml","w")

	#Reescribimos
	doc.write(outFile)
	return


#Funciones auxiliares START

#CONFIGURACIONESCENARIO(): Funcion de configuracion de escenario, activa las LANs y los bridges 
def configuracionEscenario():
	os.system("sudo brctl addbr LAN1")
	os.system("sudo brctl addbr LAN2")
	os.system("sudo ifconfig LAN1 up")
	os.system("sudo ifconfig LAN2 up")
	os.system("sudo ifconfig LAN1 10.0.1.3/24")
	os.system("sudo ip route add 10.0.0.0/16 via 10.0.1.1")
	os.system('HOME=/mnt/tmp sudo virt-manager')
	return

#ARRANCADA(): Comprueba si una maquina esta arrancada
def arrancada(hostname):
	if os.system("sudo virsh list | grep -q "+hostname) == 0:
		return 1
	else:
		return 0

#ARRANCAR: Arranca los servidores pendientes
#1_ Comprueba que servidores estan arrancados
#2_ Arranca los que falten por arrancar 
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

