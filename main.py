import uvicorn
from os import getenv

if __name__ == "__main__":
    port = int(getenv("PORT", 4444))
    uvicorn.run("app.web:app", host="127.0.0.1", port=port, reload=True)

    # uvicorn.run(
    #     "app.web:app",
    #     host="0.0.0.0",
    #     port=4444
    #     , log_level="critical", access_log=False,workers=4,reload=True)
