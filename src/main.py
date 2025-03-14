import csv
import datetime
import os
from flask import Flask, request, jsonify
import json

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
                timestamp, labels, comp, parameter, amount = row
                amount = float(amount)  # Convert amount to a float
                if parameter == search_parameter and comp == company:
                    if account and (account in labels):
                            data = row
                            break
                    else:
                        data = "No Permission"
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
                            data = "No Permission"

        return data

    def calculate_output(self):
        # Get company A's available materials
        company_a_data = {}
        company_b_data = {}
        company_c_data = {}

        # Read all data from the data file
        with open(self.data_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 5:
                    _, labels_str, account, parameter, amount = row
                    # Convert string representation of set to actual set
                    labels = eval(labels_str) if labels_str else set()

                    if 'A' in labels and parameter == 'materials':
                        company_a_data['materials'] = float(amount)
                    elif 'B' in labels and parameter == 'storage':
                        company_b_data['storage'] = float(amount)
                    elif 'C' in labels and parameter == 'storage':
                        company_c_data['storage'] = float(amount)

        # Get contract data
        contracts = []
        with open(self.contracts_filename, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                if len(row) >= 6:
                    _, labels_str, supplier, receiver, parameter, value = row
                    if supplier == 'A' and parameter == 'vaccines':
                        contracts.append({
                            'supplier': supplier,
                            'receiver': receiver,
                            'requested': float(value)
                        })

        # Calculate proportional distribution
        available_materials = company_a_data.get('materials', 0)
        total_storage = company_b_data.get('storage', 0) + company_c_data.get('storage', 0)
        total_requested = sum(c['requested'] for c in contracts)

        results = []

        if total_storage > 0 and total_requested > 0:
            # Calculate distribution proportionally to storage
            for contract in contracts:
                receiver = contract['receiver']
                requested = contract['requested']

                if receiver == 'B':
                    storage_capacity = company_b_data.get('storage', 0)
                elif receiver == 'C':
                    storage_capacity = company_c_data.get('storage', 0)
                else:
                    storage_capacity = 0

                # Calculate proportion based on storage capacity
                proportion = storage_capacity / total_storage
                fair_amount = min(available_materials * proportion, requested)

                results.append({
                    'receiver': receiver,
                    'requested': requested,
                    'recommended vaccines to order': storage_capacity-round(fair_amount, 0),
                    'capacity': storage_capacity,
                    'fill_percentage': round((fair_amount / storage_capacity * 100 if storage_capacity > 0 else 0), 2)
                })

        return {
            'available_materials': available_materials,
            'total_storage': total_storage,
            'total_requested': total_requested,
            'allocations': results
        }

    


ledger = Ledger()

#base 
@app.route('/')
def hello_world():
    return 'Hello! This is the biomeds Holy Hack 2025 API.'

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




@app.route('/simulate_distribution', methods=['GET'])
def simulate_distribution():
    # Clear existing data
    ledger.clear_csv(ledger.data_filename)
    ledger.clear_csv(ledger.contracts_filename)

    # Add company data
    ledger.add_company_data(['A'], 'A', 'materials', 300)  # Company A has materials for 300 vaccines
    ledger.add_company_data(['B'], 'B', 'storage', 500)  # Company B has storage for 500 vaccines
    ledger.add_company_data(['C'], 'C', 'storage', 200)  # Company C has storage for 200 vaccines

    # Add contracts
    ledger.add_company_contract(['A', 'B'], 'A', 'B', 'vaccines', 400)  # A contracts with B for 400 vaccines
    ledger.add_company_contract(['A', 'C'], 'A', 'C', 'vaccines', 200)  # A contracts with C for 100 vaccines

    # Calculate fair distribution
    result = ledger.calculate_output()

    # Save only the recommended vaccines to order for each company
    for allocation in result['allocations']:
        receiver = allocation['receiver']
        recommended_vaccines = round(allocation['recommended vaccines to order'])
        # Save the recommended vaccines to order for each company
        ledger.add_company_data([receiver], receiver, 'recommended_vaccines_to_order', recommended_vaccines)

    print(ledger.get_company_data(account='B', search_parameter='recommended_vaccines_to_order'))

    return jsonify(result), 200


@app.route('/visualize', methods=['GET'])
def visualize():
    # Get company parameter from request
    company = request.args.get('company')
    if not company:
        return "Please specify a company parameter (A, B, or C)", 400

    # Calculate distribution data
    result = ledger.calculate_output()

    # Filter allocations based on company
    filtered_allocations = []
    for allocation in result['allocations']:
        if company == 'A' or company == allocation['receiver']:
            filtered_allocations.append(allocation)

    # Create HTML with embedded Chart.js visualization
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vaccine Distribution Visualization - Company {company}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .chart-container {{ width: 80%; margin: 20px auto; }}
            .data-card {{
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 15px;
                margin: 15px 0;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <h1>Vaccine Distribution Dashboard - Company {company}</h1>

        <div class="data-card">
            <h2>Resource Summary</h2>
            {resource_summary}
        </div>

        {charts}
    </body>
    </html>
    """

    # Create different content based on company
    if company == 'A':
        resource_summary = f"""
            <p>Your available materials: <strong>{result['available_materials']}</strong></p>
            <p>Total Storage Capacity of partners: <strong>{result['total_storage']}</strong></p>
            <p>Total Requested Vaccines from partners: <strong>{result['total_requested']}</strong></p>
        """

        charts = f"""
        <div class="chart-container">
            <canvas id="distributionChart"></canvas>
        </div>

        <script>
            // Parse allocation data
            const allocations = {json.dumps(filtered_allocations)};

            // Create chart showing distribution
            const distributionCtx = document.getElementById('distributionChart').getContext('2d');
            const distributionChart = new Chart(distributionCtx, {{
                type: 'bar',
                data: {{
                    labels: allocations.map(a => 'Company ' + a.receiver),
                    datasets: [
                        {{
                            label: 'Requested Vaccines',
                            data: allocations.map(a => a.requested),
                            backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        }},
                        {{
                            label: 'Capacity',
                            data: allocations.map(a => a.capacity),
                            backgroundColor: 'rgba(153, 102, 255, 0.6)',
                        }},
                        {{
                            label: 'Recommended to Order',
                            data: allocations.map(a => a["recommended vaccines to order"]),
                            backgroundColor: 'rgba(255, 99, 132, 0.6)',
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        title: {{
                            display: true,
                            text: 'Vaccine Distribution to Partner Companies'
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            title: {{
                                display: true,
                                text: 'Number of Vaccines'
                            }}
                        }}
                    }}
                }}
            }});
        </script>
        """
    else:
        # For companies B or C, only show their own data
        company_allocation = next((a for a in result['allocations'] if a['receiver'] == company), None)

        if company_allocation:
            resource_summary = f"""
                <p>Your storage capacity: <strong>{company_allocation['capacity']}</strong></p>
                <p>Vaccines you requested: <strong>{company_allocation['requested']}</strong></p>
                <p>Recommended vaccines to order: <strong>{company_allocation['recommended vaccines to order']}</strong></p>
                <p>Your storage fill percentage: <strong>{company_allocation['fill_percentage']}%</strong></p>
            """

            charts = f"""
            <div class="chart-container">
                <canvas id="companyChart"></canvas>
            </div>

            <script>
                const companyData = {json.dumps(company_allocation)};

                const ctx = document.getElementById('companyChart').getContext('2d');
                const companyChart = new Chart(ctx, {{
                    type: 'bar',
                    data: {{
                        labels: ['Your Company'],
                        datasets: [
                            {{
                                label: 'Requested Vaccines',
                                data: [companyData.requested],
                                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                            }},
                            {{
                                label: 'Storage Capacity',
                                data: [companyData.capacity],
                                backgroundColor: 'rgba(153, 102, 255, 0.6)',
                            }},
                            {{
                                label: 'Recommended to Order',
                                data: [companyData["recommended vaccines to order"]],
                                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        plugins: {{
                            title: {{
                                display: true,
                                text: 'Your Vaccine Distribution Data'
                            }}
                        }},
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                title: {{
                                    display: true,
                                    text: 'Number of Vaccines'
                                }}
                            }}
                        }}
                    }}
                }});
            </script>
            """
        else:
            resource_summary = "<p>No data available for your company</p>"
            charts = ""

    return html.format(
        company=company,
        resource_summary=resource_summary,
        charts=charts
    )

if __name__ == '__main__':
    app.run(debug=True)


