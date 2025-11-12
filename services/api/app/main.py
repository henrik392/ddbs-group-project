from fastapi import FastAPI
app = FastAPI(title="DDBS API")
@app.get("/health")
def health():
    return {"status": "ok"}
