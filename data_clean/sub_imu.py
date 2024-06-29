import pandas as pd

def sub_imu_1():
    # Load the two CSV files
    file_path1 = '/u/44/yangz2/unix/Documents/vs_code_programs/multi-model-data-collector/multi-model-data-collector/output/merge.csv'
    file_path2 = '/u/44/yangz2/unix/Documents/vs_code_programs/multi-model-data-collector/multi-model-data-collector/output/merge_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1.csv'

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

def sub_imu_2(file_first, file_last):
    # there are a sequence of files to be processed, the first one is merge_1.csv, the second one is merge_1_1.csv, the third one is merge_1_1_1.csv, and so on
    # I want to subtract the rows of the second last file from the last file, and save the subset to the last file, then subtract the rows of the third last file from the second last file, and save the subset to the second last file, and so on
    # keep the first file as it is, and do not subtract any rows from it
    # the number of files to be processed is not fixed, it can be 2, 3, 4, 5, or more
    file_path1 = file_first.split('/')[-1]
    file_path2 = file_last.split('/')[-1]
    # file_path_pre is the file_first without the last part
    file_path_pre = file_first[:-len(file_path1)]
    print("file_path1:", file_path1, "file_path1_pre:", file_path_pre)
    while file_path1 != file_path2:
        file_path_temp = file_path2
        file_path2 = file_path2.split('_')
        # print("file_path2:", file_path2)
        # print("file_path2:", file_path2, "length:", len(file_path2)-1)
        #file_path2 is the file_path2 pop the last '1', keep the rest
        file_path2.pop()
        # print("file_path2:", file_path2)
        file_path2 = '_'.join(file_path2)
        print("file_path2:", file_path2)
        # Read the CSV files
        df1 = pd.read_csv(file_path_pre + file_path2 + '.csv')
        df2 = pd.read_csv(file_path_pre + file_path_temp)
        # print(file_path_pre + file_path_temp)
        # print(file_path_pre + file_path2 + '.csv')
        # Count the number of rows in each file
        rows_file1 = len(df1)
        rows_file2 = len(df2)
        # Subtract the rows of file1 from file2 but keep the header
        df2_subset = df2.iloc[rows_file1:]
        # Save the subset to a new CSV file
        output_file_path = file_path_pre + file_path_temp
        df2_subset.to_csv(output_file_path, index=False)
        print(rows_file1, rows_file2, output_file_path)
        file_path2 = file_path2 + '.csv'
    
file_first = "/u/44/yangz2/unix/Documents/vs_code_programs/multi-model-data-collector/multi-model-data-collector/output/merge_2.csv"
file_last = "/u/44/yangz2/unix/Documents/vs_code_programs/multi-model-data-collector/multi-model-data-collector/output/merge_2_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1_1.csv"
sub_imu_2(file_first, file_last)
