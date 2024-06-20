import pandas as pd

# Load the two CSV files
file_path1 = '/u/44/yangz2/unix/Documents/Data collection/dataset/subject1-20240620T133856Z-001/subject1/laptop2/IMU9/merge_12.csv'
file_path2 = '/u/44/yangz2/unix/Documents/Data collection/dataset/subject1-20240620T133856Z-001/subject1/laptop2/IMU9/merge_12_1.csv'

# Read the CSV files
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

# Count the number of rows in each file
rows_file1 = len(df1)
rows_file2 = len(df2)

# Subtract the rows of file1 from file2 but keep the header
df2_subset = df2.iloc[rows_file1:]

# Save the subset to a new CSV file
output_file_path = file_path2
df2_subset.to_csv(output_file_path, index=False)

print(rows_file1, rows_file2, output_file_path)
