import os
import zipfile
import re
from datetime import datetime
from prettytable import PrettyTable
import argparse
import matplotlib.pyplot as plt

#Go into the excel file zip archive location and extract calcChain.xml
def extract_calcchain_values(file_path):
    calcchain_path = "xl/calcChain.xml"

    with zipfile.ZipFile(file_path, "r") as zip_file:
        if calcchain_path in zip_file.namelist():
            calcchain_data = zip_file.read(calcchain_path).decode("utf-8")
            values = re.findall(r'r="([^"]+)"', calcchain_data)
            return values

    return None

#Generates a table to display calcChain values for each file and their associated index position when they were originially entered
def generate_calc_chain_table(excel_files):
    calcchain_values = {}
    for file in excel_files:
        values = extract_calcchain_values(file)
        calcchain_values[file] = values

    table = PrettyTable()
    table.field_names = ["calcChain Index position"] + excel_files
    max_rows = max(len(values) for values in calcchain_values.values())
    for i in range(max_rows):
        row = [f"Index {i+1}"]
        for file in excel_files:
            values = calcchain_values[file]
            if i < len(values):
                row.append(values[i])
            else:
                row.append("")
        table.add_row(row)

    return table, calcchain_values

#Compare calcChain values between different excel files
def compare_calc_chain_values(excel_files, calcchain_values):
    matching_files = []
    different_files = []

    for i in range(len(excel_files) - 1):
        for j in range(i + 1, len(excel_files)):
            file1 = excel_files[i]
            file2 = excel_files[j]
            values1 = calcchain_values[file1]
            values2 = calcchain_values[file2]
            if values1 == values2:
                matching_files.append((file1, file2))
            else:
                different_files.append((file1, file2))

    return matching_files, different_files

#Save the results to files (table, HTML, graph image)
def save_results(table, matching_files, different_files, results_folder, excel_files, calcchain_values):
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    results_folder = f"{results_folder}_{timestamp}"
    os.makedirs(results_folder, exist_ok=True)

    csv_file = os.path.join(results_folder, "table_results.csv")
    table_csv = table.get_csv_string()
    table_csv_cleaned = "\n".join([line for line in table_csv.splitlines() if line.strip()])
    with open(csv_file, "w") as file:
        file.write(table_csv_cleaned)

    html_file = os.path.join(results_folder, "table_results.html")
    with open(html_file, "w") as file:
        file.write(table.get_html_string())

    # Create the graph_results.html page
    graph_html_file = os.path.join(results_folder, "graph_results.html")
    with open(graph_html_file, "w") as file:
        file.write("<html>\n")
        file.write("<head>\n")
        file.write("<title>Graph Results</title>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<h1>Graph Results</h1>\n")
        file.write("<h2>CalcChain Values by Index Position</h2>\n")
        file.write("<img src=\"table_results.png\" alt=\"Graph\">\n")
        file.write("</body>\n")
        file.write("</html>\n")

    #Create and save line graphs for each file with index position as the x-axis
    for file in excel_files:
        values = calcchain_values[file]
        index_positions = range(1, len(values) + 1)
        plt.plot(index_positions, values, label=file)

    plt.xlabel("Index position")
    plt.ylabel("CalcChain Value")
    plt.legend()
    plt.title("CalcChain Values by Index Position")
    graph_image_file = os.path.join(results_folder, "table_results.png")
    plt.savefig(graph_image_file)
    plt.close()

    print("[*] Results saved:")
    print(f"[*] CSV file: {csv_file}")
    print(f"[*] HTML file: {html_file}")
    print(f"[*] Graph HTML file: {graph_html_file}")
    print(f"[*] Graph image file: {graph_image_file}")

    return results_folder

#Main function to ingest excel files, their calcChain.xml files, and compare them
def main(excel_files):
    
    table, calcchain_values = generate_calc_chain_table(excel_files)
    matching_files, different_files = compare_calc_chain_values(excel_files, calcchain_values)

    print("[*] CalcChain.xml Values:")
    print(table)
    print()

    if matching_files:
        print("[*] Matching CalcChain.xml values:")
        for files in matching_files:
            print(f"[*] {files[0]} and {files[1]}")
        print()

    if different_files:
        print("[*] Different CalcChain.xml values (possible formula tampering):")
        for files in different_files:
            print(f"[*] {files[0]} and {files[1]}")
        print()

    results_folder = save_results(table, matching_files, different_files, "calc_chain_results", excel_files, calcchain_values)

#Argparse options to caputre one or multiple files
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare calcChain.xml values in Excel files to possibly detect tampering of formulas.")
    parser.add_argument("--files", nargs="+", help="Excel files to compare", required=True)
    args = parser.parse_args()

    main(args.files)
