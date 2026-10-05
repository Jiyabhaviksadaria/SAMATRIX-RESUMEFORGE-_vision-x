import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import health, dataset, train, predict, analyze, match, metrics, demo, classify
from backend.schemas import StandardResponse

app = FastAPI(
    title="ResumeForge AI",
    description="Resume Intelligence Hackathon Starter Kit API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler returning standardized JSON
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=StandardResponse(
            success=False,
            error={
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc)
            }
        ).model_dump()
    )

# Register routes
app.include_router(health.router)
app.include_router(dataset.router)
app.include_router(train.router)
app.include_router(predict.router)
app.include_router(analyze.router)
app.include_router(match.router)
app.include_router(metrics.router)
app.include_router(demo.router)
app.include_router(classify.router)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("backend.main:app", host=host, port=port, reload=True)
