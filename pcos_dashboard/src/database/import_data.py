import sys
import os
import pandas as pd
import uuid

# Tell Python to look in the parent directory for your folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import get_connection

# ==========================================
# 1. CONFIGURATION
# ==========================================
QUESTIONNAIRE_ID = 1 
MODEL_ID = 1 
CSV_FILE_PATH = "PCOS_data_without_infertility.csv" # Ensure your CSV is in the same folder, or update this path

# This links your CSV columns directly to the 'question_text' in your database.
csv_to_question_map = {
    "Age (yrs)": "How old are you?",
    "Marraige Status (Yrs)": "How many years have you been married?",
    "Blood Group": "What is your blood group?",
    "Weight (Kg)": "Enter your weight (kg)",
    "Height(Cm)": "Enter your height (cm)",
    "Hip(inch)": "Enter your hip circumference (inch)",
    "Waist(inch)": "Enter your waist circumference (inch)",
    "Pulse rate(bpm)": "Enter your pulse rate (bpm)",
    "RR (breaths/min)": "Enter your respiratory rate (breaths/min)",
    "BP _Systolic (mmHg)": "Enter your systolic blood pressure (mmHg)",
    "BP _Diastolic (mmHg)": "Enter your diastolic blood pressure (mmHg)",
    "Cycle length(days)": "Enter your cycle length (days)",
    "Cycle(R/I)": "Is your cycle regular or irregular?",
    "Skin darkening (Y/N)": "Do you notice any skin darkening? (armpits, thighs, neck, etc)",
    "Weight gain(Y/N)": "Do you notice any abrupt weight gain?",
    "hair growth(Y/N)": "Do you notice hair growth at unexpected places? (chin, upper lip, abdomen, etc)",
    "Pimples(Y/N)": "Do you have frequent pimples/acne?",
    "Hair loss(Y/N)": "Do you have significant hair loss/thinning?",
    "No. of aborptions": "How many abortions have you had?",
    "Pregnant(Y/N)": "Are you currently pregnant?",
    "Fast food (Y/N)": "Do you eat Fast Food often?",
    "Reg.Exercise(Y/N)": "Do you excersize regularly?"
}

def import_csv_data():
    print("Connecting to database...")
    conn = get_connection()
    # Ensure dictionary=True so we can access columns by name
    cursor = conn.cursor()

    try:
        # ==========================================
        # 2. PRE-FETCH IDS FROM YOUR SEEDED QUESTIONS
        # ==========================================
        print("Fetching Question and Option IDs from database...")
        
        cursor.execute("SELECT question_id, question_text, question_type FROM questions WHERE questionnaire_id = %s", (QUESTIONNAIRE_ID,))
        questions_db = cursor.fetchall()
        question_dict = {q['question_text']: q for q in questions_db}

        cursor.execute("""
            SELECT o.option_id, o.question_id, o.option_text 
            FROM options o 
            JOIN questions q ON o.question_id = q.question_id 
            WHERE q.questionnaire_id = %s
        """, (QUESTIONNAIRE_ID,))
        options_db = cursor.fetchall()
        
        option_dict = {}
        for opt in options_db:
            qid = opt['question_id']
            if qid not in option_dict:
                option_dict[qid] = {}
            option_dict[qid][opt['option_text'].strip().lower()] = opt['option_id']

        # ==========================================
        # 3. LOAD CSV
        # ==========================================
        df = pd.read_csv(CSV_FILE_PATH)
        print(f"Loaded {len(df)} rows from CSV. Starting data import...")

        # ==========================================
        # 4. ITERATE AND INSERT DATA
        # ==========================================
        for index, row in df.iterrows():
            # A. CREATE DUMMY USER
            dummy_email = f"dataset_user_{uuid.uuid4().hex[:8]}@training.local"
            cursor.execute("""
                INSERT INTO users (role_id, username, full_name, email, password_hash, license_number, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (1, f"user_{index}", f"Data User {index}", dummy_email, "dummy_hash", None, "active"))
            
            user_id = cursor.lastrowid

            # B. CREATE SUBMISSION
            cursor.execute("""
                INSERT INTO submissions (user_id, questionnaire_id)
                VALUES (%s, %s)
            """, (user_id, QUESTIONNAIRE_ID))
            
            submission_id = cursor.lastrowid

            # C. TRANSLATE & INSERT ANSWERS
            for csv_col, q_text in csv_to_question_map.items():
                if csv_col not in row or pd.isna(row[csv_col]):
                    continue
                
                val = row[csv_col]
                q_info = question_dict.get(q_text)
                
                if not q_info:
                    continue
                
                q_id = q_info['question_id']
                q_type = q_info['question_type']
                
                numeric_val = None
                selected_option_id = None
                text_val = None

                if q_type == 'numeric':
                    numeric_val = float(val)
                elif q_type in ['radio', 'selectbox']:
                    val_str = str(val).strip().lower()
                    if val_str == 'y': val_str = 'yes'
                    if val_str == 'n': val_str = 'no'
                    if val_str == 'r': val_str = 'regular'
                    if val_str == 'i': val_str = 'irregular'
                    
                    if q_id in option_dict and val_str in option_dict[q_id]:
                        selected_option_id = option_dict[q_id][val_str]
                    else:
                        text_val = str(val)

                cursor.execute("""
                    INSERT INTO answers (submission_id, question_id, selected_option_id, text_value, numeric_value)
                    VALUES (%s, %s, %s, %s, %s)
                """, (submission_id, q_id, selected_option_id, text_val, numeric_val))

            # D. INSERT ML PREDICTION TARGET
            pcos_val = str(row.get('PCOS (Y/N)', '')).strip().upper()
            if pcos_val in ['Y', '1', 'YES']:
                risk_level, risk_score = 'High Risk', 0.95
            else:
                risk_level, risk_score = 'Low Risk', 0.05
                
            cursor.execute("""
                INSERT INTO predictions (submission_id, user_id, model_id, risk_score, risk_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (submission_id, user_id, MODEL_ID, risk_score, risk_level))

            if index % 50 == 0:
                conn.commit()
                print(f"Processed {index} rows...")

        conn.commit()
        print("SUCCESS! Patient data and answers have been perfectly imported into MariaDB!")

    except Exception as e:
        print(f"Error importing data: {e}")
        conn.rollback()
    finally:
        if 'cursor' in locals() and cursor: cursor.close()
        if 'conn' in locals() and conn:
            if hasattr(conn, 'open') and conn.open: conn.close()
            elif hasattr(conn, 'is_connected') and conn.is_connected(): conn.close()
            else:
                try: conn.close()
                except: pass

if __name__ == "__main__":
    import_csv_data()