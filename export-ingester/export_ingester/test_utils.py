from fastapi import FastAPI

app = FastAPI()


@app.get("/api/1/exports")
def get_exports():
    return [{"hello": "world"}]
