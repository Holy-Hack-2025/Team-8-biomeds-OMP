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
                header = ['timestamp', 'labels', 'Supplier', 'Receiver', 'amount', 'Priority']
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)

    def add_company_data(self, labels, account, parameter, amount):
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                if parameter == search_parameter:
                    if account and (account in labels):
                            data = row
                    else:
                        print("No Permission")
        return data
    
    
    # def add_contract(self, account1, account2, amount_materials):
    #     timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     with open(self.filename, mode='a', newline='') as file:
    #         writer = csv.writer(file)
    #         writer.writerow([timestamp, account, description, amount])


    # def print_ledger(self):
    #     transactions = self.get_transactions()
    #     for transaction in transactions:
    #         print(f"{transaction[0]} | {transaction[1]} | {transaction[2]} | {transaction[3]}")


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
    return 'Hello, World! This is the Ledger API.'

@app.route('/add_companydata', methods=['POST'])
def add_companydata():
    data = request.json
    labels = data['labels']
    account = data['account']
    parameter = data['parameter']
    amount = data['amount']
    
    ledger.add_companydata(labels, account, parameter, amount)
    return jsonify({"message": "Data added successfully"}), 200

@app.route('/get_companydata', methods=['GET'])
def get_companydata():
    account = request.args.get('account')
    search_parameter = request.args.get('search_parameter')

    result = ledger.get_companydata(account, search_parameter)
    return jsonify({"data": result}), 200

if __name__ == '__main__':
    app.run(debug=True)