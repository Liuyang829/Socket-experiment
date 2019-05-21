from tkinter import *
from socket import *
from threading import Thread
from json import *


class ServerSocket():
    def __init__(self):
        self.root = Tk()
        self.root.title("Socket_Server")
        self.root.resizable(0, 0)
        self.topframe = Frame(self.root)
        self.topframe.pack()
        self.window = Frame(self.root)
        self.window.pack()
        self.sendbox = Frame(self.root, height=100)
        self.sendbox.pack()
        self.label = Label(self.topframe, width=50, height=2, font=10, compound="left",text=("IP:" + HOST + "   " + "PORT:" + str(PORT)))
        self.label.pack(side=LEFT)
        self.close_button = Button(self.topframe, text="关闭", command=self.close, compound="right", font=10, width=8)
        self.close_button.pack(padx=5, pady=5, side=RIGHT)

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

    def dosend(self):
        self.text = self.message_box.get()
        self.message_box.delete(0, END)
        senddata = {"op": "message", "text": self.text}
        for i in currentsocket.keys():
            i.sendall(dumps(senddata).encode("utf-8"))


    def print(self,text):
        self.screenbox.insert(END, text)

    def close(self):
        # data = {"op": "exit"}
        # s.sendall(dumps(data).encode("utf-8"))
        s.close()
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()

def Create_GUI():
    global Server
    Server = ServerSocket()
    Server.mainloop()

    # 创建SOCKET
def Create_Socket():
    while True:
        clientsocket, clientaddress = s.accept()
        t = Thread(target=TCP, args=(clientsocket, clientaddress))
        t.start()

def TCP(clientsocket, clientaddress):
    while True:
        try:
            # 获取客户端消息
            data = loads(clientsocket.recv(BUFFSIZE).decode("utf-8"))
            # 登录判断
            if data["op"] == "login":
                if data["username"] in user and user[data["username"]] == data["password"]:
                    currentuser[data["username"]] = clientsocket
                    currentsocket[clientsocket] = data["username"]
                    senddata = {"op":"login_result", "username":data["username"], "password":data["password"],
                                "result":"success"}
                    clientsocket.sendall(dumps(senddata).encode("utf-8"))
                    # Server.combox_refresh()
                    Server.print("用户 < " + data["username"] + " > 登录成功 ---> 建立连接\n")
                else:
                    senddata = {"op": "login_result", "username": data["username"], "password": data["password"],
                                "result": "failure"}
                    clientsocket.sendall(dumps(senddata).encode("utf-8"))
                    Server.print("用户 < " + data["username"] + " > 登录失败\n")
            # 接受客户端信息处理
            elif data["op"] == "message":
                if(clientsocket in currentsocket.keys()):
                    Server.print(currentsocket[clientsocket] + " >>> "+ HOST +": "+data["text"] + "\n")
                    senddata = {"op":"send_result", "text":data["text"], "result":"success"}
                    clientsocket.sendall(dumps(senddata).encode("utf-8"))
                else:
                    Server.print("有用户未登录 尝试发送消息\n")
                    senddata = {"op":"send_result", "text":data["text"], "result":"failure"}
                    clientsocket.sendall(dumps(senddata).encode("utf-8"))
            # 服务端发送消息，客户端回应确认消息处理
            elif data["op"] == "send_result":
                if data["result"] == "success":
                    Server.print(HOST+" >>> "+ currentsocket[clientsocket] +": "+data["text"] + "\n")
            # 客户端关闭连接处理
            elif data["op"] == "exit":
                Server.print("用户 < " + currentsocket[clientsocket] + " > 退出连接\n")
                currentuser.pop(currentsocket[clientsocket])
                currentsocket.pop(clientsocket)
                clientsocket.close()
        except:
            pass

if __name__ == "__main__":
    # HOST——服务端地址 PORT——交互端口 clientsocketBUFFSIZE——最大传输量 user——用户-密码字典 currentuser——用户-socket线程字典
    # currentsocket socket线程-用户字典
    HOST = "127.0.0.1"
    PORT = 8801
    BUFFSIZE = 1024
    user = {"AAA": "aaa", "BBB": "bbb", "CCC": "ccc"}
    currentuser = {}
    currentsocket = {}
    # user_choose=""
    # 创建SOCKET连接，绑定IP和端口
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    # 开启GUI线程和SOCKET线程
    Socket_thread = Thread(target=Create_Socket, args=(), name='SOCKET')
    GUI_thread = Thread(target=Create_GUI, args=(), name='GUI')
    Socket_thread.start()
    GUI_thread.start()
