import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "app.main:app", host="127.0.0.1", port=8000, log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()
