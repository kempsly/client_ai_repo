import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

    GL_ACCOUNT_MAP = {
        "54820": "Personal Expenses on Bus. CC",
        "61100": "Marketing",
        "61110": "Hotel Charges",
        "61120": "Airfares",
        "61130": "Taxi Fares",
        "61131": "Car Rental Charges & Parking",
        "61133": "Train fares",
        "61200": "Entertainment and PR",
        "61215": "Meals",
        "63100": "Gasoline and Motor Oil",
        "64100": "Software",
        "64101": "Hardware",
        "64200": "Consultant Services",
        "64210": "Consultant Svcs not deducted",
        "64215": "Accounting & Legal Services",
        "65600": "Office Supplies",
        "65700": "Phone and Fax",
        "67500": "Other Costs of Operations",
        "80100": "Credit Card Interest and Fees"
    }
