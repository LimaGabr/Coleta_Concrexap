##################################################IMPORTAÇÕES#################################################
import time
from threading import *
from tkinter import *
from tkinter import messagebox
import mysql.connector
from pycomm3 import LogixDriver
from datetime import date
from datetime import datetime
import traceback
import sys
import pandas as pd
from pystray import MenuItem as item
import pystray
from PIL import Image
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG
from logging import basicConfig
from logging import critical, error, warning, info, debug
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


basicConfig(
    level=WARNING,
    filename='logs.log',
    filemode='a',
    format='%(levelname)s:%(asctime)s:%(message)s'

)

#sys.setrecursionlimit(100)

class Application():

##################################################- THREADINGS -########################################################
    def threading(self):
        self.t1 = Thread(target=self.check)
        self.t1.start()
    def threading2(self):
        self.t2 = Thread(target=self.atualizaDadosCimento)
        self.t2.start()
    def threading3(self):
        self.t2 = Thread(target=self.atualizaDadosAgregado)
        self.t2.start()

##################################################- FUNC JANELA -########################################################
    def quit_window(self, icon, item):
      
        pass
    def show_window(self, icon, item):
        self.icon.stop()
        self.root.after(0, self.root.deiconify)
      
    def withdraw_window(self):
        self.root.withdraw()
        self.image = Image.open("icone_concrexap.ico")
        self.menu = (item('Quit', self.quit_window), item('Show', self.show_window))
        self.icon = pystray.Icon("name", self.image, "Concrexap", self.menu)
        self.icon.run_detached()


    def __init__(self):
#--------------------------------------------------DEFINIÇÕES DA TELA----------------------------------------------
        self.root = Tk()
        self.root.iconbitmap('icone_concrexap.ico')
        self.root.title("Painel de Informações")
        self.root.geometry("380x290")
        self.root.configure(background= 'white')
#--------------------------------------------------BOTÕES---------------------------------------------------------
        self.btnAtualiza = Button(self.root, text="Última Pesagem", command=self.ultimaPesagem)
        self.btnAtualiza.place(x=200, y=25)
        self.btnLimpa = Button(self.root, text=" X ", command=self.limparPesagem)
        self.btnLimpa.place(x=300, y=25, width= 25)
#--------------------------------------------------IMAGEM LOGO RODAPE----------------------------------------------
        self.imgrodape=PhotoImage(file="concrexap1.png")
        self.l_rodape=Label(self.root, image=self.imgrodape)
        self.l_rodape.place(x=87, y=235)
#--------------------------------------------------IMAGEM CHECK CLP----------------------------------------------
        self.img=PhotoImage(file="clperrorfinal.png")
        self.l_logo=Label(self.root)
        self.l_logo.place(x=25, y=20)
#--------------------------------------------------IMAGEM CHECK MYSQL----------------------------------------------
        self.imgok=PhotoImage(file="mysqlerror.png")
        self.l_logook=Label(self.root)
        self.l_logook.place(x=25, y=120)
        self.clp()
        self.threading()
        self.threading2()
        #self.threading3()
#--------------------------------------------------VARIAVEL FUNÇÃO ULTIMA PESAGEM----------------------------------------------
        self.valor = [1]
#--------------------------------------------------INICIALIZA A TELA------------------------------------------------------
        self.root.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.root.mainloop()
##################################################-FUNC IMAGEM-########################################################
    def callback(self):
        self.img2 = PhotoImage(file="clpokfinal.png")
        self.l_logo.configure(image=self.img2)
        self.l_logo.image = self.img2
    def callback2(self):
        self.imgerror = PhotoImage(file="mysqlok.png")
        self.l_logook.configure(image=self.imgerror)
        self.l_logook.image = self.imgerror
    def callback3(self):
        self.img3 = PhotoImage(file="clperrorfinal.png")
        self.l_logo.configure(image=self.img3)
        self.l_logo.image = self.img3
    def callback4(self):
        self.imgerror4 = PhotoImage(file="mysqlerror.png")
        self.l_logook.configure(image=self.imgerror4)
        self.l_logook.image = self.imgerror4


