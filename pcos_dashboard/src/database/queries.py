# pcos_dashboard/src/database/queries.py

# ==========================================
# 1. USERS & AUTHENTICATION
# ==========================================

GET_USER_BY_EMAIL = """
    SELECT user_id, password_hash, role_id, full_name, status 
    FROM users 
    WHERE email = %s
"""

GET_USER_NAME_BY_EMAIL = """
    SELECT full_name 
    FROM users 
    WHERE email = %s
"""

CREATE_USER = """
    INSERT INTO users (role_id, username, full_name, email, password_hash, license_number, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

GET_ALL_USERS_FOR_ADMIN = """
    SELECT u.user_id, u.username, u.full_name, u.email, r.role_name, u.created_at
    FROM users u
    JOIN roles r ON u.role_id = r.role_id
    ORDER BY u.created_at DESC
"""

GET_USER_PROFILE_BY_ID = """
    SELECT username, full_name, email, role_id, created_at 
    FROM users 
    WHERE user_id = %s
"""

# ==========================================
# 2. DYNAMIC QUESTIONNAIRE
# ==========================================

GET_ACTIVE_QUESTIONNAIRE = """
    SELECT questionnaire_id, title 
    FROM questionnaires 
    WHERE is_active = TRUE 
    LIMIT 1;
"""

GET_QUESTIONS_BY_QUESTIONNAIRE = """
    SELECT 
        question_id, section_name, question_text, question_type, 
        question_order, is_ml_feature, feature_name, is_calculated,
        parent_question_id, follow_up_condition, is_required
    FROM questions
    WHERE questionnaire_id = %s
    ORDER BY section_name, question_order;
"""

GET_OPTIONS_BY_QUESTIONNAIRE = """
    SELECT 
        o.option_id, o.question_id, o.option_text, o.option_value
    FROM options o
    JOIN questions q ON o.question_id = q.question_id
    WHERE q.questionnaire_id = %s;
"""

# ==========================================
# 3. SUBMISSIONS & ANSWERS
# ==========================================

INSERT_SUBMISSION = """
    INSERT INTO submissions (user_id, questionnaire_id)
    VALUES (%s, %s);
"""

INSERT_ANSWER = """
    INSERT INTO answers (submission_id, question_id, selected_option_id, text_value, numeric_value)
    VALUES (%s, %s, %s, %s, %s);
"""

GET_USER_LATEST_SUBMISSION = """
    SELECT submission_id, submitted_at
    FROM submissions
    WHERE user_id = %s
    ORDER BY submitted_at DESC
    LIMIT 1;
"""

# ==========================================
# 4. ML PREDICTIONS
# ==========================================

GET_ACTIVE_ML_MODEL = """
    SELECT model_id 
    FROM ml_models 
    WHERE is_active = TRUE 
    LIMIT 1;
"""

INSERT_PREDICTION = """
    INSERT INTO predictions (submission_id, user_id, model_id, risk_score, risk_level)
    VALUES (%s, %s, %s, %s, %s);
"""

# FIXED: was referencing 'confidence_score' which does not exist in the predictions table.
# The correct column is 'risk_score'.
GET_USER_PREDICTION_HISTORY = """
    SELECT risk_score, risk_level, created_at
    FROM predictions
    WHERE user_id = %s
    ORDER BY created_at DESC;
"""

# ==========================================
# 5. COMMUNITY DASHBOARD (AGGREGATES)
# ==========================================

GET_COMMUNITY_RISK_DISTRIBUTION = """
    SELECT risk_level, COUNT(*) as total_count
    FROM predictions
    GROUP BY risk_level
"""

GET_TOTAL_ACTIVE_USERS = """
    SELECT COUNT(*) as total_users 
    FROM users 
    WHERE is_active = TRUE AND role_id = 1
"""

# ==========================================
# 6. JOURNALS (LIFESTYLE)
# ==========================================

INSERT_JOURNAL = """
    INSERT INTO journal_logs (user_id, log_date, entry_text, mood) 
    VALUES (%s, %s, %s, %s)
"""

GET_USER_JOURNALS = """
    SELECT entry_text, mood_score, created_at 
    FROM journals 
    WHERE user_id = %s 
    ORDER BY created_at DESC
"""

# ==========================================
# 7. SAVED ARTICLES (RESOURCES)
# ==========================================

INSERT_SAVED_ARTICLE = """
    INSERT IGNORE INTO saved_articles (user_id, article_title, article_url, authors, publication_date)
    VALUES (%s, %s, %s, %s, %s)
