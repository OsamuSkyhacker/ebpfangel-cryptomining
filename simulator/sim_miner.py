import os
import time
import hashlib
import socket

LOG_PATH = "/tmp/ebpfangel_miner.log"


def cpu_work(rounds: int = 50000):
    # 模拟挖矿的哈希计算
    data = os.urandom(32)
    for _ in range(rounds):
        data = hashlib.sha256(data).digest()

def disk_work():
    # 模拟挖矿程序写日志 / 配置文件
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "ab") as f:
        for _ in range(50):
            f.write(os.urandom(512))
        f.flush()

def net_work():
    # 模拟和矿池保持长连接（这里连本地，不出网）
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 尝试连一个本地端口，连不上也没关系，只是制造系统调用
        s.settimeout(0.5)
        s.connect(("127.0.0.1", 65530))
        for _ in range(10):
            s.sendall(b"x" * 1024)
            time.sleep(0.1)
    except OSError:
        # 连接失败无所谓，我们只是要触发 connect/send 系统调用
        pass
    finally:
        try:
            s.close()
        except Exception:
            pass

def main():
    print("Simulated miner started. Press Ctrl+C to stop.")
    while True:
        cpu_work()
        disk_work()
        net_work()
        # 稍微喘口气，避免把服务器打满
        time.sleep(0.2)

if __name__ == "__main__":
    main()
