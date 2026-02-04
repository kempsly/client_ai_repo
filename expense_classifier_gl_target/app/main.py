from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.prediction import predict_gl_account
import os
import uuid
import tempfile
from typing import Optional

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Directory to save uploaded files temporarily
UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Web Interface
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/predict-web/", response_class=HTMLResponse)
async def predict_web(request: Request, file: UploadFile = File(...)):
    try:
        # Save the uploaded file temporarily
        file_extension = file.filename.split(".")[-1]
        temp_filename = f"{uuid.uuid4()}.{file_extension}"
        temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)

        with open(temp_filepath, "wb") as buffer:
            buffer.write(await file.read())

        # Define output file path with "prediction_" prefix and original filename
        original_filename = os.path.splitext(file.filename)[0]
        output_filename = f"prediction_{original_filename}.xlsx"
        output_filepath = os.path.join(UPLOAD_DIR, output_filename)

        # Predict G/L Account No
        predict_gl_account(temp_filepath, output_filepath)

        # Render the download page
        return templates.TemplateResponse("download.html", {
            "request": request,
            "filename": output_filename
        })
    except Exception as e:
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)  # Use the original output filename

# API Interface (for Swagger UI)
@app.post("/predict-api/", response_class=FileResponse)
async def predict_api(file: UploadFile = File(...)):
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        file_extension = file.filename.split(".")[-1]
        temp_filename = f"{uuid.uuid4()}.{file_extension}"
        temp_filepath = os.path.join(temp_dir, temp_filename)

        # Save the uploaded file
        with open(temp_filepath, "wb") as buffer:
            buffer.write(await file.read())

        # Define output file path with "prediction_" prefix and original filename
        original_filename = os.path.splitext(file.filename)[0]
        output_filename = f"prediction_{original_filename}.xlsx"
        output_filepath = os.path.join(temp_dir, output_filename)

        # Predict G/L Account No
        predict_gl_account(temp_filepath, output_filepath)

        # Return the processed file directly with the custom filename
        return FileResponse(
            path=output_filepath,
            filename=output_filename,  # Use the custom filename for download
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



#######MAKING PREDICTION JUST UNDER DOCS/

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.responses import FileResponse
# import os
# import uuid
# import tempfile

# app = FastAPI()

# # Directory to save uploaded files temporarily
# UPLOAD_DIR = tempfile.mkdtemp()

# @app.post("/predict/")
# async def predict(file: UploadFile = File(...)):
#     try:
#         # Save the uploaded file temporarily
#         file_extension = file.filename.split(".")[-1]
#         temp_filename = f"{uuid.uuid4()}.{file_extension}"
#         temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)

#         with open(temp_filepath, "wb") as buffer:
#             buffer.write(await file.read())

#         # Define output file path
#         output_filename = f"predicted_{temp_filename}"
#         output_filepath = os.path.join(UPLOAD_DIR, output_filename)

#         # Predict G/L Account No
#         from app.services.prediction import predict_gl_account
#         predict_gl_account(temp_filepath, output_filepath)

#         # Return the processed file directly with a custom filename
#         return FileResponse(
#             path=output_filepath,
#             filename="prediction.xlsx",  # Custom filename for download
#             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))






########### FOR UI UPLOAD######################
# from fastapi import FastAPI, UploadFile, File, HTTPException, Request
# from fastapi.responses import HTMLResponse, FileResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from app.services.prediction import predict_gl_account
# import os
# import uuid

# app = FastAPI()

# # Mount static files
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# # Setup templates
# templates = Jinja2Templates(directory="app/templates")

# # Directory to save uploaded files temporarily
# UPLOAD_DIR = "app/static/uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("upload.html", {"request": request})

# @app.post("/predict/", response_class=HTMLResponse)
# async def predict(request: Request, file: UploadFile = File(...)):
#     try:
#         # Save the uploaded file temporarily
#         file_extension = file.filename.split(".")[-1]
#         temp_filename = f"{uuid.uuid4()}.{file_extension}"
#         temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)

#         with open(temp_filepath, "wb") as buffer:
#             buffer.write(await file.read())

#         # Define output file path
#         output_filename = f"predicted_{temp_filename}"
#         output_filepath = os.path.join(UPLOAD_DIR, output_filename)

#         # Predict G/L Account No
#         predict_gl_account(temp_filepath, output_filepath)

#         # Render the download page
#         return templates.TemplateResponse("download.html", {
#             "request": request,
#             "filename": output_filename
#         })
#     except Exception as e:
#         return templates.TemplateResponse("upload.html", {
#             "request": request,
#             "error": str(e)
#         })

# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(file_path, filename=filename)



