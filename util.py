import json

with open("data/data.json") as f:
    data = json.load(f)
    filtered_data = []
    for entry in data:
        if entry["startCrossingId"] <= entry["endCrossingId"]:
            filtered_data.append(entry)    
    with open("data/data.json", "w") as file:
        json.dump(filtered_data, file, indent = 4)