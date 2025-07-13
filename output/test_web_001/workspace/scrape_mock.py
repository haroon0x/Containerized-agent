from bs4 import BeautifulSoup
import os

html_file = "mock_data.html"

# Read the HTML file
try:
    with open(html_file, "r", encoding="utf-8") as f:
        html_doc = f.read()
except FileNotFoundError:
    print(f"Error: Mock HTML file '{html_file}' not found. Please ensure it was created.")
    exit(1)

# Parse the HTML
soup = BeautifulSoup(html_doc, 'html.parser')

print("--- Extracted Product Information ---")

products = soup.find_all('div', class_='product')

if not products:
    print("No product data found in the HTML.")
else:
    for i, product in enumerate(products):
        title_tag = product.find('h2')
        price_tag = product.find('span', class_='price')
        description_tag = product.find('p', class_='description')

        title = title_tag.get_text(strip=True) if title_tag else "N/A"
        price = price_tag.get_text(strip=True) if price_tag else "N/A"
        description = description_tag.get_text(strip=True) if description_tag else "N/A"

        print(f"\nProduct {i+1}:")
        print(f"  Title: {title}")
        print(f"  Price: {price}")
        print(f"  Description: {description}")
        print("--------------------------------")

# Optional: Clean up the mock HTML file after execution
# try:
#     os.remove(html_file)
#     print(f"Cleaned up {html_file}")
# except OSError as e:
#     print(f"Error removing {html_file}: {e}")
