import requests
import time


class BlockchainClient:
    def __init__(self, user_client, node_url="http://localhost:5000"):
        self.user = user_client
        self.node_url = node_url

    def write_data(self, data, read_access=None, write_access=None):
        payload = {
            "data": data,
            "public_key": self.user.get_public_key_str(),
            "read_access": read_access or [self.user.get_public_key_str()],
            "write_access": write_access or [self.user.get_public_key_str()]
        }

        try:
            response = requests.post(
                f"{self.node_url}/add",
                json=payload
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Node unavailable"}

    def read_chain(self):
        try:
            response = requests.get(
                f"{self.node_url}/chain",
                params={"public_key": self.user.get_public_key_str()}
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Node unavailable"}


def main_loop(username):
    from user_client import UserClient
    user = UserClient(username)
    client = BlockchainClient(user)

    while True:
        print("\n1. Write to blockchain")
        print("2. Read blockchain")
        print("3. Exit")
        choice = input("Choose operation: ")

        if choice == '1':
            data = input("Enter data: ")
            read_access = input("Read access (comma-separated public keys): ").split(',')
            write_access = input("Write access (comma-separated public keys): ").split(',')
            result = client.write_data(data, read_access, write_access)
            print("Result:", result)

        elif choice == '2':
            chain = client.read_chain()
            print("\nAuthorized Blocks:")
            for block in chain:
                print(f"Block {block['index']}: {block['data']}")

        elif choice == '3':
            break

        time.sleep(1)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python client_ops.py [username]")
        sys.exit(1)
    main_loop(sys.argv[1])