from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.llm_service import predict_gl_account
from app.services.file_service import process_excel_file, save_predictions
from app.services.task_service import task_manager
from app.utils.helpers import validate_file_extension
from app.utils.logger import logger
import os
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Directory to save uploaded files temporarily
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_file_background(temp_filepath, original_filename, task_id):
    """Background task to process the file"""
    try:
        # Process the Excel file
        df = process_excel_file(temp_filepath)
        total_rows = len(df)
        
        # Update task with total rows
        task_manager.tasks[task_id]["total_rows"] = total_rows
        
        # Process rows in batches to update progress
        predictions = []
        batch_size = max(1, total_rows // 10)  # Update progress 10 times
        
        for i, (idx, row) in enumerate(df.iterrows()):
            try:
                prediction = predict_gl_account(row.to_dict())
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Failed to process row {idx}: {str(e)}")
                predictions.append({
                    "gl_account_number": "ERROR",
                    "confidence_score": "0.0",
                    "alternative_gl_account_number": "",
                    "reasoning": f"Error: {str(e)[:100]}"
                })
            
            # Update progress every batch or at the end
            if (i + 1) % batch_size == 0 or (i + 1) == total_rows:
                task_manager.update_progress(task_id, i + 1)
        
        # Save predictions
        output_filename = f"prediction_{original_filename}_{task_id}.xlsx"
        output_filepath = os.path.join(UPLOAD_DIR, output_filename)
        save_predictions(df, predictions, output_filepath)
        
        # Mark task as completed
        task_manager.complete_task(task_id, output_filename)
        
        # Clean up temp file after some time
        os.remove(temp_filepath)
        
    except Exception as e:
        logger.error(f"Error in background processing: {e}")
        task_manager.fail_task(task_id, str(e))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/start-prediction/", response_class=HTMLResponse)
async def start_prediction(request: Request, file: UploadFile = File(...)):
    """Start the prediction process and show progress page"""
    try:
        validate_file_extension(file.filename)
        
        # Save the uploaded file temporarily
        file_extension = file.filename.split(".")[-1]
        temp_filename = f"{uuid.uuid4()}.{file_extension}"
        temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)
        
        with open(temp_filepath, "wb") as buffer:
            buffer.write(await file.read())
        
        # Get initial row count for progress tracking
        try:
            df = process_excel_file(temp_filepath)
            total_rows = len(df)
        except:
            total_rows = 100  # Default estimate
        
        # Create a task
        task_id = task_manager.create_task(file.filename, total_rows)
        
        # Start background processing
        import threading
        thread = threading.Thread(
            target=process_file_background,
            args=(temp_filepath, os.path.splitext(file.filename)[0], task_id)
        )
        thread.daemon = True
        thread.start()
        
        # Show processing page
        return templates.TemplateResponse("processing.html", {
            "request": request,
            "task_id": task_id,
            "filename": file.filename
        })
        
    except Exception as e:
        logger.error(f"Error starting prediction: {e}")
        return templates.TemplateResponse("upload.html", {
            "request": request,
            "error": str(e)
        })

@app.get("/processing/{task_id}", response_class=HTMLResponse)
async def check_processing(request: Request, task_id: str):
    """Page that checks processing status"""
    task = task_manager.get_task(task_id)
    
    if not task:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Task not found"
        })
    
    return templates.TemplateResponse("processing.html", {
        "request": request,
        "task_id": task_id,
        "filename": task.get("filename", "Unknown"),
        "task": task
    })

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """API endpoint for checking task status (used by JavaScript)"""
    task = task_manager.get_task(task_id)
    
    if not task:
        return JSONResponse({"status": "not_found"})
    
    return JSONResponse({
        "status": task["status"],
        "progress": task["progress"],
        "processed_rows": task.get("processed_rows", 0),
        "total_rows": task.get("total_rows", 0),
        "result_file": task.get("result_file"),
        "error": task.get("error")
    })

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.get("/redirect-to-home")
async def redirect_to_home():
    return RedirectResponse(url="/", status_code=303)








