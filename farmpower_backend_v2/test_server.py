from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Test Server</title>
        </head>
        <body>
            <h1>Test Server is Working!</h1>
        </body>
    </html>
    """ 