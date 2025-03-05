import json

# Load the JSON file
with open("book_dreamuk_3-03-25.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Extract only "member" and "user" records
filtered_data = [item for item in data if item["model"] in ["member", "user"]]

# Print the extracted JSON data
print(json.dumps(filtered_data, indent=4))
