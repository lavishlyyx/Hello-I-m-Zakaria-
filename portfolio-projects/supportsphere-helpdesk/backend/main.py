"""Local-only SupportSphere demo API. No authentication: do not deploy publicly."""
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB = Path(__file__).with_name("supportsphere.db")
STATUSES = {"Open", "In Progress", "Resolved", "Closed"}
app = FastAPI(title="SupportSphere Local Demo", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET","POST","PATCH"], allow_headers=["*"])

@contextmanager
def connect():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

with connect() as db:
    db.execute("""CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TEXT NOT NULL
    )""")
    if db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
        db.execute("INSERT INTO tickets(title,description,priority,status,created_at) VALUES (?,?,?,?,?)",
            ("Cannot access company account","Fictional employee reports a sign-in issue.","High","Open",datetime.now(timezone.utc).isoformat()))

class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=5, max_length=2000)
    priority: str = Field(pattern=r"^(Low|Medium|High)$")

class StatusChange(BaseModel):
    status: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tickets")
def list_tickets():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()]

@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    with connect() as db:
        cursor=db.execute("INSERT INTO tickets(title,description,priority,status,created_at) VALUES (?,?,?,?,?)",
            (ticket.title,ticket.description,ticket.priority,"Open",datetime.now(timezone.utc).isoformat()))
        return dict(db.execute("SELECT * FROM tickets WHERE id=?", (cursor.lastrowid,)).fetchone())

@app.patch("/tickets/{ticket_id}/status")
def update_status(ticket_id:int, change:StatusChange):
    if change.status not in STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status")
    with connect() as db:
        cursor=db.execute("UPDATE tickets SET status=? WHERE id=?", (change.status,ticket_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return dict(db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone())
