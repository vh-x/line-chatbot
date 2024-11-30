from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return JSONResponse(content={"status": "OK"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
