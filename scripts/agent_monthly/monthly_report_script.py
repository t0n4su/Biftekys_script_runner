import pandas as pd
import matplotlib.pyplot as plt
import openpyxl
import zipfile
import os
import sys

# ✅ Accept file argument (drag & drop support)
if len(sys.argv) > 1:
    csv_file = sys.argv[1]
else:
    csv_file = "agent.csv"  # fallback for manual runs

# ✅ Output folder from GUI or fallback to current directory
output_dir = os.environ.get("OUTPUT_DIR", ".")
print(f"📁 Output folder set to: {output_dir}\n")

# 🔎 Read file line by line to find header row
with open(csv_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

header_index = None
for i, line in enumerate(lines):
    if 'CALLS' in line and 'TALK TIME' in line:
        header_index = i
        break

# ✅ Load data into DataFrame
df = pd.read_csv(csv_file, skiprows=header_index, encoding='utf-8')
df.rename(columns={'Χρήστης ': 'agent'}, inplace=True)

# ✅ Keep only relevant columns
columns_of_interest = ['agent', 'CALLS', 'TALK TIME %', 'PAUSETIME %', 'DEAD TIME %']
df_filtered = df[columns_of_interest].copy()

# ✅ Clean percentage columns
for col in ['TALK TIME %', 'PAUSETIME %', 'DEAD TIME %']:
    df_filtered[col] = df_filtered[col].str.replace('%', '').str.strip().astype(float)

# 📊 Create charts
charts = {
    'CALLS': os.path.join(output_dir, 'calls_chart.png'),
    'TALK TIME %': os.path.join(output_dir, 'talk_time_chart.png'),
    'PAUSETIME %': os.path.join(output_dir, 'pause_time_chart.png'),
    'DEAD TIME %': os.path.join(output_dir, 'dead_time_chart.png')
}

for col, filename in charts.items():
    plt.figure(figsize=(10, 6))
    plt.bar(df_filtered['agent'], df_filtered[col], color='red')
    plt.xticks(rotation=90)
    plt.title(f'{col} by Agent')
    plt.xlabel('Agent')
    plt.ylabel(col)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"📊 Chart created: {filename}")

# 📄 Save filtered Excel
output_file = os.path.join(output_dir, "filtered_agent_data.xlsx")
df_filtered.to_excel(output_file, index=False)
print(f"📄 Excel file created: {output_file}")

# 📦 Bundle all files into ZIP
files_to_zip = list(charts.values()) + [
    output_file,
    os.path.join(output_dir, "filtered_agent_time_with_agent_column.xlsx"),
    os.path.join(output_dir, "filtered_agent_time_with_names.xlsx")
]

zip_filename = os.path.join(output_dir, "agent_performance_package.zip")
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for file in files_to_zip:
        if os.path.exists(file):
            zipf.write(file, os.path.basename(file))
            print(f"📦 Added to ZIP: {file}")

# 🗑️ Delete intermediate files (keep only ZIP)
for file in files_to_zip:
    if os.path.exists(file) and file != zip_filename:
        os.remove(file)
        print(f"🗑️ Deleted temporary file: {file}")

# ✅ Final Summary
print("\n========================================")
print("✅ Agent Performance Package Created")
print(f"📦 ZIP file: {zip_filename}")
print("📂 Contents:")
for file in files_to_zip:
    print(f"   - {os.path.basename(file)}")
print("========================================\n")
