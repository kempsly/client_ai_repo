import pandas as pd
from app.utils.logger import logger

def process_excel_file(file_path):
    """Read and process the Excel file."""
    try:
        df = pd.read_excel(file_path)
        logger.info(f"Successfully read Excel file: {file_path}")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel file: {e}")
        raise

def save_predictions(df, predictions, output_filepath):
    """Save the DataFrame with predictions to an Excel file."""
    try:
        # Add new columns to the DataFrame
        df["Predicted GL Account"] = [prediction["gl_account_number"] for prediction in predictions]
        df["Confidence Score"] = [prediction["confidence_score"] for prediction in predictions]
        df["Alternative GL Account"] = [prediction["alternative_gl_account_number"] for prediction in predictions]
        df["Reasoning"] = [prediction["reasoning"] for prediction in predictions]

        df.to_excel(output_filepath, index=False)
        logger.info(f"Successfully saved predictions to: {output_filepath}")
    except Exception as e:
        logger.error(f"Error saving predictions: {e}")
        raise
