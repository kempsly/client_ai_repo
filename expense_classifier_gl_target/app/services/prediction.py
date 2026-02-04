import pandas as pd
import numpy as np
from app.models.model import model, label_encoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

# Define text columns and preprocessor
text_columns = ["Description", "Extended Details", "Appears On Your Statement As", "Address", "City/State", "Country", "CC Name"]
preprocessor = ColumnTransformer(
    transformers=[
        ("text", TfidfVectorizer(max_features=100, stop_words="english"), "combined_text"),
        ("num", SimpleImputer(strategy="median"), ["Amount"])
    ]
)

def predict_gl_account(input_file_path: str, output_file_path: str):
    # Load new data
    new_df = pd.read_excel(input_file_path)

    # Check if required columns exist
    required_columns = text_columns + ["Amount"]
    missing_columns = [col for col in required_columns if col not in new_df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns in input data: {missing_columns}")

    # Preprocess new data
    new_df["combined_text"] = new_df[text_columns].fillna("").agg(" ".join, axis=1)
    X_new = new_df[["combined_text", "Amount"]]

    # Predict G/L Account No
    y_new_encoded = model.predict(X_new)
    y_new_proba = model.predict_proba(X_new)

    # Get top 2 predictions and their probabilities
    top2_indices = np.argsort(y_new_proba, axis=1)[:, -2:]
    top2_proba = np.take_along_axis(y_new_proba, top2_indices, axis=1)

    # Inverse transform each column of top2_indices separately
    top2_labels = np.empty(top2_indices.shape, dtype=object)
    for i in range(top2_indices.shape[1]):
        top2_labels[:, i] = label_encoder.inverse_transform(top2_indices[:, i])

    # Add predictions to new DataFrame
    new_df["Predicted GL Account No"] = label_encoder.inverse_transform(y_new_encoded)
    new_df["Confidence Score"] = top2_proba[:, 1]
    new_df["Alternative GL Account No"] = top2_labels[:, 0]
    new_df["Reasoning"] = new_df.apply(
        lambda row: f"Predicted as '{row['Predicted GL Account No']}' with {row['Confidence Score']:.2f} confidence. "
                    f"Alternative: '{row['Alternative GL Account No']}'.",
        axis=1
    )

    # Save results
    new_df.to_excel(output_file_path, index=False)
    return output_file_path