##################################################-CONECTAR CLP-########################################################
    def clp(self):
        time.sleep(2)
        with LogixDriver('192.168.1.245') as self.micro:
            self.peso_blc_01 = self.micro.read('Peso_BA_01')[1]
            self.peso_blc_02 = self.micro.read('Peso_BA_02')[1]
            #self.peso_blc_03 = self.micro.read('Peso_BA_03')[1]
            #self.peso_blc_04 = self.micro.read('Peso_BA_04')[1]

##################################################-CHECK CONEXÃO CLP-########################################################
    def check(self):
        print("conectando CLP...")
        time.sleep(2)
        while True:
            try:
                with LogixDriver('192.168.1.245') as self.micro:
                    self.status_clp = self.micro.connected
                    time.sleep(2)

                if self.status_clp == True:
                    print("conetado")
                    self.callback()
                else:
                    self.callback3()
                    print("fora")
                    error('CLP com error')
                    time.sleep(1)
                    sender_email = "xxxxxxxxx@xxxxxxx.com" #Remetente
                    receiver_email = "xxxxxxxxxx@xxxxxxx.com" #Destinatário
                    password = "xxxxxxxxxxxx" #Password
                    message = MIMEMultipart("alternative")
                    message["Subject"] = "LOG DE ERRO CLP"
                    message["From"] = sender_email
                    message["To"] = receiver_email

                    html = f"""
                                        <html>
                                          <body>
                                            <p>Log de controle Concrexap<br><br><br>

                                            </p>
                                          </body>
                                        </html>
                                        """
                  
                    part2 = MIMEText(html, "html")
                    message.attach(part2)
                    arquivo = "C:\\Local_desejado_para_salvar\\logs.log"
                    attachment = open(arquivo, 'rb')
                    att = MIMEBase('application', 'octet-stream')
                    att.set_payload(attachment.read())
                    encoders.encode_base64(att)
                    att.add_header('Content-Disposition', f'attachment; filename=log.logs')
                    attachment.close()
                    message.attach(att)

                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(sender_email, password)
                        server.sendmail(
                            sender_email, receiver_email, message.as_string()
                        )
                    server.close()
                    time.sleep(5)

            except Exception:
                self.callback3()
                traceback.print_exc()
##################################################-CONECTA BANCO DE DADOS-########################################################
    def conecta(self):
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="",
            database='relatorio_sao_miguel')
        self.cursor = self.conn.cursor()
      
##################################################-GERA LABEL ULTIMA PESAGEM-########################################################
    def ultimaPesagem(self):
        if self.valor == [1]:
            self.conecta()
            self.query = (""" SELECT * FROM balanca_sao_miguel ORDER BY codigo ASC
                                                                """)
            self.df = pd.read_sql(self.query, self.conn)
            self.valor_cimento1 = self.df.iloc[-1]
            self.test = self.valor_cimento1[1:5]
            #self.valor_agregado2 = self.df['agregado'].iloc[-1]
            #self.valor_cimento3 = self.df['cimento_BA_03'].iloc[-1]
            #self.valor_agregado4 = self.df['agregado_BA_04'].iloc[-1]
            #self.valor_data = self.df['data'].iloc[-1]
            self.texto_info = Label(self.root, text="Última Pesagem")
            self.texto_info.place(x=200, y=50)
            #self.texto_data = Label(self.root, text="")
            #self.texto_data.place(x=200, y=75)
            self.texto_cimento1 = Label(self.root, text="")
            self.texto_cimento1.place(x=200, y=100)
            #self.texto_agregado2 = Label(self.root, text="")
            #self.texto_agregado2.place(x=200, y=125)
            #self.texto_cimento3 = Label(self.root, text="")
            #self.texto_cimento3.place(x=200, y=150)
            #self.texto_agregado4 = Label(self.root, text="")
            #self.texto_agregado4.place(x=200, y=175)
            #self.texto_data["text"] = self.valor_data
            self.texto_cimento1["text"] = "->", self.test
            #self.texto_agregado2["text"] = "Agregado: ", self.valor_agregado2
            #self.texto_cimento3["text"] = "Cimento_BA_03: ", self.valor_cimento3
            #self.texto_agregado4["text"] = "Agregado_BA_04: ", self.valor_agregado4
            self.valor.append(1)
            self.conn.close()
            print(self.valor)
