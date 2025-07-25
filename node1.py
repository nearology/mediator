from token_ring import TokenRingNode

def main():
    node = TokenRingNode(
        node_id=1,
        my_ip="127.0.0.1",
        my_port=5001,
        ring_table=[1, 2, 3],
        rf_addr=("127.0.0.1", 5002)
    )
    node.start()

if __name__ == "__main__":
    main() 