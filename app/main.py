from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Get the directory of this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/")
async def get_form():
    form_path = os.path.join(BASE_DIR, "app", "templates", "form.html")
    return FileResponse(form_path)


@app.get("/health")
def health_check():
    return {"status": "ok"}
