# NOTE: Not being used



# daemon.py

import os
import signal
import socket
import sqlite3
import json
import subprocess
import time

DB_FILE = "jobs.db"
os.makedirs("/tmp/nyun", exist_ok=True)
SOCKET_FILE = "/tmp/nyun/job_manager.sock"

class DaemonProcess:
    def __init__(self):
        self.db_connection = sqlite3.connect(DB_FILE)
        self.setup_database()
        self.setup_ipc()

    def setup_database(self):
        cursor = self.db_connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY, name TEXT, command TEXT, status TEXT)")
        self.db_connection.commit()

    def setup_ipc(self):
        if os.path.exists(SOCKET_FILE):
            os.remove(SOCKET_FILE)

        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(SOCKET_FILE)
        self.sock.listen(1)

    def handle_client(self, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = json.loads(data.decode())
            if message["command"] == "add":
                self.add_job(message["name"], message["command"])
            elif message["command"] == "list":
                self.list_jobs(conn)
            elif message["command"] == "delete":
                self.delete_job(message["id"])
            else:
                conn.sendall(b"Invalid command")
        conn.close()

    def add_job(self, name, command):
        cursor = self.db_connection.cursor()
        cursor.execute("INSERT INTO jobs (name, command, status) VALUES (?, ?, ?)", (name, command, "pending"))
        self.db_connection.commit()

    def list_jobs(self, conn):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM jobs")
        jobs = cursor.fetchall()
        conn.sendall(json.dumps(jobs).encode())

    def delete_job(self, job_id):
        cursor = self.db_connection.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        self.db_connection.commit()

    def start(self):
        while True:
            conn, _ = self.sock.accept()
            pid = os.fork()
            if pid == 0:
                self.handle_client(conn)
                os._exit(0)
            else:
                conn.close()


def main():
    daemon = DaemonProcess()
    daemon.start()

if __name__ == "__main__":
    main()
