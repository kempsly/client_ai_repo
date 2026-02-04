import joblib
import os

# Paths to the saved model and encoder
MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/best_gl_account_model.pkl")
ENCODER_PATH = os.path.join(os.path.dirname(__file__), "../../models/label_encoder.pkl")

# Load the model and encoder
model = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