##################################################-LIMPA LABEL ÚLTIMA PESAGEM-########################################################
    def limparPesagem(self):
        if self.valor == [1,1]:
            self.valor.remove(1)
            self.texto_info.destroy()
            #self.texto_data.destroy()
            self.texto_cimento1.destroy()
            #self.texto_agregado2.destroy()
            #self.texto_cimento3.destroy()
            #self.texto_agregado4.destroy()
            print(self.valor)
##################################################-COLETA E ADICIONA NO BANCO DE DADOS-########################################################
    def atualizaDadosCimento(self):
        while True:
            try:
                time.sleep(2)
                print("buscando cimento")
                self.conecta()
                self.callback2()
                self.now = datetime.now()
                self.date_time =self.now.strftime("%d/%m/%Y, %H:%M:%S")
                self.nome_balanca = "BA_01"
                self.material = "Cimento"
                with LogixDriver('192.168.1.245') as self.micro: #ip do CLP
                    self.peso_blc_01 = self.micro.read('Peso_BA_01')[1]
                    #self.peso_blc_02 = self.micro.read('Peso_BA_02')[1]
                    #self.peso_blc_03 = self.micro.read('Peso_BA_03')[1]
                    #self.peso_blc_04 = self.micro.read('Peso_BA_04')[1]
                #self.temp_silo_01 = int.from_bytes(self.db[258:260], byteorder='big')
                #self.temp_silo_02 = int.from_bytes(self.db[260:262], byteorder='big')
                    self.sinalBotao1 = self.micro.read('Grava_BA_01')[1]
                    #self.sinalBotao2 = self.micro.read('Grava_BA_02')[1]
                    #self.sinalBotao3 = self.micro.read('Grava_BA_03')[1]
                    #self.sinalBotao4 = self.micro.read('Grava_BA_04')[1]

                if self.sinalBotao1 == True:
                    self.cursor.execute("INSERT INTO balanca_sao_miguel (balanca, material, peso, data) VALUES ('{0}', '{1}', '{2}', '{3}')".format(self.nome_balanca, self.material, self.peso_blc_01, self.date_time))
                    print("gravado com sucesso")
                    self.conn.commit()
                    self.conn.close()
                    self.micro.close()
                    warning('Peso gravado com sucesso!')
                    time.sleep(1)

                    sender_email = "xxxxxxxxxxxxx@gmail.com" #Remetente
                    receiver_email = "xxxxxxxxxx@hotmail.com" #Destino
                    password = "xxxxxxxxx" #Password

                    message = MIMEMultipart("alternative")
                    message["Subject"] = "SUCESSO NA PESAGEM"
                    message["From"] = sender_email
                    message["To"] = receiver_email

                    html = f"""
                                        <html>
                                          <body>
                                            <p>Log de controle Concrexap<br><br><br>

                                            </p>
                                          </body>
                                        </html>
                                        """

                    part2 = MIMEText(html, "html")
                    message.attach(part2)
                    arquivo = "C:\\Local_desejado\\logs.log"
                    attachment = open(arquivo, 'rb')
                    att = MIMEBase('application', 'octet-stream')
                    att.set_payload(attachment.read())
                    encoders.encode_base64(att)
                    att.add_header('Content-Disposition', f'attachment; filename=log.logs')
                    attachment.close()
                    message.attach(att)
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(sender_email, password)
                        server.sendmail(
                            sender_email, receiver_email, message.as_string()
                        )
                    server.close()
                    time.sleep(9)
                  
            except Exception:
                traceback.print_exc()
                self.callback4()
                print("Falha na conexão")
                error('Banco de dados com error')
                time.sleep(1)
                sender_email = "xxxxxxxxxxxxx@gmail.com" #Remetente
                receiver_email = "xxxxxxxxxx@hotmail.com" #Destino
                password = "xxxxxxxxx" #Password

                message = MIMEMultipart("alternative")
                message["Subject"] = "LOG DE ERRO BANCO DE DADOS"
                message["From"] = sender_email
                message["To"] = receiver_email
              
                html = f"""
                    <html>
                      <body>
                        <p>Log de controle Concrexap<br><br><br>

                        </p>
                      </body>
                    </html>
                    """

                part2 = MIMEText(html, "html")
                message.attach(part2)
                arquivo = "C:\\Local_desejado\\logs.log"
                attachment = open(arquivo, 'rb')
                att = MIMEBase('application', 'octet-stream')
                att.set_payload(attachment.read())
                encoders.encode_base64(att)
                att.add_header('Content-Disposition', f'attachment; filename=log.logs')
                attachment.close()
                message.attach(att)
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                    server.login(sender_email, password)
                    server.sendmail(
                        sender_email, receiver_email, message.as_string()
                    )
                server.close()

    def atualizaDadosAgregado(self):
        while True:
            try:
                time.sleep(3)
                print("buscando agregado")
                self.conecta()
                self.callback2()
                self.now = datetime.now()
                self.date_time = self.now.strftime("%d/%m/%Y, %H:%M:%S")
                self.nome_balanca2 = "BA_02"
                self.material2 = "Agregado"
                with LogixDriver('192.168.1.245') as self.micro:
                    #self.peso_blc_01 = self.micro.read('Peso_BA_01')[1]
                    self.peso_blc_02 = self.micro.read('Peso_BA_02')[1]
                    # self.peso_blc_03 = self.micro.read('Peso_BA_03')[1]
                    # self.peso_blc_04 = self.micro.read('Peso_BA_04')[1]
                    # self.temp_silo_01 = int.from_bytes(self.db[258:260], byteorder='big')
                    # self.temp_silo_02 = int.from_bytes(self.db[260:262], byteorder='big')
                    #self.sinalBotao1 = self.micro.read('Grava_BA_01')[1]
                    self.sinalBotao2 = self.micro.read('Grava_BA_02')[1]
                    # self.sinalBotao3 = self.micro.read('Grava_BA_03')[1]
                    # self.sinalBotao4 = self.micro.read('Grava_BA_04')[1]

                if  self.sinalBotao2 == True:
                    self.cursor.execute(
                        "INSERT INTO balanca_sao_miguel (balanca, material, peso, data) VALUES ('{0}', '{1}', '{2}', '{3}')".format(self.nome_balanca2, self.material2, self.peso_blc_02, self.date_time))
                    print("gravado com sucesso")
                    self.conn.commit()
                    self.conn.close()
                    self.micro.close()
                    time.sleep(9)


            except Exception:
                traceback.print_exc()
                self.callback4()
                print("Falha na conexão")
                time.sleep(2)

        #threading.Thread(target=atualizaDados()).start()
        #temp_silo_02 = int.from_bytes(db[260:262], byteorder='big' )
        #print("temp02 = ",temp_silo_02)
        #temp_silo_03 = int.from_bytes(db[262:264], byteorder='big' )
        #print("temp03 = ",temp_silo_03)
        #temp_silo_04 = int.from_bytes(db[264:268], byteorder='big' )
        #print("temp04 = ",temp_silo_04)
##########################################################################################################
if __name__== "__main__":
    Application()
