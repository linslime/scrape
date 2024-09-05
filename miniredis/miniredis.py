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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 使用UDP方式传输
    server.bind((ip, port))  # 绑定IP与端口
    server.listen(200)
    # 将 server_socket 设置为非阻塞模式
    server.setblocking(False)
    # 存储已连接的 client_socket
    connected_clients = []
    # 不断循环，接受客户端发来的消息
    while True:
        # 使用 select 函数监听所有连接的 client_socket
        readable_sockets, _, _ = select.select([server] + connected_clients, [], [])
        # 处理所有可读的 socket
        for sock in readable_sockets:
            # 如果是 server_socket 表示有新的连接
            if sock is server:
                client_socket, client_address = server.accept()
                connected_clients.append(client_socket)
                # 否则是已连接的 client_socket，需要处理收到的数据
            else:
                try:
                    socket_data = sock.recv(Config.BUFFER_SIZE)
                    if socket_data:
                        # print(socket_data)
                        result = process_data(socket_data)
                        sock.send(result)
                    else:
                        sock.close()
                        connected_clients.remove(sock)
                        print("Connection closed")
                except Exception as e:
                    # 出现异常，也需要关闭 socket 并从 connected_clients 中移除
                    print(f"Error occurred while receiving data from {sock.getpeername()}: {e}")
                    sock.close()
                    connected_clients.remove(sock)


def start_client_socket():
    """
    启动客户端UDP Socket
    :return:
    """
    ip, port = Config.SOCKET_IP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 使用TCP方式传输
    client.connect((ip, port))  # 连接远程服务端
    data = [i for i in range(10000)]
    data = pickle.dumps(data)
    # 与服务端交互
    for i in range(1000):
        client.sendto(data, Config.SOCKET_IP)  # 使用sendto发送UDP消息，address填入服务端IP和端口
        socket_data = client.recv(Config.BUFFER_SIZE)
        if socket_data != data:
            print("出错了")
    client.close()
    print("success")


def process_data(data):
    return data


if __name__ == '__main__':
    process = multiprocessing.Process(target=start_server_socket, args=())
    process.start()

    processes = list()
    for i in range(100):
        process = multiprocessing.Process(target=start_client_socket, args=())
        processes.append(process)
    for process in processes:
        process.start()

    for process in processes:
        process.join()
