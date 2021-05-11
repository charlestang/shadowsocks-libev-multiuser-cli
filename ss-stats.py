import argparse
import json
import os
import re
import socket
import sqlite3
import sys
from datetime import datetime
from typing import List

import psutil
from psutil._common import sconn


def get_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ss-manager and ss-server maintain script."
    )
    parser.add_argument(
        "config_file", metavar="<config_path>", help="ss-manager' config file path."
    )
    return parser


def get_processes_by_name(name: str) -> List[psutil.Process]:
    """
    根据进程名，获取进程列表
    """
    res = []
    for proc in psutil.process_iter(["pid", "name", "create_time"]):
        if proc.info["name"] == name:
            res.append(proc)
    return res


def get_conns_by_pids(pids: List[int]) -> List[sconn]:
    conns = psutil.net_connections()
    res = []
    for c in conns:
        if c.pid in pids:
            res.append(c)
    return res


def ss_servers():
    conns = psutil.net_connections()
    for c in conns:
        print(c.fd, c.family, c.type, c.laddr, c.raddr, c.status, c.pid)
        print(c)


if __name__ == "__main__":
    # 参数解析
    parser = get_argparser()
    args = parser.parse_args()

    # 配置文件解析
    configs = json.load(open(args.config_file, "r"))

    # ss-manager 查活，否则清理，先清理ss-server，然后清理ss-manager，最后重启ss-manager
    managers = get_processes_by_name("ss-manager")
    retry = 0
    while len(managers) != 1 and retry < 3:
        os.system("systemctl restart shadowsocks-libev.service")
        retry += 1
        managers = get_processes_by_name("ss-manager")
    if len(managers) != 1:
        print("fatal error, 3 times retried and no ss-manager started")
        sys.exit(1)
    pid = managers[0].info["pid"]
    create_time = datetime.fromtimestamp(
        round(managers[0].info["create_time"], 0)
    ).strftime("%Y-%m-%d %H:%M:%S")

    conns = get_conns_by_pids([x.info["pid"] for x in managers])
    ip = conns[0].laddr[0]
    port = conns[0].laddr[1]

    # 获取统计，插入数据库
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto("ping".encode(), ("127.0.0.1", 55092))
    data = udp_socket.recvfrom(1024)
    match = re.match(rb"^\w+:\s*(.*)", data[0])
    udp_socket.close()

    # 打开数据库
    conn = sqlite3.connect("/root/softwares/ss-stats.db")
    cur = conn.cursor()

    cur.execute("""SELECT id, port FROM SERVER""")
    servers = {k: v for v, k in cur.fetchall()}

    json_data = json.loads(match[1])
    print(pid, create_time)
    records = []
    for (k, v) in json_data.items():
        server_id = servers[int(k)]
        record = (server_id, pid, create_time, v)
        print(record)
        records.append(record)

    for r in records:
        cur.execute(
            """SELECT COUNT(1) FROM waterlog
                        WHERE server_id = ? AND pid = ? AND pid_created_at = ? AND total_traffic = ?""",
            r,
        )
        cnt = cur.fetchone()[0]
        if cnt == 0:
            print(r)
            res = cur.execute(
                """INSERT INTO waterlog (server_id, pid, pid_created_at, total_traffic)
                            VALUES (?, ?, ?, ?)""",
                r,
            )
            print("insert result: ", res)

    conn.commit()
    conn.close()

    if datetime.fromisoformat(create_time).date() < datetime.today().date():
        os.system("systemctl restart shadowsocks-libev.service")

    # ss-server 查活，否则，按照配置添加 ss-server
    servers = get_processes_by_name("ss-server")
    print(servers, json_data)
    retry = 0
    if len(servers) < len(json_data) and retry < 3:
        os.system("systemctl restart shadowsocks-libev.service")
        retry += 1
        servers = get_processes_by_name("ss-server")

    if len(servers) < len(json_data):
        print("fatal error: ss-server's number is less than config")
