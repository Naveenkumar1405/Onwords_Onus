import csv


def add_client_to_crm(name, email, phone):
    # Mock implementation - replace with your actual CRM adding logic
    print(f"Added client: {name}, {phone},{email}")


def add_clients_from_csv(file_path):
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            add_client_to_crm(row["Name"], row["Phone"], row["Email"])


if __name__ == "__main__":
    add_clients_from_csv("sample_client_data.csv")
