from fastapi import FastAPI

app = FastAPI(title="Materials Curve Dataset Platform API", version="0.1.0")


@app.get('/health')
def health() -> dict[str, str]:
    return {"status": "ok", "service": "materials-curve-backend"}
