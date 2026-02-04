from app.utils.logger import logger
import uuid
import json
import os
import time

class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.tasks_dir = "app/static/tasks"
        os.makedirs(self.tasks_dir, exist_ok=True)
    
    def create_task(self, filename, total_rows):
        """Create a new task and save it to disk"""
        task_id = str(uuid.uuid4())
        task_data = {
            "task_id": task_id,
            "filename": filename,
            "status": "processing",
            "progress": 0,
            "total_rows": total_rows,
            "processed_rows": 0,
            "start_time": time.time(),
            "result_file": None,
            "error": None
        }
        
        self.tasks[task_id] = task_data
        self._save_task(task_id)
        return task_id
    
    def update_progress(self, task_id, processed_rows):
        """Update task progress"""
        if task_id in self.tasks:
            self.tasks[task_id]["processed_rows"] = processed_rows
            self.tasks[task_id]["progress"] = int((processed_rows / self.tasks[task_id]["total_rows"]) * 100)
            self._save_task(task_id)
    
    def complete_task(self, task_id, result_file):
        """Mark task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "completed"
            self.tasks[task_id]["result_file"] = result_file
            self.tasks[task_id]["progress"] = 100
            self._save_task(task_id)
    
    def fail_task(self, task_id, error_message):
        """Mark task as failed"""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = "failed"
            self.tasks[task_id]["error"] = error_message
            self._save_task(task_id)
    
    def get_task(self, task_id):
        """Get task status"""
        if task_id in self.tasks:
            return self.tasks[task_id]
        # Try to load from disk
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        if os.path.exists(task_file):
            with open(task_file, 'r') as f:
                return json.load(f)
        return None
    
    def _save_task(self, task_id):
        """Save task data to disk"""
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        with open(task_file, 'w') as f:
            json.dump(self.tasks[task_id], f, indent=2)

# Global task manager instance
task_manager = TaskManager()