# token_ring.py

import threading
import time
import csv
import os
from typing import List, Tuple, Optional
from config import TOKEN_HOLD_MIN, TOKEN_TIMEOUT, DEBUG_MODE, VERBOSITY_LEVEL
from utils import (
    pack_data_header, pack_data_chunk, pack_data_end, pack_token,
    unpack_token, unpack_data_header, unpack_data_chunk, unpack_data_end,
    DATA_HEADER, DATA_CHUNK, DATA_END, DATA_CHUNK_SIZE
)
from network import create_udp_socket, send_udp
from models import DataReceive

class TokenRingNode:
    """A single participant in the token ring."""

    def __init__(
        self,
        node_id: int,
        my_ip: str,
        my_port: int,
        ring_table: List[int],
        rf_addr: Tuple[str, int],
    ) -> None:
        self.id = node_id
        self.ip = my_ip
        self.port = my_port
        self.ring_table = sorted(ring_table)
        self.rf_addr = rf_addr

        self.token_event = threading.Event()
        self.last_seq_seen = {}
        self.last_token_time = time.time()
        self.my_seq = 0
        self.is_token_origin = (self.id == min(self.ring_table))
        self.sock = create_udp_socket(self.ip, self.port)
        self.data_recv: Optional[DataReceive] = None

        self.log_file = f"node{self.id}_log.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "event", "details"])

    def log_csv(self, event: str, details: str):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event, details])

    def _debug_log(self, message: str) -> None:
        if DEBUG_MODE:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[DEBUG {timestamp}] Node{self.id}: {message}")

    def _log(self, message: str, level: int = 2) -> None:
        if VERBOSITY_LEVEL >= level:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Node{self.id}: {message}")

    def _receiver(self) -> None:
        self._debug_log("_receiver thread started")
        while True:
            try:
                data, addr = self.sock.recvfrom(8)
                self._debug_log(f"received {len(data)} bytes from {addr}")
                if len(data) != 8:
                    self._debug_log(f"invalid message length: {len(data)}")
                    continue
                token = unpack_token(data)
                if data[0] in [DATA_HEADER, DATA_CHUNK, DATA_END]:
                    self._handle_data_message(data)
                    continue
                if token["type"] != "TOKEN":
                    self._debug_log(f"unknown message type: {token['type']}")
                    continue
                self._process_token(token)
            except Exception as e:
                self._debug_log(f"_receiver error: {e}")
                continue

    def _handle_data_message(self, msg: bytes):
        msg_type = msg[0]
        origin = msg[1]
        if origin == self.id:
            self._debug_log("Ignoring my own DATA message")
            return
        if msg_type == DATA_HEADER:
            header = unpack_data_header(msg)
            if VERBOSITY_LEVEL == 1:
                self.data_recv = DataReceive(
                    origin=header["origin"],
                    seq=header["seq"],
                    dst=header["dst"],
                    length=header["total_len"],
                    chunks=[]
                )
            else:
                self._log(f"Received DATA_HEADER from Node{header['origin']} (seq={header['seq']}), DLEN={header['total_len']}", level=2)
                self.data_recv = DataReceive(
                    origin=header["origin"],
                    seq=header["seq"],
                    dst=header["dst"],
                    length=header["total_len"],
                    chunks=[]
                )
        elif msg_type == DATA_CHUNK:
            chunk = unpack_data_chunk(msg)
            if self.data_recv:
                self.data_recv.chunks.append(chunk["data"])
        elif msg_type == DATA_END:
            end = unpack_data_end(msg)
            if self.data_recv:
                d = self.data_recv
                payload = b''.join(d.chunks)[:d.length]
                self.log_csv("DATA_RECEIVED", f"from Node{d.origin} to Node{d.dst} data={payload!r}")
                if VERBOSITY_LEVEL == 1:
                    print(f"Data received: from Node{d.origin} to Node{d.dst} : {payload!r}")
                else:
                    self._log("Received DATA_END!", level=2)
                    self._log(f"==> Data received from Node{d.origin}, Seq={d.seq} : {payload!r}", level=2)
            self.data_recv = None

    def _process_token(self, token: dict) -> None:
        origin = token["origin"]
        seq = token["seq"]
        dst = token["dst"]
        self._debug_log(f"processing token: origin={origin}, seq={seq}, dst={dst}")
        if origin == self.id:
            self._debug_log(f"ignoring my own token: origin={origin}")
            return
        last_seq = self.last_seq_seen.get(origin, -1)
        if seq <= last_seq:
            self._debug_log(f"dropping old/duplicate token: seq={seq} <= last_seen={last_seq}")
            return
        self.last_seq_seen[origin] = seq
        self.last_token_time = time.time()
        self._log(f"TOKEN seq={seq} origin={origin} dst={dst} received")
        if dst == self.id:
            self._debug_log("token is for me, setting event")
            self.log_csv("TOKEN_RECEIVED", f"seq={seq} from Node{origin}")
            self.token_event.set()

    def _logic(self) -> None:
        self._debug_log("_logic thread started")
        if self.is_token_origin:
            self._debug_log("I am token origin, creating initial token after delay")
            time.sleep(2.0)
            self._create_token()
        while True:
            self._debug_log("waiting for token...")
            got_token = self.token_event.wait(timeout=0.1)
            if got_token:
                self._debug_log("received token event")
                self.token_event.clear()
                self._handle_my_token()
            else:
                if self.is_token_origin:
                    time_since_last = time.time() - self.last_token_time
                    if time_since_last > TOKEN_TIMEOUT:
                        self._debug_log(f"token timeout ({time_since_last:.1f}s), regenerating")
                        self._create_token()

    def broadcast_data(self, data: bytes):
        for node_id in self.ring_table:
            if node_id != self.id:
                self.send_data(dst=node_id, data=data)

    def _handle_my_token(self) -> None:
        self._debug_log("handling my token")
        time.sleep(TOKEN_HOLD_MIN)
        if self.id == 1:
            self.send_data(dst=2, data=b'Hello Node2')
            self.send_data(dst=3, data=b'Hello Node3')
        self._forward_token()

    def _forward_token(self) -> None:
        next_node = self._get_successor()
        self.my_seq += 1
        self._debug_log(f"forwarding token to node {next_node} with seq {self.my_seq}")
        token_data = pack_token(self.id, self.my_seq, next_node)
        send_udp(self.sock, token_data, self.rf_addr)
        self.log_csv("TOKEN_SENT", f"seq={self.my_seq} to Node{next_node}")
        self._log(f"TOKEN forwarded to node{next_node} (seq={self.my_seq})")

    def _create_token(self) -> None:
        if not self.is_token_origin:
            self._debug_log("not token origin, cannot create token")
            return
        next_node = self._get_successor()
        self.my_seq += 1
        self._debug_log(f"creating new token for node {next_node} with seq {self.my_seq}")
        token_data = pack_token(self.id, self.my_seq, next_node)
        send_udp(self.sock, token_data, self.rf_addr)
        self.last_token_time = time.time()
        self.log_csv("TOKEN_SENT", f"seq={self.my_seq} to Node{next_node}")
        self._log(f"TOKEN created for node{next_node} (seq={self.my_seq})")

    def send_data(self, dst: int, data: bytes):
        seq = (self.my_seq + 1)
        origin = self.id
        total_len = len(data)
        self.log_csv("DATA_SENT", f"to Node{dst} seq={seq} data={data!r}")
        self._log(f"Sending {total_len} bytes data to Node{dst}")
        header = pack_data_header(origin, seq, dst, total_len)
        send_udp(self.sock, header, self.rf_addr)
        for i in range(0, total_len, DATA_CHUNK_SIZE):
            chunk = data[i:i+DATA_CHUNK_SIZE]
            chunk_msg = pack_data_chunk(chunk)
            send_udp(self.sock, chunk_msg, self.rf_addr)
        end_msg = pack_data_end(origin, seq, dst)
        send_udp(self.sock, end_msg, self.rf_addr)
        self._log(f"Data transmission finished (seq={seq})")

    def _get_successor(self) -> int:
        try:
            idx = self.ring_table.index(self.id)
            successor = self.ring_table[(idx + 1) % len(self.ring_table)]
            self._debug_log(f"successor of node {self.id} is node {successor}")
            return successor
        except ValueError:
            self._debug_log(f"node {self.id} not found in ring table")
            return self.ring_table[0]

    def start(self) -> None:
        self._debug_log("starting node threads")
        receiver_thread = threading.Thread(target=self._receiver, daemon=True)
        receiver_thread.start()
        self._debug_log("receiver thread started")
        logic_thread = threading.Thread(target=self._logic, daemon=True)
        logic_thread.start()
        self._debug_log("logic thread started")
        self._log("Node started – press Ctrl-C to quit")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._log("Shutting down...") 