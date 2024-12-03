from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load disease data into memory
DATA_FILEPATH = 'final.xlsx'
disease_mapping = {}
remedies_mapping = {}

def load_disease_data(filepath):
    """
    Load disease data from an Excel file.
    """
    global disease_mapping, remedies_mapping
    try:
        data = pd.read_excel(filepath)
        for _, row in data.iterrows():
            disease = row['Disease']
            symptoms = [
                str(row['Symptom 1']).lower(),
                str(row['Symptom 2']).lower(),
                str(row['Symptom 3']).lower(),
                str(row['Symptom 4']).lower(),
                str(row['Symptom 5']).lower(),
            ]
            remedies = [
                str(row['Ayurvedic Remedy 1']).lower(),
                str(row['Ayurvedic Remedy 2']).lower(),
                str(row['Ayurvedic Remedy 3']).lower(),
            ]
            disease_mapping[disease.lower()] = symptoms
            remedies_mapping[disease.lower()] = remedies
    except Exception as e:
        print(f"Error loading data: {e}")

@app.route('/predict', methods=['POST'])
def predict_disease():
    """
    Endpoint to predict the disease based on symptoms.
    """
    try:
        user_symptoms = request.json.get('symptoms', [])
        user_symptoms_set = set([symptom.lower() for symptom in user_symptoms if symptom.lower() != 'nil'])

        best_match = None
        best_match_score = 0
        remedies = None

        # Match symptoms to diseases
        for disease, symptoms in disease_mapping.items():
            matched_symptoms = user_symptoms_set.intersection(set([symptom.lower() for symptom in symptoms]))
            match_score = len(matched_symptoms)

            if match_score >= 3:  # At least 3 symptoms need to match
                if match_score > best_match_score:
                    best_match = disease
                    best_match_score = match_score
                    remedies = remedies_mapping[disease]

        if best_match:
            return jsonify({
                'disease': best_match.capitalize(),
                'remedies': [remedy.capitalize() for remedy in remedies]
            }), 200
        else:
            return jsonify({'error': 'No matching disease found. Please try again with different symptoms.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def update_remedy_priority():
    """
    Endpoint to update remedy priority based on feedback.
    """
    try:
        data = request.json
        disease = data.get('disease', '').lower()
        remedy_index = data.get('remedyIndex', 1)

        # Load the data again to ensure updates are saved correctly
        excel_data = pd.read_excel(DATA_FILEPATH)
        disease_row = excel_data[excel_data['Disease'].str.lower() == disease].index

        if not disease_row.empty:
            row_idx = disease_row[0]
            remedy_cols = ['Ayurvedic Remedy 1', 'Ayurvedic Remedy 2', 'Ayurvedic Remedy 3']

            # Swap remedies
            current_remedy = excel_data.loc[row_idx, remedy_cols[remedy_index - 1]]
            first_remedy = excel_data.loc[row_idx, remedy_cols[0]]
            excel_data.loc[row_idx, remedy_cols[remedy_index - 1]] = first_remedy
            excel_data.loc[row_idx, remedy_cols[0]] = current_remedy

            # Save changes back to the file
            excel_data.to_excel(DATA_FILEPATH, index=False)
            return jsonify({'message': 'Remedies updated successfully.'}), 200
        else:
            return jsonify({'error': 'Disease not found in the dataset.'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load data on startup
    load_disease_data(DATA_FILEPATH)
    app.run(debug=True)