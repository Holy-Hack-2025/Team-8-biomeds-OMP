import csv
import datetime
import os
from flask import Flask, request, jsonify

app = Flask(__name__)


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
                pass
                #self.clear_csv(self.data_filename)  # file exists
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
                header = ['timestamp', 'labels', 'Supplier', 'Receiver', 'amount', 'Priority']
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def add_company_data(self, labels, account, parameter, amount):
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            labels = set(labels)
            with open(self.data_filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([timestamp, labels, account, parameter, amount])

    def get_company_data(self, account= None, company = None, search_parameter=None):
        data = "Not found"
        with open(self.data_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            reader = list(csv.reader(file))
            for row in reversed(reader):
                timestamp, labels, acc, parameter, amount = row
                amount = float(amount)  # Convert amount to a float
                print(parameter == search_parameter)
                print(search_parameter)
                if parameter == search_parameter:

                    if account and (account in labels):
                            data = row
                    else:
                        print("No Permission")
        return data
    
    def add_company_contract(self, labels, supplier, receiver, parameter, value):
        """
        Add a contract between a supplier and receiver to the contracts ledger

        Args:
            supplier: The supplier company name
            receiver: The receiver company name
            amount: Contract amount
            priority: Priority level of the contract
        """
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create labels including both supplier and receiver
        #labels = f"{supplier},{receiver}"

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
            priority: Filter by priority level

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
                    #matches_priority = not priority or str(priority) == prio

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
            contracts_data.append(['timestamp', 'labels', 'Supplier', 'Receiver', 'amount', 'Priority'])

        # Write data to the .csv file
        with open(output_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in contracts_data:
                writer.writerow(row)

        print(f"Contracts data exported to {output_filename}")
    

# Example usage
# ledger = Ledger()
# ledger.add_companydata(set(['Account1']),'Account1', 'stock', 1000)
# print(ledger.get_companydata('Account1','Account1','stock'))
# print(ledger.get_transactions('Account 1'))
# ledger.print_ledger()
ledger = Ledger()

#base 
@app.route('/')
def hello_world():
    return 'Hello! This is this API.'

@app.route('/add_company_data', methods=['POST'])
def add_company_data():
    data = request.json
    labels = data['labels']
    account = data['account']
    parameter = data['parameter']
    amount = data['amount']

    ledger.add_company_data(labels, account, parameter, amount)
    return jsonify({"message": "Data added successfully"}), 200

@app.route('/add_company_contracts', methods=['POST'])
def add_company_contracts():
    data = request.json
    labels = data['labels']
    supplier = data['supplier']
    receiver = data['receiver']
    parameter = data['parameter']
    value = data['value']

    ledger.add_company_contract(labels, supplier, receiver, parameter, value)
    return jsonify({"message": "Data added successfully"}), 200

@app.route('/get_company_data', methods=['GET'])
def get_company_data():
    account = request.args.get('account')
    company = request.args.get('company')
    search = request.args.get('search')

    result = ledger.get_company_data(account, company, search)
    return jsonify({"data": result}), 200


@app.route('/get_company_contract', methods=['GET'])
def get_company_contracts():
    account = request.args.get('account')
    company = request.args.get('company')
    supplier = request.args.get('supplier')
    receiver = request.args.get('receiver')

    result = ledger.get_company_contract(account, company, supplier, receiver)
    return jsonify({"data": result}), 200

if __name__ == '__main__':
    app.run(debug=True)