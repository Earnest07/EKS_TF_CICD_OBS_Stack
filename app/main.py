from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.config import (
    APP_NAME,
    APP_VERSION,
    APP_ENVIRONMENT,
)


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>{APP_NAME}</title>

        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 0;
            }}

            .container {{
                max-width: 800px;
                margin: 80px auto;
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }}

            h1 {{
                margin-bottom: 10px;
            }}

            .version {{
                font-size: 28px;
                font-weight: bold;
                margin: 20px 0;
            }}

            .environment {{
                color: #555;
                font-size: 18px;
            }}

            .status {{
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                border-radius: 6px;
                background: #e8f5e9;
                color: #2e7d32;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <h1>{APP_NAME}</h1>

            <div class="version">
                Version {APP_VERSION}
            </div>

            <div class="environment">
                Environment: {APP_ENVIRONMENT}
            </div>

            <div class="status">
                Application is running
            </div>

        </div>

    </body>
    </html>
    """


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
    }


@app.get("/version")
def version():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
    }