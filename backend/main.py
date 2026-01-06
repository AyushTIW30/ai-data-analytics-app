from fastapi import FastAPI

app = FastAPI(title="AIDataApp API")

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}