"""

GET_USER_SAVED_ARTICLES = """
    SELECT saved_id, article_title, article_url, authors, publication_date, saved_at 
    FROM saved_articles 
    WHERE user_id = %s 
    ORDER BY saved_at DESC
"""

DELETE_SAVED_ARTICLE = """
    DELETE FROM saved_articles WHERE saved_id = %s AND user_id = %s
"""

# ==========================================
# 8. PRO CONNECT (DOCTOR-PATIENT)
# ==========================================

SEARCH_PATIENT_BY_EMAIL = """
    SELECT user_id, full_name, email 
    FROM users 
    WHERE email = %s AND role_id = 1
"""

LINK_DOCTOR_PATIENT = """
    INSERT IGNORE INTO doctor_patients (doctor_id, patient_id)
    VALUES (%s, %s)
"""

GET_DOCTOR_PATIENTS = """
    SELECT u.user_id, u.full_name, u.email, dp.connected_at
    FROM users u
    JOIN doctor_patients dp ON u.user_id = dp.patient_id
    WHERE dp.doctor_id = %s
    ORDER BY dp.connected_at DESC
"""

SEARCH_PATIENT_BY_EMAIL_OR_USERNAME = """
    SELECT user_id, full_name, email, username 
    FROM users 
    WHERE (email = %s OR username = %s) AND role_id = 1;
"""

# ==========================================
# 9. ADMIN ANALYTICS 
# ==========================================

GET_TOTAL_USERS_BY_ROLE = """
    SELECT role_id, COUNT(*) as count 
    FROM users 
    GROUP BY role_id
"""

GET_TOTAL_ASSESSMENTS = """
    SELECT COUNT(*) as total FROM predictions
"""

GET_RISK_DISTRIBUTION = """
    SELECT risk_level, COUNT(*) as count 
    FROM predictions 
    GROUP BY risk_level
"""

GET_AVG_CONFIDENCE_SCORE = """
    SELECT AVG(risk_score) as avg_score FROM predictions
"""

GET_USER_GROWTH_LAST_7_DAYS = """
    SELECT DATE(created_at) as date, COUNT(user_id) as new_users 
    FROM users 
    WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
    GROUP BY DATE(created_at)
    ORDER BY date ASC
"""

# ==========================================
# 10. USER MANAGEMENT (ADMIN)
# ==========================================

GET_PENDING_DOCTORS = """
    SELECT user_id, full_name, email, created_at 
    FROM users 
    WHERE role_id = 2 AND status = 'pending'
"""

UPDATE_USER_STATUS = """
    UPDATE users 
    SET status = %s 
    WHERE user_id = %s
"""

GET_ALL_USERS = """
    SELECT user_id, full_name, email, role_id, status, created_at 
    FROM users
    ORDER BY created_at DESC
"""

# ==========================================
# 11. CYCLE & JOURNAL DATA FETCHING / UPSERTING
# ==========================================

GET_MONTHLY_CYCLES = """
    SELECT log_date, period, mood, symptoms, cervical_fluid, medication, blood_pressure, sugar_level, notes 
    FROM cycle_logs 
    WHERE user_id = %s AND YEAR(log_date) = %s AND MONTH(log_date) = %s
"""

GET_MONTHLY_JOURNALS = """
    SELECT id, log_date, created_at, entry_text, mood 
    FROM journal_logs 
    WHERE user_id = %s AND YEAR(log_date) = %s AND MONTH(log_date) = %s
"""

UPSERT_CYCLE = """
    INSERT INTO cycle_logs (user_id, log_date, period, mood, symptoms, cervical_fluid, medication, blood_pressure, sugar_level, notes) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        period = %s, mood = %s, symptoms = %s, cervical_fluid = %s, medication = %s, blood_pressure = %s, sugar_level = %s, notes = %s
"""

UPSERT_CYCLE_ACTIVE_ONLY = """
    INSERT INTO cycle_logs (user_id, log_date, period) 
    VALUES (%s, %s, 'Heavy')
    ON DUPLICATE KEY UPDATE period = 'Heavy'
"""

EXPORT_CYCLE_DATA = """
    SELECT log_date, period, mood, symptoms, cervical_fluid, 
           medication, blood_pressure, sugar_level, notes 
    FROM cycle_logs 
    WHERE user_id = %s 
    ORDER BY log_date DESC
"""

DELETE_CYCLE = """
    DELETE FROM cycle_logs WHERE user_id = %s AND log_date = %s
