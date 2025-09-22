import pandas as pd
import re
import os
import sys
import datetime
import glob

def get_input_files():
    """Get input files from command line arguments or auto-detect lead generation files"""
    input_files = sys.argv[1:] if len(sys.argv) > 1 else []
    # If no files provided as arguments, look for lead generation files in current directory
    if not input_files:
        pattern_files = glob.glob("lead_generation_*.xlsx")
        if pattern_files:
            input_files = pattern_files
            print(f"Auto-detected {len(pattern_files)} lead generation files")
    # If still no files found, use fallback
    if not input_files:
        input_files = ["forma.csv"] # Original fallback
        print("Using fallback input file: forma.csv")
    return input_files

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
    number = re.sub(r"\D", "", number) # remove everything except digits
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

def detect_source(filepath):
    fname = os.path.basename(filepath)
    if fname.startswith("lead_generation_"):
        return "tiktok"
    elif fname.startswith("Απλοποιημένη φόρμα_Leads_"):
        return "facebook"
    else:
        return "unknown"

def process_lead_file(file_path):
    """Process a single lead generation file"""
    try:
        source = detect_source(file_path)
        if file_path.endswith('.xlsx'):
            # Handle Excel files (lead generation format)
            df = pd.read_excel(file_path)
            # Map columns from lead generation format to expected format
            if 'Name' in df.columns and 'Phone number' in df.columns:
                # Lead generation format
                df_mapped = pd.DataFrame({
                    'full name': df['Name'],
                    'phone': df['Phone number'],
                    'adset_name': df.get('ad_name', df.get('form_name', 'Unknown')),
                    'SOURCE': source
                })
            else:
                # Assume it's already in the expected format
                df_mapped = df
                df_mapped['SOURCE'] = source
        elif file_path.endswith('.csv'):
            # Handle CSV files (original format)
            df = pd.read_csv(file_path, encoding="utf-16", sep="\t")
            df['SOURCE'] = source
            df_mapped = df
        else:
            print(f"❌ Unsupported file format: {file_path}")
            return pd.DataFrame()
        print(f"✅ Processed {file_path}: {len(df_mapped)} records")
        return df_mapped
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return pd.DataFrame()

def main():
    output_dir = os.environ.get("OUTPUT_DIR", ".")
    OUTPUT_FILE = os.path.join(output_dir, "List_Ready.xlsx")
    print("🚀 Starting lead generation processing...")

    # Get input files
    input_files = get_input_files()
    print(f"📁 Processing {len(input_files)} files:")
    for f in input_files:
        print(f" - {f}")

    # Process all files and combine
    combined_df = pd.DataFrame()
    for file_path in input_files:
        df_mapped = process_lead_file(file_path)
        if not df_mapped.empty:
            combined_df = pd.concat([combined_df, df_mapped], ignore_index=True)

    if combined_df.empty:
        print("❌ No valid data found in input files")
        return

    print(f"📊 Total combined records: {len(combined_df)}")
    print(f"📋 Available columns: {list(combined_df.columns)}")

    # Clean phone numbers for calling
    print("🧹 Cleaning phone numbers...")
    cleaned = combined_df["phone"].apply(clean_phone)

    # Set today's date (broadcast to all rows)
    today = datetime.datetime.today().strftime("%d/%m/%Y")

    # Create result DataFrame with desired column order, including SOURCE
    result = pd.DataFrame({
        "LEAD_DATE": today,
        "FORM_NAME": combined_df.get("adset_name", "Unknown"),
        "MOBILE PROVIDER": "",
        "FIXED PROVIDER": "",
        "CUS_NAME": combined_df["full name"],
        "MSISDN": cleaned,
        "TILEFONO_KATIKIAS": cleaned,
        "SOURCE": combined_df["SOURCE"]
    })

    # Filter out empty phone numbers
    valid_records = len(result)
    result = result[result["MSISDN"] != ""]
    filtered_records = len(result)
    if filtered_records < valid_records:
        print(f"⚠️ Filtered out {valid_records - filtered_records} records with invalid phone numbers")

    # Save to Excel
    result.to_excel(OUTPUT_FILE, index=False)
    print(f"✅ File created: {OUTPUT_FILE}")
    print(f"✅ Total valid records: {len(result)}")

    # Show sample of results
    if len(result) > 0:
        print("\n📋 Sample of processed data:")
        print(result.head()[['CUS_NAME', 'MSISDN', 'FORM_NAME', 'SOURCE']].to_string(index=False))

if __name__ == "__main__":
    main()
