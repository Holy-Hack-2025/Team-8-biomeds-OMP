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
                header = ['timestamp', 'labels', 'supplier', 'receiver', 'parameter', 'value']
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def add_company_contract(self, supplier, receiver, parameter, value):
        """
        Add a contract between a supplier and receiver to the contracts ledger

        Args:
            supplier: The supplier company name
            receiver: The receiver company name
            amount: Contract amount
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create labels including both supplier and receiver
        labels = f"{supplier},{receiver}"

        with open(self.contracts_filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, labels, supplier, receiver, parameter, value])

    def get_company_contract(self, account=None, company=None, supplier=None, receiver=None):
        """
        Retrieve contract data from the contracts ledger.

        Args:
            account: Account requesting the data (for permission checking)
            company: Company to search for (as supplier or receiver)
            supplier: Filter by specific supplier
            receiver: Filter by specific receiver

        Returns:
            Matching contract data or "Not found"
        """
        data = "Not found"

        with open(self.contracts_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            reader = list(csv.reader(file))

            for row in reversed(reader):
                if len(row) >= 6:  # Ensure we have all columns
                    timestamp, labels, sup, rec, amount, prio = row

                    # Check if row matches search criteria
                    matches_company = not company or (company == sup or company == rec)
                    matches_supplier = not supplier or supplier == sup
                    matches_receiver = not receiver or receiver == rec

                    # Only return data if the requesting account has permission
                    if matches_company and matches_supplier and matches_receiver:
                        if account and (account in labels):
                            # Convert amount to float for consistency
                            data = row
                            break
                        else:
                            print("No Permission")

        return data

    def export_contracts_to_csv(self, output_filename='ledger_Contracts.csv'):
        """
        Export contracts data to a file with .csv extension

        Args:
            output_filename: The name of the output file (default: ledger_Contracts.csv)
        """
        # Read data from the existing contracts CSV file
        contracts_data = []
        try:
            with open(self.contracts_filename, mode='r', newline='') as file:
                reader = csv.reader(file)
                header = next(reader)  # Get header
                contracts_data.append(header)  # Add header to data
                for row in reader:
                    contracts_data.append(row)
        except FileNotFoundError:
            # If the contracts file doesn't exist, use the default header
            contracts_data.append(['timestamp', 'labels', 'Supplier', 'Receiver', 'amount'])

        # Write data to the .csv file
        with open(output_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in contracts_data:
                writer.writerow(row)

        print(f"Contracts data exported to {output_filename}")


# Create a new ledger
ledger = Ledger()

# Add contracts between companies
ledger.add_company_contract(
    supplier='Company 1',
    receiver='Company 2',
    parameter='Free storage',
    value='500cm^3'
)

ledger.add_company_contract(
    supplier='Company 3',
    receiver='Company 1',
    parameter='grondstoffen beschikbaar',
    value='500kg kobalt'
)

# Export the contracts to ledger_Contracts.csv
ledger.export_contracts_to_csv()

# Example 1: Get contract where Company 1 is the supplier
contract1 = ledger.get_company_contract(
    account="Company 1",  # Account requesting data (needs permission)
    supplier="Company 1"
)
print("Contract where Company 1 is supplier:", contract1)

# Example 2: Get contract where Company 1 is involved (as supplier or receiver)
contract2 = ledger.get_company_contract(
    account="Company 1",
    company="Company 1"
)
print("Contract where Company 1 is involved:", contract2)


# Example 3: Get contract with specific supplier and receiver
contract3 = ledger.get_company_contract(
    account="Company 1",
    supplier="Company 3",
    receiver="Company 1"
)
print("Contract between Company 3 and Company 1:", contract3)