from tkinter import *
from socket import *
from threading import Thread
from json import *

class ClientSocket():
    def __init__(self):
        self.root=Tk()
        self.root.title("Socket_Client")
        self.root.resizable(0,0)
        self.topframe=Frame(self.root)
        self.topframe.pack()
        self.window=Frame(self.root,height=300,width=300)
        self.window.pack()
        self.sendbox = Frame(self.root, height=100)
        self.sendbox.pack()
        self.username_word = Label(self.topframe, text=" 用户名：", font=10, width=8)
        self.username_word.pack(padx=5, pady=5, side=LEFT)
        self.usernamebox = Entry(self.topframe, text="username", font=10, width=10)
        self.usernamebox.pack(padx=5, pady=5, side=LEFT)
        self.password_word = Label(self.topframe, text="密码：", font=10, width=5)
        self.password_word.pack(padx=5, pady=5, side=LEFT)
        self.passwordbox = Entry(self.topframe, text="password", show="*",font=10, width=10)
        self.passwordbox.pack(padx=5, pady=5, side=LEFT)
        self.login_button = Button(self.topframe, text="登录", command=self.login, compound="center", font=10, width=10)
        self.login_button.pack(padx=5, pady=5, side=LEFT)
        self.login_button = Button(self.topframe, text="退出连接", command=self.exit, compound="center", font=10, width=10)
        self.login_button.pack(padx=5, pady=5, side=LEFT)

        self.rightbar = Scrollbar(self.window, orient=VERTICAL)
        self.screenbox = Text(self.window, xscrollcommand=self.rightbar.set, width=65, font=10)
        self.screenbox.bind("<KeyPress>", lambda op: "break")
        self.screenbox.state = 'readonly'
        self.rightbar.pack(expand=1, side=RIGHT, fill=Y)
        self.screenbox.pack(expand=1, side=LEFT, fill=BOTH)
        self.rightbar.config(command=self.screenbox.yview)

        self.message_box = Entry(self.sendbox, text="message", font=10, width=50)
        self.message_box.pack(padx=10, pady=5, side=LEFT)
        self.send_button = Button(self.sendbox, text="发送", command=self.dosend, compound="center", font=10, width=10)
        self.send_button.pack(padx=5, pady=5, side=RIGHT)
    # 登陆
    def login(self):
        data = {"op":"login", "username":Client.usernamebox.get(), "password":Client.passwordbox.get()}
        s.send(dumps(data).encode("utf-8"))

    def print(self,text):
        self.screenbox.insert(END, text)

    def exit(self):
        data = {"op":"exit"}
        s.send(dumps(data).encode("utf-8"))
        s.close()
        self.root.destroy()

    def dosend(self):
        self.text = self.message_box.get()
        self.message_box.delete(0, END)
        data = {"op":"message", "text":self.text}
        s.send(dumps(data).encode("utf-8"))

    def mainloop(self):
        self.root.mainloop()

def Create_GUI():
    global Client
    Client = ClientSocket()
    Client.mainloop()

def Create_Socket():
    while True:
        try:
            # 获取服务端消息
            data=loads(s.recv(BUFFSIZE).decode("utf-8"))
            # 登录成功与否返回消息处理
            if data["op"] == "login_result":
                if data["result"] == "success":
                    Client.print(" < " + HOST + " > " + "连接成功\n")
                elif data["result"] == "failure":
                    Client.print(" < " + HOST + " > " + "连接失败  用户名或密码错误\n")
            # 从服务端接受信息处理
            elif data["op"] == "message":
                Client.print(HOST + " >>> " +Client.usernamebox.get()+ ": "+data["text"] + '\n')
                senddata={"op":"send_result", "text":data["text"], "result":"success"}
                s.send(dumps(senddata).encode("utf-8"))
            # 客户端发送消息，服务端回应确认消息处理
            elif data["op"] == "send_result":
                if data["result"] == "success":
                    Client.print(Client.usernamebox.get()+" >>> " + HOST + ": "+ data["text"] + '\n')
                else:
                    Client.print(" 发送失败，请先登录\n")
            elif data["op"] == "exit":
                Client.print("服务器已断开连接\n")
        except:
            pass

if __name__ == "__main__":
    # HOST——服务端地址 PORT——交互端口 BUFFSIZE——最大传输量
    HOST = "127.0.0.1"
    PORT = 8801
    BUFFSIZE = 1024
    # 创建SOCKET连接，绑定IP和端口
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((HOST, PORT))
    # 开启GUI线程和SOCKET线程
    GUI_thread = Thread(target=Create_GUI, args=(), name='GUI')
    Socket_thread = Thread(target=Create_Socket, args=(), name='SOCKET')
    Socket_thread.start()
    GUI_thread.start()