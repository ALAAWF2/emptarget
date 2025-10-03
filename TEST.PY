import pandas as pd
import json
import numpy as np

# --- Configuration ---
EMPLOYEES_CSV_PATH = 'الموظفين.csv'
BRANCHES_CSV_PATH = 'branches.csv'
OUTPUT_JSON_PATH = 'data.json'
CSV_ENCODING = 'windows-1256' # Common encoding for Arabic CSVs from Excel on Windows

def normalize_name(name):
    """
    Normalizes a string by making it lowercase, trimming whitespace,
    replacing common separators, and collapsing multiple spaces.
    Ensures consistent matching between different files.
    """
    if not isinstance(name, str):
        return ''
    return name.lower().strip().replace('_', ' ').replace('-', ' ').replace(r'/', ' ').replace('\\', ' ').replace('  ', ' ').strip()

def process_data():
    """
    Reads data from CSV files, processes and structures it,
    and saves it as a single JSON file.
    """
    try:
        # --- Read CSV files using pandas for robust parsing ---
        print(f"Reading '{EMPLOYEES_CSV_PATH}'...")
        employees_df = pd.read_csv(EMPLOYEES_CSV_PATH, encoding=CSV_ENCODING)
        
        print(f"Reading '{BRANCHES_CSV_PATH}'...")
        branches_df = pd.read_csv(BRANCHES_CSV_PATH, encoding=CSV_ENCODING)

        # --- Clean and Structure Employee Data ---
        print("Processing employee data...")
        employees_data = {}
        # Rename columns to remove trailing spaces and ensure consistency
        employees_df.rename(columns=lambda x: x.strip(), inplace=True)
        
        for index, row in employees_df.iterrows():
            # Use .get(key, default) to avoid errors if a column is missing
            store_name_raw = row.get('اسم المعرض', '')
            employee_name = row.get('الاسم', '')
            system_name = row.get('اسم الموظف على سيستم', '') # Get the system name

            if pd.notna(store_name_raw) and store_name_raw and pd.notna(employee_name) and employee_name:
                normalized_store_name = normalize_name(store_name_raw)
                
                if normalized_store_name not in employees_data:
                    employees_data[normalized_store_name] = {
                        'original_name': store_name_raw.strip(),
                        'employees': []
                    }

                sales = []
                for i in range(1, 10):
                    sale_value = row.get(f'مبيعات شهر {i}', 0)
                    # Replace numpy.nan with 0 for JSON compatibility
                    sales.append(0 if pd.isna(sale_value) else float(sale_value))

                employees_data[normalized_store_name]['employees'].append({
                    'name': str(employee_name).strip(),
                    'system_name': str(system_name).strip(), # Add system name to the employee object
                    'sales': sales
                })

        # --- Clean and Structure Manager Data ---
        print("Processing manager and branch data...")
        managers_data = {}
        branches_df.rename(columns=lambda x: x.strip(), inplace=True)

        for index, row in branches_df.iterrows():
            manager_name = row.get('AREA MANAGER', '')
            branch_name_raw = row.get('BRANCH', '')

            if pd.notna(manager_name) and manager_name and pd.notna(branch_name_raw) and branch_name_raw:
                manager_name = manager_name.strip()
                if manager_name not in managers_data:
                    managers_data[manager_name] = []
                
                managers_data[manager_name].append(branch_name_raw.strip())
        
        # --- Combine into final structure ---
        final_data = {
            'managers': managers_data,
            'employees_by_store': employees_data
        }

        # --- Write to JSON file ---
        print(f"Writing processed data to '{OUTPUT_JSON_PATH}'...")
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            # ensure_ascii=False is crucial for saving Arabic characters correctly
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print("\nConversion successful!")
        print(f"'{OUTPUT_JSON_PATH}' has been created/updated.")

    except FileNotFoundError as e:
        print(f"\nError: File not found - {e.filename}")
        print("Please make sure both CSV files are in the same directory as the script.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == '__main__':
    process_data()

