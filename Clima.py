from pprint import pprint
import requests
import time
import schedule
import smtplib
from string import Template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pysftp



ARCHIVO_PLANTILLA = r"C:\Users\Owner\Documents\PUCMM\Temas Especiales 1\plantilla.txt"
MI_CORREO = '***Correo***'
PASSWORD = '***Contraseña***'

MTA_HOST = 'smtp.gmail.com'
MTA_PORT = 587  # SSL: 465, TLS: 587

url = "http://api.openweathermap.org/data/2.5/forecast"

querystring = {"id":"3492914","APPID":"4db9e05fcaabc024ae1b53c1a0e7f7e0","units":"metric","lang": "es"}

payload = ""
headers = {
    'cache-control': "no-cache",
    'Postman-Token': "c30d04cf-4750-4f06-ac80-85f8400670b7"
    }


def lee_plantilla(filename):
    """
    Returna un objeto Template que encapsula el contenido de filename
    """

    with open(filename, 'r', encoding='iso-8859-1') as archivo:
        contenido = archivo.read()
    return Template(contenido)


def main():
    message_template = lee_plantilla(ARCHIVO_PLANTILLA)

    # crea sesión SMTP
    s = smtplib.SMTP(host=MTA_HOST, port=MTA_PORT)
    s.starttls()
    #s.set_debuglevel(1)  # esto se debería de remover en un ambiente real
    s.login(MI_CORREO, PASSWORD)
    msj = MIMEMultipart()  # create a message

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)

    Data = response.json()
    # pprint(Data)
    for i in Data['list']:
        print("Pronostico para " + i['dt_txt'] + ": " + i['weather'][0]['description'] + "\n" +
              "velocidad del viento: " + str(i['wind']['speed']) + "\n" +
              "Porcentaje de nubosidad: " + str(i['clouds']['all']) + "%" + "\n" +
              "Temperatura promedio: " + str(i['main']['temp']) + "\n")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    FECHA = Data['list'][0]['dt_txt']
    PRONOSTICO = Data['list'][0]['weather'][0]['description']
    NUBES = Data['list'][0]['clouds']['all']
    WIND_SPEED = Data['list'][0]['wind']['speed']
    TEMP = Data['list'][0]['main']['temp']

    info = open("Registro_clima.txt","w+")

    info.write("Pronostico para " + i['dt_txt'] + ": " + i['weather'][0]['description'] + "\n" +
              "velocidad del viento: " + str(i['wind']['speed']) + "\n" +
              "Porcentaje de nubosidad: " + str(i['clouds']['all']) + "%" + "\n" +
              "Temperatura promedio: " + str(i['main']['temp']) + "\n")
    info.close()

    with pysftp.Connection('192.168.77.44', username='root', password='20150075') as sftp:
        with sftp.cd('proyecto_final'):
            print(sftp.listdir())
            print(sftp.pwd)  # retorna directorio en el que se está trabajando actualmente
            sftp.put(R"C:\Users\Owner\PycharmProjects\Proyecto_final\Registro_clima.txt")  # cargar archivo
            sftp.get('Registro_clima.txt', R"C:\Users\Owner\PycharmProjects\Proyecto_final\Registro_clima.txt")

    if 'lluvia ligera' in PRONOSTICO:
        ARTICULO = 'Paraguas'
    elif 'cielo claro' in PRONOSTICO:
        ARTICULO='protector solar'
    else:
        ARTICULO = 'cepillo de dientes'
     # agrega el nombre de la persona en el mensaje de la plantilla
    mensaje =  message_template.substitute(FECHA = FECHA, PRONOSTICO = PRONOSTICO, NUBES = NUBES, WIND_SPEED = WIND_SPEED, TEMP = TEMP, ARTICULO = ARTICULO)

    # Imprime el mensaje
    # print(mensaje)

    # asigna parámetros al correo
    msj['From'] = MI_CORREO
    msj['To'] = '***Destinatario***'
    msj['Subject'] = "Estado del clima"

    # agrega mensaje al cuerpo del correo
    msj.attach(MIMEText(mensaje,'plain'))

    # envía mensaje usando sesión creada anteriormente
    s.send_message(msj)
    del msj

    # Termina la sesión SMTP y cierra la conexión
    s.quit()


if __name__ == '__main__':
    schedule.every().day.at("20:48:00").do(main)

    while True:
        schedule.run_pending()
        time.sleep(1)
