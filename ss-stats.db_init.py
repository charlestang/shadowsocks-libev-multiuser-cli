import sqlite3
from socket import inet_aton
from struct import unpack

if __name__ == "__main__":
    conn = sqlite3.connect("ss-stats.db")
    cur = conn.cursor()

    cur.execute(
        """CREATE TABLE IF NOT EXISTS account (
                        id INTEGER PRIMARY KEY ASC,
                        nickname VARCHAR(32) UNIQUE NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
    )

    cur.execute(
        """INSERT INTO account(nickname) VALUES ('charles'), ('tang335'), ('liaojing')
                        ON CONFLICT DO NOTHING"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS server (
                        id INTEGER PRIMARY KEY ASC,
                        account_id INTEGER NOT NULL,
                        ip BIGINT NOT NULL,
                        port INTEGER NOT NULL,
                        valid BOOLEAN NOT NULL DEFAULT 1,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
    )

    cur.execute("""SELECT * from server""")
    if not cur.fetchone():
        ip2long = unpack("!L", inet_aton("47.52.43.114"))[0]
        servers = [(1, ip2long, 18081), (2, ip2long, 18082), (3, ip2long, 18083)]
        cur.executemany(
            """INSERT INTO server(account_id, ip, port) VALUES
                            (?, ?, ?)""",
            servers,
        )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS waterlog (
                        id INTEGER PRIMARY KEY ASC,
                        server_id INTEGER NOT NULL,
                        pid INTEGER NOT NULL,
                        pid_created_at DATETIME NOT NULL,
                        total_traffic BIGINT NOT NULL,
                        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP)"""
    )
    conn.commit()
    conn.close()
