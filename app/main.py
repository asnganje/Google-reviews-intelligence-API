from fastapi import FastAPI

app = FastAPI(
    title="Google Reviews Intelligence API",
    description=(
        "A platform for collecting, managing, "
        "and analysing customer reviews."
    ),
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "msg":"Google Reviews Intelligence API is running!"
    }