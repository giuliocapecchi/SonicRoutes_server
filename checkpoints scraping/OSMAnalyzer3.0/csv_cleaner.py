import pandas as pd

# Define the input and output file paths
input_file = 'intersections_clustered_with_tags.csv'
output_file = 'intersections_clustered.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(input_file)

# Introduce index as the first column
df.insert(0, 'index', df.index)

# Remove the 'tags' column
df.drop('tags', axis=1, inplace=True)

# Replace ',' with ';' in the 'street_name' column
df['street_name'] = df['street_name'].str.replace(',', ';')

# Save the modified DataFrame to a new CSV file
df.to_csv(output_file, index=False)

print(f"Modified CSV saved to '{output_file}'")
