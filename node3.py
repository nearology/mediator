from token_ring import TokenRingNode

def main():
    node = TokenRingNode(
        node_id=3,
        my_ip="127.0.0.1",
        my_port=5003,
        ring_table=[1, 2, 3],
        rf_addr=("127.0.0.1", 5001)
    )
    node.start()

if __name__ == "__main__":
    main() 