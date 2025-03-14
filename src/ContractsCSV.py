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

        # Create or reset data file
        try:
            with open(self.data_filename, mode='r') as file:
                self.clear_csv(self.data_filename)  # file exists
        except FileNotFoundError:
            pass
        self.create_ledger('data')

        # Create or reset contracts file
        try:
            with open(self.contracts_filename, mode='r') as file:
                self.clear_csv(self.contracts_filename)  # file exists
        except FileNotFoundError:
            pass
        self.create_ledger('contracts')

    def clear_csv(self, filename):
        # write mode ('w') to clear its contents
        with open(filename, mode='w', newline='') as file:
            pass

    def create_ledger(self, key):
        match key:
            case "data":
                filename = self.data_filename
                header = ['timestamp', 'labels', 'account', 'parameter', 'amount']
            case "contracts":
                filename = self.contracts_filename
                header = ['timestamp', 'labels', 'Supplier', 'Receiver', 'amount', 'Priority']
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def add_transaction(self, account, parameter, amount):
        labels = {account}  # Create a set with the account
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.data_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, labels, account, parameter, amount])

    def get_transactions(self, account=None, min_amount=None, max_amount=None):
        transactions = []
        with open(self.data_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) < 5:  # Skip malformed rows
                    continue
                timestamp, labels, acc, parameter, amount_str = row
                try:
                    amount = float(amount_str)
                except ValueError:
                    continue  # Skip if amount cannot be converted to float

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
        labels = {account1, account2}  # Create a set with both accounts
        with open(self.contracts_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, labels, account1, account2, amount_materials, "Normal"])

    def print_ledger(self):
        transactions = self.get_transactions()
        for transaction in transactions:
            print(" | ".join(transaction))

    def add_company_contracts(self, company_name, parameter, amount, related_companies=None):
        """
        Add company contracts to the ledger

        Args:
            company_name: The company writing to the ledger
            parameter: Type of data entry (e.g., 'Revenue', 'Employee Count')
            amount: Numerical value associated with the parameter
            related_companies: Optional list of companies that have contracts with this company
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create labels including the company itself and any related companies
        labels = {company_name}
        if related_companies:
            labels.update(related_companies)

        with open(self.data_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, labels, company_name, parameter, amount])

    def get_company_contracts(self, company_name=None, parameter=None, min_amount=None, max_amount=None):
        """
        Get company contracts from the ledger with optional filtering
        """
        company_data = []
        with open(self.data_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) < 5:  # Skip malformed rows
                    continue
                timestamp, labels, comp, param, amount_str = row

                try:
                    amount = float(amount_str)
                except ValueError:
                    continue  # Skip if amount cannot be converted to float

                # Apply filters
                if company_name and comp != company_name:
                    continue
                if parameter and param != parameter:
                    continue
                if min_amount is not None and amount < min_amount:
                    continue
                if max_amount is not None and amount > max_amount:
                    continue

                company_data.append(row)
        return company_data


# Create a new ledger
ledger = Ledger()

# Example 1: Company 1 adds data that relates to both Company 1 and Company 2
ledger.add_company_contracts(
    company_name='Company 1',  # The company making the entry
    parameter='Joint Revenue',
    amount=1000000,
    related_companies=['Company 2']  # This adds Company 2 to the labels
)

# Example 2: More complex relationship between multiple companies
ledger.add_company_contracts(
    company_name='Company 1',
    parameter='Partnership Result',
    amount=500000,
    related_companies=['Company 2', 'Company 3', 'Company 4']
)

# Display all data with joint labeling
joint_data = ledger.get_company_contracts()
print("\nEntries with joint company labels:")
for data in joint_data:
    print(f"Timestamp: {data[0]}")
    print(f"Labels: {data[1]}")  # Will show the set of companies
    print(f"Primary company: {data[2]}")
    print(f"Parameter: {data[3]}")
    print(f"Amount: {data[4]}")
    print("---")


# ledger.add_transaction('Account 1', 'Payment Received', 1000)
# ledger.add_transaction('Account 2', 'Payment Sent', -500)
# ledger.get_transactions('Account 1')
# ledger.print_ledger()