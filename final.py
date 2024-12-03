import pandas as pd

def load_disease_data(filepath):
    """
    Load disease data from an Excel file.
    """
    try:
        data = pd.read_excel(filepath)
        disease_mapping = {}
        remedies_mapping = {}

        # Prepare the mapping for diseases and remedies
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

        return disease_mapping, remedies_mapping

    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None

def find_disease_and_remedy(user_symptoms, disease_mapping, remedies_mapping):
    """
    Find the disease based on user input symptoms and return disease name and remedies.
    """
    user_symptoms_set = set([symptom.lower() for symptom in user_symptoms if symptom.lower() != 'nil'])

    best_match = None
    best_match_score = 0
    remedies = None  # Initialize remedies variable to avoid reference error

    # Iterate through disease_mapping to check for matching symptoms
    for disease, symptoms in disease_mapping.items():
        # Count how many symptoms match
        matched_symptoms = user_symptoms_set.intersection(set([symptom.lower() for symptom in symptoms]))
        match_score = len(matched_symptoms)

        if match_score >= 3:  # At least 3 symptoms need to match
            if match_score > best_match_score:
                best_match = disease
                best_match_score = match_score
                remedies = remedies_mapping[disease]

    # If no match was found, return None for both disease and remedies
    if best_match is None:
        return None, None

    return best_match, remedies

def update_remedies(filepath, disease, remedy_index):
    """
    Update Ayurvedic Remedies in the Excel file based on user feedback.
    Remedy with remedy_index is promoted to the first position.
    """
    try:
        # Load data from the Excel file
        data = pd.read_excel(filepath)

        # Locate the row for the disease
        disease_row = data[data['Disease'].str.lower() == disease.lower()].index

        if not disease_row.empty:
            row_idx = disease_row[0]  # Get the row index
            # Remedy columns
            remedy_cols = ['Ayurvedic Remedy 1', 'Ayurvedic Remedy 2', 'Ayurvedic Remedy 3']

            # Swap remedies: Make the remedy that worked Remedy 1
            current_remedy = data.loc[row_idx, remedy_cols[remedy_index - 1]]
            first_remedy = data.loc[row_idx, remedy_cols[0]]
            data.loc[row_idx, remedy_cols[remedy_index - 1]] = first_remedy
            data.loc[row_idx, remedy_cols[0]] = current_remedy

            # Save the updated Excel file
            data.to_excel(filepath, index=False)
            print(f"Remedies updated successfully in the Excel file: {filepath}")
        else:
            print("Disease not found in the dataset.")

    except Exception as e:
        print(f"Error updating remedies: {e}")

def main():
    # Filepath to the Excel sheet with disease data
    filepath = 'final.xlsx'

    # Load data from the Excel file
    disease_mapping, remedies_mapping = load_disease_data(filepath)
    if disease_mapping is None or remedies_mapping is None:
        print("Unable to load disease data. Exiting.")
        return

    # Take user input for symptoms
    user_symptoms = []
    print("Please enter your symptoms (type 'done' when finished):")
    for i in range(5):
        symptom = input(f"Enter symptom {i+1}: ")
        if symptom.lower() == 'done':
            break
        user_symptoms.append(symptom)

    # Find the disease and remedies based on symptoms
    disease, remedies = find_disease_and_remedy(user_symptoms, disease_mapping, remedies_mapping)

    if disease:
        print(f"\nThe disease predicted is: {disease.capitalize()}")
        print("Suggested Ayurvedic Remedies:")
        for idx, remedy in enumerate(remedies, 1):
            (f"{idx}. {remedy.capitalize()}")
    else:
        print("No matching disease found. Please try again with different symptoms.")
        return

    # User feedback loop for remedies
    for i, remedy in enumerate(remedies, 1):
        feedback = input(f"\nTry this Ayurvedic Remedy {remedy.capitalize()}, Did it work? (y/n): ").strip().lower()
        if feedback == 'y':
            print("Great! Updating priority for future predictions.")
            if i > 1:  # Remedy 2 or 3 worked; update Excel
                update_remedies(filepath, disease, i)
            break
        elif feedback == 'n' and i < len(remedies):
            print(f"Trying next remedy: {remedies[i].capitalize()}")
        elif feedback == 'n' and i == len(remedies):
            print("We tried to help. Please visit a nearby doctor for further assistance.")
            break

if __name__ == '__main__':
    main()
