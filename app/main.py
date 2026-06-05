from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Smart Grid Load Balancing API"}