"""

DELETE_JOURNAL = """
    DELETE FROM journal_logs WHERE id = %s AND user_id = %s
"""

# ==========================================
# 12. DASHBOARD ANALYTICS & CLINICAL TRENDS
# ==========================================

GET_RISK_TRENDS = """
    SELECT 
        DATE_FORMAT(created_at, '%b') AS month_name,
        MONTH(created_at) AS month_num,
        risk_level,
        COUNT(*) as total_count
    FROM predictions
    WHERE YEAR(created_at) = YEAR(CURRENT_DATE) 
        AND risk_level IN ('Low Risk', 'Medium Risk', 'High Risk')
    GROUP BY month_num, month_name, risk_level
    ORDER BY month_num;
"""

GET_DEMOGRAPHICS_RISK = """
    WITH AgeGroups AS (
        SELECT 'Adolescents (13-18)' AS age_group, 1 AS sort_order
        UNION ALL SELECT 'Adults (19-30)', 2
        UNION ALL SELECT 'Mid-Life (31-45)', 3
        UNION ALL SELECT 'Older Adults (46+)', 4
        UNION ALL SELECT 'Unknown', 5
    ),
    PatientData AS (
        SELECT 
            CASE 
                WHEN a.numeric_value BETWEEN 13 AND 18 THEN 'Adolescents (13-18)'
                WHEN a.numeric_value BETWEEN 19 AND 30 THEN 'Adults (19-30)'
                WHEN a.numeric_value BETWEEN 31 AND 45 THEN 'Mid-Life (31-45)'
                WHEN a.numeric_value >= 46 THEN 'Older Adults (46+)'
                ELSE 'Unknown'
            END AS age_group,
            p.prediction_id,
            p.risk_level
        FROM predictions p
        JOIN answers a ON p.submission_id = a.submission_id
        JOIN questions q ON a.question_id = q.question_id
        WHERE (q.question_text = 'How old are you?' OR q.feature_name = 'age (yrs)')
          AND a.numeric_value IS NOT NULL
    )
    SELECT 
        ag.age_group,
        COUNT(DISTINCT pd.prediction_id) AS total_respondents,
        COALESCE(ROUND(SUM(CASE WHEN pd.risk_level = 'High Risk' THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT pd.prediction_id), 0) * 100, 0), 0) AS high_risk_pct
    FROM AgeGroups ag
    LEFT JOIN PatientData pd ON ag.age_group = pd.age_group
    GROUP BY ag.age_group, ag.sort_order
    ORDER BY ag.sort_order;
"""

GET_BMI_CYCLE = """
    SELECT 
        s.submission_id,
        MAX(CASE WHEN q.question_text = 'Enter your weight (kg)' THEN a.numeric_value END) / 
        POWER(MAX(CASE WHEN q.question_text = 'Enter your height (cm)' THEN a.numeric_value END) / 100.0, 2) AS bmi,
        
        MAX(CASE WHEN q.question_text = 'Is your cycle regular or irregular?' 
                 THEN COALESCE(o.option_text, a.text_value) END) AS cycle_data
    FROM submissions s
    JOIN answers a ON s.submission_id = a.submission_id
    JOIN questions q ON a.question_id = q.question_id
    LEFT JOIN options o ON a.selected_option_id = o.option_id
    GROUP BY s.submission_id
    HAVING bmi IS NOT NULL AND cycle_data IS NOT NULL;
"""

GET_SYMPTOMS = """
    SELECT 
        q.feature_name AS symptom,
        COUNT(*) AS count
    FROM answers a
    JOIN questions q ON a.question_id = q.question_id
    LEFT JOIN options o ON a.selected_option_id = o.option_id
    WHERE q.feature_name IN ('pimples', 'weight_gain', 'skin_darkening', 'hirsutism', 'hair_loss')
      AND (o.option_value = 1 OR o.option_text = 'Yes' OR a.numeric_value = 1)
    GROUP BY q.feature_name;
"""

GET_KPIS = """
    SELECT 
        (SELECT COUNT(*) FROM users) AS total_users,
        (SELECT COUNT(*) FROM submissions WHERE DATE(submitted_at) = CURRENT_DATE) AS daily_checkins,
        (SELECT COUNT(*) FROM predictions) AS total_assessments;
"""

# ==========================================
# 13. GAMIFICATION (STREAKS & VITALITY)
# ==========================================

GET_USER_VITALITY_STATS = """
    SELECT streak, total_vitality, last_login 
    FROM user_stats 
    WHERE user_id = %s
