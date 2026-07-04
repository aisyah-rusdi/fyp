import sys
import os
# Tell Python to look in the parent directory (src) for your folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from connection import get_connection
from utils.questions import QUESTIONNAIRE

def seed_database():
    print("Connecting to database...")
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # 1. Get the questionnaire ID we created earlier
        cursor.execute("SELECT questionnaire_id FROM questionnaires WHERE is_active = TRUE LIMIT 1")
        questionnaire_row = cursor.fetchone()
        
        if not questionnaire_row:
            print("Error: No active questionnaire found! Please run the SQL INSERT commands first.")
            return
            
        q_id = questionnaire_row[0]
        print(f"Found active questionnaire (ID: {q_id}). Seeding questions...")

        # 2. Loop through the dictionary and insert all questions
        order = 1
        for section_name, questions in QUESTIONNAIRE.items():
            for q in questions:
                # Handle boolean flag for calculated fields (BMI, WHR)
                is_calc = True if q.get("type") == "calculated" else False
                
                # Match Streamlit types to database ENUM ('radio', 'selectbox', 'text', 'numeric', 'calculated')
                q_type = q.get("type")
                if q_type == "number": q_type = "numeric"
                
                insert_q_sql = """
                    INSERT INTO questions (questionnaire_id, section_name, question_text, question_type, question_order, is_calculated)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_q_sql, (q_id, section_name, q["id"], q_type, order, is_calc))
                main_question_db_id = cursor.lastrowid
                order += 1

                # Insert Options for Main Question (if any, like Yes/No)
                if "options" in q:
                    for opt in q["options"]:
                        cursor.execute("INSERT INTO options (question_id, option_text) VALUES (%s, %s)", (main_question_db_id, opt))

                # Insert Follow-Up Questions (if any, like for Irregular cycles)
                if "follow_up" in q:
                    condition = q["follow_up"]["condition"]
                    for fu in q["follow_up"]["questions"]:
                        fu_type = fu.get("type")
                        if fu_type == "number": fu_type = "numeric"
                        
                        insert_fu_sql = """
                            INSERT INTO questions (questionnaire_id, section_name, question_text, question_type, question_order, parent_question_id, follow_up_condition)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_fu_sql, (q_id, section_name, fu["id"], fu_type, order, main_question_db_id, condition))
                        order += 1

        # 3. Save the changes to the database
        conn.commit()
        print("SUCCESS! All questions and options have been perfectly seeded into MariaDB!")

    except Exception as e:
        print(f"Error seeding database: {e}")
    finally:
        # Safely close connection
        if 'cursor' in locals() and cursor: 
            cursor.close()
        if 'conn' in locals() and conn:
            if hasattr(conn, 'open') and conn.open: conn.close()
            elif hasattr(conn, 'is_connected') and conn.is_connected(): conn.close()
            else:
                try: conn.close()
                except: pass

if __name__ == "__main__":
    seed_database()