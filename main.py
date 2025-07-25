# main.py

from token_ring import TokenRingNode

def main():
    # Example: Node 1 in a 3-node ring
    node = TokenRingNode(
        node_id=1,
        my_ip="127.0.0.1",
        my_port=5007,
        ring_table=[1, 2, 3],
        rf_addr=("127.0.0.1", 5006)
    )
    node.start()

if __name__ == "__main__":
    main() 