"""

UPSERT_USER_VITALITY = """
    INSERT INTO user_stats (user_id, streak, total_vitality, last_login) 
    VALUES (%s, %s, %s, CURRENT_DATE)
    ON DUPLICATE KEY UPDATE 
        streak = VALUES(streak), 
        total_vitality = VALUES(total_vitality), 
        last_login = CURRENT_DATE
"""

GET_USER_QUEST_HISTORY = """
    SELECT 
        quest_name, 
        points_earned, 
        DATE_FORMAT(completed_at, '%Y-%m-%d') as completed_on
    FROM quest_logs  -- Change this table name to match your actual database schema
    WHERE user_id = %s
    ORDER BY completed_at DESC
"""

# ==========================================
# 14. PRO MONITOR (PATIENT CLINICAL VIEW)
# ==========================================

# Returns one row per question per submission, with submitted_at exposed.
# Answer priority in the page: option_text > numeric_value > text_value
GET_USER_QUESTIONNAIRE = """
    SELECT
        s.submitted_at,
        q.question_text,
        q.feature_name,
        o.option_text,
        a.numeric_value,
        a.text_value
    FROM submissions s
    JOIN answers a ON s.submission_id = a.submission_id
    JOIN questions q ON a.question_id = q.question_id
    LEFT JOIN options o ON a.selected_option_id = o.option_id
    WHERE s.user_id = %s
    ORDER BY s.submitted_at DESC, q.question_order ASC
"""

# Only returns cycle_log rows that have at least one meaningful entry
# (i.e. not just the default 'Nothing'/'Neutral' placeholders).
GET_USER_PERIOD_LOGS = """
    SELECT log_date, period, mood, symptoms, cervical_fluid,
           blood_pressure, sugar_level, notes
    FROM cycle_logs
    WHERE user_id = %s
      AND NOT (
            (period IS NULL OR period = 'Nothing')
        AND (mood IS NULL OR mood = 'Neutral')
        AND (symptoms IS NULL OR symptoms = '')
        AND (cervical_fluid IS NULL OR cervical_fluid = '')
        AND (blood_pressure IS NULL OR blood_pressure = '')
        AND (sugar_level IS NULL OR sugar_level = '')
        AND (notes IS NULL OR notes = '')
      )
    ORDER BY log_date DESC
    LIMIT 50
"""

# Fetches vitality points and login streak from user_stats.
GET_USER_QUEST_SCORE = """
    SELECT streak, total_vitality, last_login
    FROM user_stats
    WHERE user_id = %s
"""

# ==========================================
# 15. CLINICAL NOTES
# ==========================================

GET_CLINICAL_NOTES = """
    SELECT 
        note_id,
        title,
        content,
        DATE_FORMAT(created_at, '%b %d, %Y') AS created_at
    FROM clinical_notes
    WHERE patient_id = %s AND doctor_id = %s
    ORDER BY created_at DESC
"""

INSERT_CLINICAL_NOTE = """
    INSERT INTO clinical_notes (doctor_id, patient_id, title, content)
    VALUES (%s, %s, %s, %s)
"""

DELETE_CLINICAL_NOTE = """
    DELETE FROM clinical_notes WHERE note_id = %s AND doctor_id = %s
"""

UPDATE_CLINICAL_NOTE = """
    UPDATE clinical_notes
    SET title = %s, content = %s
    WHERE note_id = %s AND doctor_id = %s
"""

GET_EXERCISE_CYCLE = """
    SELECT 
        s.submission_id,
        -- Grab the Yes/No answer for Exercise
        MAX(CASE WHEN q.question_text IN ('Do you excersize regularly?', 'Do you exercise regularly?') 
                 THEN COALESCE(o.option_text, a.text_value) END) AS exercise,
                 
        -- Grab the Regular/Irregular answer for Cycle
        MAX(CASE WHEN q.question_text = 'Is your cycle regular or irregular?' 
                 THEN COALESCE(o.option_text, a.text_value) END) AS cycle_data
    FROM submissions s
    JOIN answers a ON s.submission_id = a.submission_id
    JOIN questions q ON a.question_id = q.question_id
    LEFT JOIN options o ON a.selected_option_id = o.option_id
    GROUP BY s.submission_id
    -- Only keep users who answered both questions
    HAVING exercise IS NOT NULL AND cycle_data IS NOT NULL;
"""