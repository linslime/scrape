import socket
import pickle
from Config import Config
import multiprocessing
import select


def start_server_socket():
    """
    启动服务端UDP Socket
    :return:
    """
    ip, port = Config.SOCKET_IP
    server = socket.socket(type=socket.SOCK_DGRAM)  # 使用UDP方式传输
    server.bind((ip, port))  # 绑定IP与端口

    # 不断循环，接受客户端发来的消息
    while True:
        socket_data, address = server.recvfrom(Config.BUFFER_SIZE)
        result = socket_data
        server.sendto(result, address)


def start_client_socket():
    """
    启动客户端UDP Socket
    :return:
    """
    ip, port = Config.SOCKET_IP
    client = socket.socket(type=socket.SOCK_DGRAM)  # 使用TCP方式传输
    client.connect((ip, port))  # 连接远程服务端
    data = [i for i in range(10000)]
    data = pickle.dumps(data)
    # 与服务端交互
    for i in range(10000):
        client.sendto(data, Config.SOCKET_IP)  # 使用sendto发送UDP消息，address填入服务端IP和端口
        socket_data, address = client.recvfrom(Config.BUFFER_SIZE)
        if socket_data != data:
            print("出错了")
    print("success")


if __name__ == '__main__':
    processes = list()

    process = multiprocessing.Process(target=start_server_socket, args=())
    # processes.append(process)
    process.start()

    for i in range(1):
        process = multiprocessing.Process(target=start_client_socket, args=())
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
    # start_server_socket()