# from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
# from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from app.services.llm_service import predict_gl_account
# from app.services.file_service import process_excel_file, save_predictions
# from app.utils.helpers import validate_file_extension
# from app.utils.logger import logger
# import os
# import uuid
# from concurrent.futures import ThreadPoolExecutor, as_completed

# app = FastAPI()

# # Mount static files
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# # Setup templates
# templates = Jinja2Templates(directory="app/templates")

# # Directory to save uploaded files temporarily
# UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "static", "uploads")
# os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the directory exists

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("upload.html", {"request": request})

# @app.post("/predict-web/", response_class=HTMLResponse)
# async def predict_web(request: Request, file: UploadFile = File(...)):
#     try:
#         validate_file_extension(file.filename)

#         # Save the uploaded file temporarily
#         file_extension = file.filename.split(".")[-1]
#         temp_filename = f"{uuid.uuid4()}.{file_extension}"
#         temp_filepath = os.path.join(UPLOAD_DIR, temp_filename)

#         logger.info(f"Saving file to: {temp_filepath}")
#         with open(temp_filepath, "wb") as buffer:
#             content = await file.read()
#             buffer.write(content)
        
#         if not content:
#             raise HTTPException(status_code=400, detail="Uploaded file is empty")
            
#         logger.info(f"File saved successfully: {os.path.exists(temp_filepath)}")

#         # Process the Excel file
#         df = process_excel_file(temp_filepath)
        
#         # Check if dataframe is empty
#         if df.empty:
#             raise HTTPException(status_code=400, detail="Excel file is empty or couldn't be read")
        
#         # Limit the number of rows for testing
#         if len(df) > 100:  # You can adjust this limit
#             logger.warning(f"File has {len(df)} rows, processing first 100 rows only")
#             df = df.head(100)

#         # Predict G/L Account No for each row with better error handling
#         predictions = []
#         failed_rows = []
        
#         # Process rows one by one to isolate errors
#         for idx, row in df.iterrows():
#             try:
#                 logger.info(f"Processing row {idx + 1}/{len(df)}")
#                 prediction = predict_gl_account(row.to_dict())
#                 predictions.append(prediction)
#             except Exception as e:
#                 logger.error(f"Failed to process row {idx}: {str(e)}")
#                 # Add a default prediction for failed rows
#                 predictions.append({
#                     "gl_account_number": "ERROR",
#                     "confidence_score": "0.0",
#                     "alternative_gl_account_number": "",
#                     "reasoning": f"Error: {str(e)[:100]}"
#                 })
#                 failed_rows.append(idx + 1)
        
#         # Log any failures
#         if failed_rows:
#             logger.warning(f"Failed to process rows: {failed_rows}")

#         # Save predictions to the DataFrame
#         original_filename = os.path.splitext(file.filename)[0]
#         output_filename = f"prediction_{original_filename}.xlsx"
#         output_filepath = os.path.join(UPLOAD_DIR, output_filename)
#         save_predictions(df, predictions, output_filepath)

#         # Render the download page
#         return templates.TemplateResponse("download.html", {
#             "request": request,
#             "filename": output_filename
#         })
#     except HTTPException as he:
#         raise he
#     except Exception as e:
#         logger.error(f"Error processing file: {e}", exc_info=True)
#         return templates.TemplateResponse("upload.html", {
#             "request": request,
#             "error": f"Error processing file: {str(e)}"
#         })

# @app.get("/download/{filename}")
# async def download_file(filename: str):
#     file_path = os.path.join(UPLOAD_DIR, filename)
#     if not os.path.exists(file_path):
#         raise HTTPException(status_code=404, detail="File not found")
#     return FileResponse(file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# @app.get("/redirect-to-home")
# async def redirect_to_home():
#     return RedirectResponse(url="/", status_code=303)

