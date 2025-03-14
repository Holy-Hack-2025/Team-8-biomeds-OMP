import csv
import datetime
import os

class Ledger:
    def __init__(self, filename='ledger.csv'):
        # Extract the base name from the input filename (without extension)
        base_filename = os.path.splitext(filename)[0]

        # Create new filenames based on the base name
        self.data_filename = f"{base_filename}_Data.csv"
        self.contracts_filename = f"{base_filename}_Contracts.csv"
        # Create the CSV file with header if it doesn't exist
        try:
            with open(self.data_filename, mode='r') as file:
                self.clear_csv(self.data_filename)  # file exists
        except FileNotFoundError:
            self.create_ledger('data')
        # Create the CSV file with header if it doesn't exist
        try:
            with open(self.contracts_filename, mode='r') as file:
                self.clear_csv(self.contracts_filename)  # file exists
        except FileNotFoundError:
            self.create_ledger('contracts')

    def clear_csv(self,filename):
        # write mode ('w') to clear its contents
        with open(filename, mode='r', newline='') as file:
            # Read the first line (header)
            header = file.readline()

        # Open the file in write mode to clear its content
        with open(filename, mode='w', newline='') as file:
            # Write the header back to the file
            file.write(header)

    def create_ledger(self, key ):
        match key:
            case "data":
                filename = self.data_filename
                header = ['timestamp', 'labels', 'account', 'parameter', 'amount']
            case "contracts":
                filename = self.contracts_filename
                header = ['timestamp', 'labels', 'Supplier', 'Receiver' 'amount', 'Priority']
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def add_transaction(self, account, description, amount):
        labels = set(account)
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, labels, account, description, amount])

    def get_transactions(self, account=None, min_amount=None, max_amount=None):
            transactions = []
            with open(self.filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    timestamp, acc, description, amount = row
                    amount = float(amount)  # Convert amount to a float
                    if account and acc != account:
                        continue  # Skip if the account does not match
                    if min_amount is not None and amount < min_amount:
                        continue  # Skip if the amount is less than the minimum
                    if max_amount is not None and amount > max_amount:
                        continue  # Skip if the amount is greater than the maximum
                    transactions.append(row)
            return transactions

    def add_contract(self, account1, account2, amount_materials):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, account, description, amount])


    def print_ledger(self):
        transactions = self.get_transactions()
        for transaction in transactions:
            print(f"{transaction[0]} | {transaction[1]} | {transaction[2]} | {transaction[3]}")


# Example usage
ledger = Ledger()
# ledger.add_transaction('Account 1', 'Payment Received', 1000)
# ledger.add_transaction('Account 2', 'Payment Sent', -500)
# print(ledger.get_transactions('Account 1'))
#ledger.print_ledger()