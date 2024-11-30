from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello_world():
    return "hello world"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
