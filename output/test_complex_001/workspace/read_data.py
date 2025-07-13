file_path = 'test_data/data.txt'
try:
    with open(file_path, 'r') as f:
        for line in f:
            print(line.strip())
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
except Exception as e:
    print(f"An error occurred: {e}")