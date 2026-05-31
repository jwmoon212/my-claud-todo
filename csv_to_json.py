import csv
import json
import re

def is_valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email))

# Step 1: Open and read the CSV file
with open("customers.csv", newline="", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    customers = list(reader)

# Step 2: Convert id from string to integer
for customer in customers:
    customer["id"] = int(customer["id"])

# Step 3: Filter out customers with invalid email addresses
valid_customers = [c for c in customers if is_valid_email(c["email"])]
skipped = len(customers) - len(valid_customers)
if skipped:
    print(f"Skipped {skipped} customer(s) with invalid email address.")

# Step 4: Convert the data to a JSON string
json_data = json.dumps(valid_customers, indent=2)

# Step 5: Write the JSON string to a new file
with open("customers.json", "w", encoding="utf-8") as json_file:
    json_file.write(json_data)

print(f"Done! {len(valid_customers)} customer(s) written to customers.json.")
