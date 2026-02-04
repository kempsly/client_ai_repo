
import openai
import json
from app.config import Config
from app.utils.logger import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import time

openai.api_key = Config.OPENAI_API_KEY

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((openai.error.APIError, openai.error.Timeout, openai.error.RateLimitError))
)
def predict_gl_account(expense_details):
    prompt = f"""
    You are an expert in GAAP accounting. Based on the following expense details, predict the most appropriate G/L account number from the list below.
    Only use the provided G/L account numbers and do not make up any new ones.

    G/L Account Numbers and Descriptions:
    {Config.GL_ACCOUNT_MAP}

    Expense Details:
    Description: {expense_details.get('Description', '')}
    Extended Details: {expense_details.get('Extended Details', '')}
    Appears On Your Statement As: {expense_details.get('Appears On Your Statement As', '')}
    Address: {expense_details.get('Address', '')}
    City/State: {expense_details.get('City/State', '')}
    Country: {expense_details.get('Country', '')}
    CC Name: {expense_details.get('CC Name', '')}
    Amount: {expense_details.get('Amount', '')}

    Provide your response in the following format (do not include any additional text or JSON markers):
    gl_account_number,confidence_score,alternative_gl_account_number,reasoning
    """

    try:
        logger.info(f"Sending request to OpenAI for expense: {expense_details.get('Description', 'N/A')}")
        
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Make sure you have access to GPT-4
            messages=[
                {"role": "system", "content": "You are an expert in GAAP accounting. Always respond in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )

        response_content = response.choices[0].message.content.strip()
        logger.info(f"LLM Response: {response_content}")

        # Split the response into components
        try:
            parts = response_content.split(',', 3)
            if len(parts) != 4:
                raise ValueError(f"Expected 4 parts, got {len(parts)}")
            
            gl_account_number, confidence_score, alternative_gl_account_number, reasoning = parts
            
            return {
                "gl_account_number": gl_account_number.strip(),
                "confidence_score": confidence_score.strip(),
                "alternative_gl_account_number": alternative_gl_account_number.strip(),
                "reasoning": reasoning.strip()
            }
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}. Response was: {response_content}")
            # Return a default response if parsing fails
            return {
                "gl_account_number": "67500",  # Default to "Other Costs of Operations"
                "confidence_score": "0.0",
                "alternative_gl_account_number": "",
                "reasoning": f"Error parsing response: {str(e)}"
            }
            
    except openai.error.InvalidRequestError as e:
        logger.error(f"Invalid request to OpenAI API: {e}")
        # If it's a model access issue, fall back to gpt-3.5-turbo
        if "gpt-4" in str(e).lower():
            logger.info("Falling back to gpt-3.5-turbo")
            return predict_with_gpt35(expense_details)
        raise Exception(f"OpenAI API error: {e}")
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        raise Exception(f"Error calling OpenAI API: {e}")

def predict_with_gpt35(expense_details):
    """Fallback function using GPT-3.5-turbo"""
    prompt = f"""
    You are an expert in GAAP accounting. Based on the following expense details, predict the most appropriate G/L account number from the list below.
    Only use the provided G/L account numbers and do not make up any new ones.

    G/L Account Numbers and Descriptions:
    {Config.GL_ACCOUNT_MAP}

    Expense Details:
    Description: {expense_details.get('Description', '')}
    Extended Details: {expense_details.get('Extended Details', '')}
    Appears On Your Statement As: {expense_details.get('Appears On Your Statement As', '')}
    Address: {expense_details.get('Address', '')}
    City/State: {expense_details.get('City/State', '')}
    Country: {expense_details.get('Country', '')}
    CC Name: {expense_details.get('CC Name', '')}
    Amount: {expense_details.get('Amount', '')}

    Provide your response in the following format (do not include any additional text or JSON markers):
    gl_account_number,confidence_score,alternative_gl_account_number,reasoning
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in GAAP accounting. Always respond in the exact format requested."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        response_content = response.choices[0].message.content.strip()
        parts = response_content.split(',', 3)
        
        if len(parts) == 4:
            gl_account_number, confidence_score, alternative_gl_account_number, reasoning = parts
            return {
                "gl_account_number": gl_account_number.strip(),
                "confidence_score": confidence_score.strip(),
                "alternative_gl_account_number": alternative_gl_account_number.strip(),
                "reasoning": reasoning.strip()
            }
        else:
            # Return default response
            return {
                "gl_account_number": "67500",
                "confidence_score": "0.0",
                "alternative_gl_account_number": "",
                "reasoning": "Fallback response due to parsing error"
            }
    except Exception as e:
        logger.error(f"Error with GPT-3.5 fallback: {e}")
        # Return a safe default response
        return {
            "gl_account_number": "67500",
            "confidence_score": "0.0",
            "alternative_gl_account_number": "",
            "reasoning": f"Error with API: {str(e)[:100]}"
        }


# import openai
# import json
# from app.config import Config
# from app.utils.logger import logger
# from tenacity import retry, stop_after_attempt, wait_exponential

# openai.api_key = Config.OPENAI_API_KEY

# @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
# def predict_gl_account(expense_details):
#     prompt = f"""
#     You are an expert in GAAP accounting. Based on the following expense details, predict the most appropriate G/L account number from the list below.
#     Only use the provided G/L account numbers and do not make up any new ones.

#     G/L Account Numbers and Descriptions:
#     {Config.GL_ACCOUNT_MAP}

#     Expense Details:
#     Description: {expense_details.get('Description', '')}
#     Extended Details: {expense_details.get('Extended Details', '')}
#     Appears On Your Statement As: {expense_details.get('Appears On Your Statement As', '')}
#     Address: {expense_details.get('Address', '')}
#     City/State: {expense_details.get('City/State', '')}
#     Country: {expense_details.get('Country', '')}
#     CC Name: {expense_details.get('CC Name', '')}
#     Amount: {expense_details.get('Amount', '')}

#     Provide your response in the following format (do not include any additional text or JSON markers):
#     gl_account_number,confidence_score,alternative_gl_account_number,reasoning
#     """

#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",  # Using a more robust model
#             messages=[
#                 {"role": "system", "content": "You are an expert in GAAP accounting."},
#                 {"role": "user", "content": prompt}
#             ]
#         )

#         response_content = response.choices[0].message.content.strip()
#         logger.info(f"LLM Response: {response_content}")

#         # Split the response into components
#         gl_account_number, confidence_score, alternative_gl_account_number, reasoning = response_content.split(',', 3)
#         return {
#             "gl_account_number": gl_account_number.strip(),
#             "confidence_score": confidence_score.strip(),
#             "alternative_gl_account_number": alternative_gl_account_number.strip(),
#             "reasoning": reasoning.strip()
#         }
#     except Exception as e:
#         logger.error(f"Error calling OpenAI API: {e}")
#         raise Exception(f"Error calling OpenAI API: {e}")
