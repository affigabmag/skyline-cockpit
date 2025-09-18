from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="My FastAPI App", version="1.0.0")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id, "name": f"User {user_id}"}


@app.post("/users")
def create_user(name: str, email: str):
    return {"message": "User created", "name": name, "email": email}


@app.get("/docs-html", response_class=HTMLResponse)
def custom_docs():
    return """
    <html>
        <head>
            <title>FastAPI Docs</title>
        </head>
        <body>
            <h1>Welcome to FastAPI!</h1>
            <p>Visit <a href="/docs">/docs</a> for interactive API documentation</p>
            <p>Visit <a href="/redoc">/redoc</a> for alternative documentation</p>
        </body>
    </html>
    """