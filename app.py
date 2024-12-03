from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

def load_disease_data(filepath):
    try:
        data = pd.read_excel(filepath)
        disease_mapping = {}
        remedies_mapping = {}

        for _, row in data.iterrows():
            disease = row['Disease'].strip().lower()
            symptoms = [
                str(row[f'Symptom {i}']).strip().lower()
                for i in range(1, 6) if not pd.isna(row[f'Symptom {i}'])
            ]
            remedies = [
                str(row[f'Ayurvedic Remedy {i}']).strip()
                for i in range(1, 4) if not pd.isna(row[f'Ayurvedic Remedy {i}'])
            ]
            disease_mapping[disease] = symptoms
            remedies_mapping[disease] = remedies

        return disease_mapping, remedies_mapping

    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def clean_user_symptoms(user_symptoms):
    cleaned_symptoms = []
    for symptom in user_symptoms:
        clean_symptom = ''.join(e for e in symptom if e.isalnum() or e.isspace()).strip().lower()
        if clean_symptom:
            cleaned_symptoms.append(clean_symptom)
    return cleaned_symptoms

def find_disease_and_remedy(user_symptoms, disease_mapping, remedies_mapping):
    user_symptoms = clean_user_symptoms(user_symptoms)
    if not user_symptoms:
        return []

    matching_diseases = []

    for disease, symptoms in disease_mapping.items():
        matched_symptoms = [symptom for symptom in user_symptoms if symptom in symptoms]
        match_score = len(matched_symptoms)

        if match_score >= 3:
            matching_diseases.append((disease, match_score))

    matching_diseases.sort(key=lambda x: x[1], reverse=True)

    results = [
        {"disease": disease, "remedies": remedies_mapping[disease]}
        for disease, _ in matching_diseases
    ]
    return results

def update_remedies(filepath, disease, remedy_index):
    try:
        data = pd.read_excel(filepath)
        disease_row = data[data['Disease'].str.lower() == disease.lower()].index

        if not disease_row.empty:
            row_idx = disease_row[0]
            remedy_cols = ['Ayurvedic Remedy 1', 'Ayurvedic Remedy 2', 'Ayurvedic Remedy 3']
            current_remedy = data.loc[row_idx, remedy_cols[remedy_index - 1]]
            first_remedy = data.loc[row_idx, remedy_cols[0]]
            data.loc[row_idx, remedy_cols[remedy_index - 1]] = first_remedy
            data.loc[row_idx, remedy_cols[0]] = current_remedy

            data.to_excel(filepath, index=False)
            print(f"Remedies updated successfully in the Excel file: {filepath}")
        else:
            print("Disease not found in the dataset.")
    except Exception as e:
        print(f"Error updating remedies: {e}")

@app.route('/predict', methods=['POST'])
def predict():
    filepath = 'yoyo.xlsx'
    user_symptoms = request.json.get('symptoms', [])
    
    disease_mapping, remedies_mapping = load_disease_data(filepath)
    if disease_mapping is None or remedies_mapping is None:
        return jsonify({"error": "Unable to load disease data"}), 500
    
    results = find_disease_and_remedy(user_symptoms, disease_mapping, remedies_mapping)
    if not results:
        return jsonify({"message": "No matching disease found"}), 404

    return jsonify(results), 200

@app.route('/feedback', methods=['POST'])
def feedback():
    filepath = 'yoyo.xlsx'
    data = request.json
    disease = data.get('disease')
    remedy_index = data.get('remedy_index')

    if not disease or not remedy_index:
        return jsonify({"message": "Feedback received and remedies updated successfully"}), 400

    update_remedies(filepath, disease, remedy_index)
    return jsonify({"message": "Feedback received and remedies updated successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
