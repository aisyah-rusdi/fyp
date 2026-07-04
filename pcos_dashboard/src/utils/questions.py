QUESTIONNAIRE = {
    "general_information": [
        {"id": "How old are you?", "label": "Age (years)", "type": "number", "min_value": 10, "max_value": 100},
        {"id": "How many years have you been married?", "label": "Marriage Status (years)", "type": "number", "min_value": 0},
        {"id": "What is your blood group?", "label": "Blood Group", "type": "radio", "options": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]},
        {"id": "Enter your weight (kg)", "label": "Weight (kg)", "type": "number", "min_value": 20.0, "max_value": 250.0},
        {"id": "Enter your height (cm)", "label": "Height (cm)", "type": "number", "min_value": 100.0, "max_value": 250.0},
        {"id": "Calculate your BMI", "label": "BMI", "type": "calculated", "calc_rule": "bmi"},
        {"id": "Enter your hip circumference (inch)", "label": "Hip (inch)", "type": "number", "min_value": 10.0},
        {"id": "Enter your waist circumference (inch)", "label": "Waist (inch)", "type": "number", "min_value": 10.0},
        {"id": "Calculate your Waist-Hip Ratio", "label": "Waist–Hip Ratio", "type": "calculated", "calc_rule": "whr"}
    ],
    "physical_symptoms": [
        {"id": "Enter your pulse rate (bpm)", "label": "Pulse Rate (bpm)", "type": "number", "min_value": 30.0, "max_value": 250.0},
        {"id": "Enter your respiratory rate (breaths/min)", "label": "Respiratory Rate (breaths/min)", "type": "number", "min_value": 10.0, "max_value": 80.0},
        {"id": "Enter your systolic blood pressure (mmHg)", "label": "BP Systolic (mmHg)", "type": "number", "min_value": 70.0, "max_value": 250.0},
        {"id": "Enter your diastolic blood pressure (mmHg)", "label": "BP Diastolic (mmHg)", "type": "number", "min_value": 40.0, "max_value": 150.0},
        {"id": "Enter your cycle length (days)", "label": "Cycle Length (days)", "type": "number", "min_value": 2.0, "max_value": 365.0},
        
        # --- MULTIPLE FOLLOW-UPS ---
        {"id": "Is your cycle regular or irregular?", "label": "Cycle (Regular/Irregular)", "type": "radio", "options": ["Regular", "Irregular"],
         "follow_up": {
             "condition": "Irregular",
             "questions": [
                 # These are allowed to be 0!
                 {"id": "Maximum days?", "type": "number", "min_value": 0.0},
                 {"id": "Minimum days?", "type": "number", "min_value": 0.0},
                 {"id": "Usual gaps (days)?", "type": "number", "min_value": 0.0},
                 {"id": "Maximum gap (days)?", "type": "number", "min_value": 0.0},
                 {"id": "Minimum gap (days)?", "type": "number", "min_value": 0.0}
             ]
         }},
         
        # --- TEXT FOLLOW-UPS ---
        {"id": "Do you notice any skin darkening? (armpits, thighs, neck, etc)", "label": "Any skin darkening noticed?", "type": "radio", "options": ["Yes", "No"],
         "follow_up": {
             "condition": "Yes",
             "questions": [{"id": "Where? (e.g., armpits, thighs, neck)", "type": "text"}]
         }},
        
        {"id": "Do you notice any abrupt weight gain?", "label": "Recent unexplained weight gain?", "type": "radio", "options": ["Yes", "No"],
         "follow_up": {
             "condition": "Yes", 
             "questions": [{"id": "How much weight do you think you gained? (kg)", "type": "number", "min_value": 1.0}]
         }},
        
        {"id": "Do you notice hair growth at unexpected places? (chin, upper lip, abdomen, etc)", "label": "Excessive hair growth (Hirsutism)?", "type": "radio", "options": ["Yes", "No"],
         "follow_up": {
             "condition": "Yes",
             "questions": [{"id": "Where? (e.g., chin, upper lip, abdomen)", "type": "text"}]
         }},
         
        {"id": "Do you have frequent pimples/acne?", "label": "Frequent pimples/acne?", "type": "radio", "options": ["Yes", "No"]},
        {"id": "Do you have significant hair loss/thinning?", "label": "Significant hair loss/thinning?", "type": "radio", "options": ["Yes", "No"]}
    ],
    "lifestyle_medical_history": [
         {"id": "How many abortions have you had?", "label": "Number of Abortions", "type": "number", "min_value": 0},
         {"id": "Are you currently pregnant?", "label": "Are you currently pregnant?", "type": "radio", "options": ["Yes", "No"]},
         
         {"id": "Do you eat Fast Food often?", "label": "Do you consume fast food regularly?", "type": "radio", "options": ["Yes", "No"],
          "follow_up": {
             "condition": "Yes",
             "questions": [{"id": "How many times a week?", "type": "number", "min_value": 0}]
         }},
         
         {"id": "Do you excersize regularly?", "label": "Do you exercise regularly?", "type": "radio", "options": ["Yes", "No"],
          "follow_up": {
             "condition": "Yes",
             "questions": [{"id": "How many times a week?", "type": "number", "min_value": 0}]
         }}
    ]
}