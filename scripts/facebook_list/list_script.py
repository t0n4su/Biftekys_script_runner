import pandas as pd
import re
import os
import sys
import datetime

# ✅ Accept file argument
if len(sys.argv) > 1:
    INPUT_FILE = sys.argv[1]
else:
    INPUT_FILE = "forma.csv"  # fallback for old behavior

output_dir = os.environ.get("OUTPUT_DIR", ".")
OUTPUT_FILE = os.path.join(output_dir, "List_Ready.xlsx")


def clean_phone(number):
    """
    Clean phone numbers for calling:
    - Remove all non-digit characters
    - Remove country code '30' if present
    - Keep only 10-digit local numbers
    """
    if pd.isna(number):
        return ""
    number = str(number).strip()
    number = re.sub(r"\D", "", number)  # remove everything except digits

    # Remove +30 or 30 country code prefix if present
    if number.startswith("30") and len(number) > 10:
        number = number[2:]

    # Ensure only 10-digit numbers
    if len(number) > 10:
        number = number[-10:]
    elif len(number) < 10:
        # invalid number, return empty
        return ""
    
    return number


def main():
    # Read CSV
    df = pd.read_csv(INPUT_FILE, encoding="utf-16", sep="\t")
    print("✅ Columns:", df.columns.tolist())

    # Clean phone numbers for calling
    cleaned = df["phone"].apply(clean_phone)

    # Set today's date (broadcast to all rows)
    today = datetime.datetime.today().strftime("%d/%m/%Y")

    # Create result DataFrame with desired column order
    result = pd.DataFrame({
        "LEAD_DATE": today,
        "FORM_NAME": df["adset_name"],
        "MOBILE PROVIDER": "",
        "FIXED PROVIDER": "",
        "CUS_NAME": df["full name"],
        "MSISDN": cleaned,
        "TILEFONO_KATIKIAS": cleaned
    })

    # Save to Excel
    result.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ File created: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
