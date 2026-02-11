from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import os

app = FastAPI()

# Set up Jinja2 templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(BASE_DIR, "app", "templates")
env = Environment(loader=FileSystemLoader(templates_dir))


@app.get("/", response_class=HTMLResponse)
async def get_form():
    template = env.get_template("form.html")
    return template.render()


@app.get("/health")
def health_check():
    return {"status": "ok"}
