from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import auth, calendar, notes, projects, todos, uploads

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Notes App API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(notes.router)
app.include_router(todos.router)
app.include_router(uploads.router)
app.include_router(calendar.router)


@app.get("/health")
def health():
    return {"status": "ok"}
