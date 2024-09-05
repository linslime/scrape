import socket
import pickle
from Config import Config
import multiprocessing
import select


class Data:
    SET = 0
    GET = 1
    DEL = 2
    QUEUE_GET = 3
    QUEUE_PUT = 4
    def __init__(self, function, key, value=None):
        self.function = function
        self.key = key
        self.value = value


class Server:
    def __init__(self):
        self.memory = dict()
        self.queue = dict()

    def start_server_socket(self):
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
                            result = self.__process_data(socket_data)
                            sock.send(result)
                        else:
                            sock.close()
                            connected_clients.remove(sock)
                    except Exception:
                        # 出现异常，也需要关闭 socket 并从 connected_clients 中移除
                        sock.close()
                        connected_clients.remove(sock)

    def __process_data(self, data):
        data = pickle.loads(data)
        result = None
        if data.function == Data.GET:
            result = self.__get_data(data.key)
        elif data.function == Data.SET:
            result = self.__set_data(data.key, data.value)
        elif data.function == Data.DEL:
            result = self.__del_data(data.key)
        elif data.function == Data.QUEUE_GET:
            result = self.__queue_get(data.key)
        elif data.function == Data.QUEUE_PUT:
            self.__queue_put(data.key, data.value)
        result = pickle.dumps(result)
        return result

    def __get_data(self, key):
        result = None
        if key in self.memory.keys():
            result = self.memory[key]
        return result

    def __set_data(self, key, value):
        result = None
        if key in self.memory.keys():
            result = self.memory[key]
        self.memory[key] = value
        return result

    def __del_data(self, key):
        result = None
        if key in self.memory.keys():
            result = self.memory.pop(key)
        return result

    def __queue_get(self, key):
        result = None
        if key in self.queue.keys() and len(self.queue[key]) > 0:
            result = self.queue[key].pop(0)
        return result

    def __queue_put(self, key, value):
        if key not in self.queue.keys():
            self.queue[key] = list()
        self.queue[key].append(value)


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
    client.close()


if __name__ == '__main__':
    server = Server()
    process = multiprocessing.Process(target=server.start_server_socket, args=())
    process.start()

    processes = list()
    for i in range(10):
        process = multiprocessing.Process(target=start_client_socket, args=())
        processes.append(process)
    for process in processes:
        process.start()

    for process in processes:
        process.join()
