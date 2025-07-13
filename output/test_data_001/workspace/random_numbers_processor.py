import random

# Generate 5 random numbers between 1 and 100
numbers_to_write = [random.randint(1, 100) for _ in range(5)]
print(f"Generated numbers: {numbers_to_write}")

# Save numbers to 'numbers.txt' (one number per line)
with open('numbers.txt', 'w') as f:
    for number in numbers_to_write:
        f.write(str(number) + '\n')
print("Numbers saved to 'numbers.txt'.")

# Read numbers from 'numbers.txt' and calculate average
read_numbers = []
try:
    with open('numbers.txt', 'r') as f:
        for line in f:
            try:
                read_numbers.append(int(line.strip()))
            except ValueError:
                print(f"Skipping invalid line in file: {line.strip()}")
except FileNotFoundError:
    print("Error: 'numbers.txt' not found.")
    exit()

if read_numbers:
    total_sum = sum(read_numbers)
    average = total_sum / len(read_numbers)
    print(f"Numbers read from file: {read_numbers}")
    print(f"Sum of numbers: {total_sum}")
    print(f"Average of numbers: {average:.2f}")
else:
    print("No numbers found in 'numbers.txt' to calculate average.")