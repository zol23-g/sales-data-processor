import csv
import random
from datetime import datetime, timedelta

# Define departments and a base sales range for each (to create some variation)
departments = [
    {"name": "Electronics", "base_min": 50, "base_max": 350},
    {"name": "Clothing", "base_min": 25, "base_max": 250},
    {"name": "Grocery", "base_min": 60, "base_max": 180},
    {"name": "Home & Garden", "base_min": 20, "base_max": 120},
    {"name": "Sports", "base_min": 10, "base_max": 100},
    {"name": "Automotive", "base_min": 5, "base_max": 80},
    {"name": "Toys", "base_min": 15, "base_max": 150},
    {"name": "Books", "base_min": 10, "base_max": 90},
]

# Define the date range (e.g., 100 days)
start_date = datetime(2023, 8, 1)
end_date = datetime(2023, 11, 9) # Approximately 100 days later

# Function to generate a list of dates within the range
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

# Prepare the data
data = [["Department Name", "Date", "Number of Sales"]]

# For each date in the range, create a sales figure for each department
for single_date in daterange(start_date, end_date):
    date_str = single_date.strftime("%Y-%m-%d")
    for dept in departments:
        sales = random.randint(dept["base_min"], dept["base_max"])
        # Add some weekend boost for certain departments
        if single_date.weekday() >= 5:  # Saturday and Sunday
            if dept["name"] in ["Electronics", "Clothing", "Sports"]:
                sales = int(sales * random.uniform(1.1, 1.6))
        data.append([dept["name"], date_str, sales])

# If we haven't reached 1000 records, add some more from random days
# This ensures we get exactly 1000 lines of *data* (plus header)
while len(data) < 1001: # Target is 1000 data rows + 1 header row
    random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days))
    date_str = random_date.strftime("%Y-%m-%d")
    dept = random.choice(departments)
    sales = random.randint(dept["base_min"], dept["base_max"])
    data.append([dept["name"], date_str, sales])

# Write to a CSV file
with open('sales_data_1000.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(data)

print("File 'sales_data_1000.csv' with 1000 records has been generated!")