import pandas as pd
import json
import numpy as np

# --- Configuration ---
EMPLOYEES_CSV_PATH = 'الموظفين.csv'
BRANCHES_CSV_PATH = 'branches.csv'
OUTPUT_JSON_PATH = 'data.json'
CSV_ENCODING = 'windows-1256'  # الترميز الافتراضي لملفات Excel العربية

def normalize_name(name):
    """توحيد شكل الاسم لتسهيل المطابقة"""
    if not isinstance(name, str):
        return ''
    return name.lower().strip().replace('_', ' ').replace('-', ' ').replace('/', ' ').replace('\\', ' ').replace('  ', ' ').strip()

def process_data():
    try:
        print(f"📥 قراءة ملف الموظفين '{EMPLOYEES_CSV_PATH}'...")
        employees_df = pd.read_csv(EMPLOYEES_CSV_PATH, encoding=CSV_ENCODING)

        print(f"📥 قراءة ملف الفروع '{BRANCHES_CSV_PATH}'...")
        branches_df = pd.read_csv(BRANCHES_CSV_PATH, encoding=CSV_ENCODING)

        # تنظيف الأعمدة
        employees_df.rename(columns=lambda x: x.strip(), inplace=True)
        branches_df.rename(columns=lambda x: x.strip(), inplace=True)

        # === بناء بيانات الفروع والمدراء ===
        print("⚙️ معالجة بيانات الفروع والمدراء...")
        managers_data = {}
        branch_targets = {}

        for _, row in branches_df.iterrows():
            branch_name = row.get('BRANCH', '')
            manager_name = row.get('AREA MANAGER', '')
            target_value = row.get('Target', 0)

            if pd.notna(branch_name) and branch_name:
                branch_targets[normalize_name(branch_name)] = 0 if pd.isna(target_value) else float(target_value)

            if pd.notna(manager_name) and manager_name and pd.notna(branch_name) and branch_name:
                manager_name = str(manager_name).strip()
                if manager_name not in managers_data:
                    managers_data[manager_name] = []
                managers_data[manager_name].append(str(branch_name).strip())

        # === بناء بيانات الموظفين ===
        print("⚙️ معالجة بيانات الموظفين...")
        employees_data = {}

        for _, row in employees_df.iterrows():
            store_name_raw = row.get('اسم المعرض', '')
            employee_name = row.get('الاسم', '')
            system_name = row.get('اسم الموظف على سيستم', '')
            notes = row.get('ملاحظات', '')
            input_target = row.get('التارجت المدخل', 0)

            if pd.notna(store_name_raw) and store_name_raw and pd.notna(employee_name) and employee_name:
                normalized_store_name = normalize_name(store_name_raw)

                if normalized_store_name not in employees_data:
                    employees_data[normalized_store_name] = {
                        'original_name': store_name_raw.strip(),
                        'target': branch_targets.get(normalized_store_name, 0),
                        'employees': []
                    }

                # جمع مبيعات الشهور 1 إلى 10
                sales = []
                for i in range(1, 13):
                    val = row.get(f'مبيعات شهر {i}', 0)
                    sales.append(0 if pd.isna(val) else int(round(val)))


                employees_data[normalized_store_name]['employees'].append({
                    'name': str(employee_name).strip(),
                    'system_name': str(system_name).strip(),
                    'sales': sales,
                    'notes': str(notes).strip() if pd.notna(notes) else '',
                    'manual_target': 0 if pd.isna(input_target) else int(round(input_target))

                })

        # === الدمج والحفظ ===
        final_data = {
            'managers': managers_data,
            'employees_by_store': employees_data
        }

        print(f"💾 حفظ البيانات في '{OUTPUT_JSON_PATH}'...")
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)

        print("\n✅ التحويل ناجح! الملف تم إنشاؤه بنجاح.")

    except FileNotFoundError as e:
        print(f"❌ خطأ: لم يتم العثور على الملف - {e.filename}")
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")

if __name__ == '__main__':
    process_data()
