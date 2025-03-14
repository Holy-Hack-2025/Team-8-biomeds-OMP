import csv
import datetime


class Ledger:
    def __init__(self, filename='ledger.csv'):
        self.filename = filename
        # Create the CSV file with header if it doesn't exist
        try:
            with open(self.filename, mode='r') as file:
                pass  # file exists
        except FileNotFoundError:
            self.create_ledger()

    def create_ledger(self):
        with open(self.filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['timestamp', 'account', 'description', 'amount'])

    def add_transaction(self, account, description, amount):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, account, description, amount])

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
    

    def print_ledger(self):
        transactions = self.get_transactions()
        for transaction in transactions:
            print(f"{transaction[0]} | {transaction[1]} | {transaction[2]} | {transaction[3]}")


# Example usage
ledger = Ledger()
ledger.add_transaction('Account 1', 'Payment Received', 1000)
ledger.add_transaction('Account 2', 'Payment Sent', -500)
ledger.get_transactions('Account 1')
ledger.print_ledger()