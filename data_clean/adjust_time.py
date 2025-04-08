import os
import pandas as pd

def process_csv_files(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    # 读取 CSV 文件
                    df = pd.read_csv(file_path)

                    # 删除第一列
                    df = df.iloc[:, 1:]

                    # 修改第二列的 timestamp 数据
                    if not df.empty and df.shape[1] > 0:
                        df.iloc[:, 0] = range(len(df))  # 赋值为范围
                        df.iloc[:, 0] = df.iloc[:, 0].astype(int)  # 确保为整数类型
                    
                    # 保存修改后的文件，只对 timestamp 列应用整数格式
                    df.to_csv(file_path, index=False)

                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    directory = input("Enter the directory path: ").strip()
    process_csv_files(directory)
