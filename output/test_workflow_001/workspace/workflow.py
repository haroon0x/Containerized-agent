import json
import csv
import random
import os

def main():
    config_file = 'config.json'
    
    # 1. Load Configuration
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
        return
    
    data_file = config.get('data_file', 'sample_data.csv')
    report_file = config.get('report_file', 'summary_report.txt')
    num_records = config.get('num_records', 100)
    min_value = config.get('min_value', 1)
    max_value = config.get('max_value', 1000)

    print(f"--- Workflow Started ---")
    print(f"Config: {config}")

    # 2. Generate Sample Data
    print(f"Generating {num_records} records into '{data_file}'...")
    try:
        with open(data_file, 'w', newline='') as csvfile:
            fieldnames = ['id', 'value1', 'value2']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(num_records):
                writer.writerow({
                    'id': i + 1,
                    'value1': random.randint(min_value, max_value),
                    'value2': round(random.uniform(min_value, max_value), 2)
                })
        print(f"Successfully generated '{data_file}'.")
    except IOError as e:
        print(f"Error generating data file: {e}")
        return

    # 3. Process the Data
    print(f"Processing data from '{data_file}'...")
    data = []
    try:
        with open(data_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    data.append({
                        'id': int(row['id']),
                        'value1': int(row['value1']),
                        'value2': float(row['value2'])
                    })
                except ValueError as e:
                    print(f"Skipping row due to data conversion error: {row} - {e}")
        
        if not data:
            print("No valid data to process.")
            total_value1 = 0
            total_value2 = 0.0
            avg_value1 = 0.0
            avg_value2 = 0.0
            processed_count = 0
        else:
            processed_count = len(data)
            total_value1 = sum(d['value1'] for d in data)
            total_value2 = sum(d['value2'] for d in data)
            avg_value1 = total_value1 / processed_count
            avg_value2 = total_value2 / processed_count
        
        print(f"Successfully processed {processed_count} records.")

    except FileNotFoundError:
        print(f"Error: Data file '{data_file}' not found for processing.")
        return
    except IOError as e:
        print(f"Error reading data file: {e}")
        return
    
    # 4. Create a Summary Report
    print(f"Creating summary report in '{report_file}'...")
    try:
        with open(report_file, 'w') as f:
            f.write("--- Data Processing Summary Report ---\n")
            f.write(f"Date: {os.stat(data_file).st_mtime_ns if os.path.exists(data_file) else 'N/A'}\n") # Placeholder for actual date/time
            f.write(f"Data Source: {data_file}\n")
            f.write(f"Total Records Processed: {processed_count}\n")
            f.write("\n")
            f.write("--- Metrics ---\n")
            f.write(f"Total Value1: {total_value1:,.2f}\n")
            f.write(f"Average Value1: {avg_value1:,.2f}\n")
            f.write(f"Total Value2: {total_value2:,.2f}\n")
            f.write(f"Average Value2: {avg_value2:,.2f}\n")
            f.write("\n")
            f.write("--- End of Report ---\n")
        print(f"Summary report successfully created in '{report_file}'.")
    except IOError as e:
        print(f"Error writing report file: {e}")

    print(f"--- Workflow Finished ---")

if __name__ == '__main__':
    main()