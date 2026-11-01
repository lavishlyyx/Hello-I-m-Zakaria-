"""SupportSphere portfolio demo API. LOCAL ONLY: no login / no real user data."""
from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB = Path(__file__).with_name("supportsphere.db")
app = FastAPI(title="SupportSphere Portfolio Demo", version="0.2.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_methods=["GET","POST","PATCH"], allow_headers=["*"])
STATUSES = ("Open","In Progress","Resolved","Closed")
PRIORITIES = ("Low","Medium","High","Critical")
DIRECTORY = {
  "jsmith": {"username":"jsmith","display_name":"Jamie Smith","department":"Finance","enabled":True,"locked":False},
  "amorgan": {"username":"amorgan","display_name":"Alex Morgan","department":"HR","enabled":False,"locked":False},
  "tlee": {"username":"tlee","display_name":"Taylor Lee","department":"IT","enabled":True,"locked":True}
}

@contextmanager
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        con.execute("PRAGMA foreign_keys=ON")
        yield con
        con.commit()
    finally:
        con.close()

def now():
    return datetime.now(timezone.utc).isoformat()

def record(con, ticket_id, message):
    con.execute("INSERT INTO history(ticket_id,message,created_at) VALUES (?,?,?)", (ticket_id,message,now()))

def setup():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, requester TEXT NOT NULL, priority TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Open', assignee TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL, updated_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS comments(id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL REFERENCES tickets(id), author TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS history(id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL REFERENCES tickets(id), message TEXT NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS assets(id INTEGER PRIMARY KEY, asset_tag TEXT UNIQUE, device TEXT NOT NULL, assigned_to TEXT NOT NULL, status TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS articles(id INTEGER PRIMARY KEY, title TEXT NOT NULL, body TEXT NOT NULL, category TEXT NOT NULL);
        """)
        if not db.execute("SELECT 1 FROM tickets LIMIT 1").fetchone():
            moment = now()
            db.execute("INSERT INTO tickets(title,description,requester,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",("Cannot sign in","Fictional employee cannot access a test account.","Jamie Smith","High","Open","",moment,moment))
        if not db.execute("SELECT 1 FROM assets LIMIT 1").fetchone():
            db.executemany("INSERT INTO assets(asset_tag,device,assigned_to,status) VALUES (?,?,?,?)", [("NS-LAP-001","Windows 11 Laptop","Jamie Smith","Active"),("NS-LAP-002","Windows 11 Laptop","Alex Morgan","In repair"),("NS-SRV-001","Windows Server (fictional)","IT Department","Active")])
        if not db.execute("SELECT 1 FROM articles LIMIT 1").fetchone():
            db.executemany("INSERT INTO articles(title,body,category) VALUES (?,?,?)", [
               ("Account sign-in troubleshooting","Check network and domain connectivity; verify account state and log a ticket before changing access.","Accounts"),
               ("DNS troubleshooting","Run ipconfig /all and nslookup. Confirm the client's DNS points to the test domain controller.","Network"),
               ("Workstation slow","Review Task Manager, free disk space, installed updates and resource usage. Record findings.","Devices")])
setup()

class TicketIn(BaseModel):
    title: str = Field(min_length=3,max_length=120)
    description: str = Field(min_length=5,max_length=2000)
    requester: str = Field(min_length=2,max_length=80)
    priority: str = Field(default="Medium")

class UpdateIn(BaseModel):
    status: str | None = None
    assignee: str | None = Field(default=None,max_length=80)
    priority: str | None = None

class CommentIn(BaseModel):
    author: str = Field(min_length=2,max_length=80)
    body: str = Field(min_length=2,max_length=2000)

def ticket_or_404(db, ticket_id):
    row = db.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    if row is None: raise HTTPException(404,"Ticket not found")
    return dict(row)

@app.get("/health")
def health():
    return {"status":"ok","mode":"local-demo"}

@app.get("/tickets")
def tickets():
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM tickets ORDER BY id DESC")]

@app.get("/tickets/{ticket_id}")
def ticket(ticket_id:int):
    with connect() as db:
        result = ticket_or_404(db,ticket_id)
        result["comments"] = [dict(r) for r in db.execute("SELECT * FROM comments WHERE ticket_id=? ORDER BY id",(ticket_id,))]
        result["history"] = [dict(r) for r in db.execute("SELECT * FROM history WHERE ticket_id=? ORDER BY id",(ticket_id,))]
        return result

@app.post("/tickets",status_code=201)
def create_ticket(item:TicketIn):
    if item.priority not in PRIORITIES: raise HTTPException(422,"Invalid priority")
    with connect() as db:
        stamp=now()
        cur=db.execute("INSERT INTO tickets(title,description,requester,priority,status,assignee,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)",(item.title,item.description,item.requester,item.priority,"Open","",stamp,stamp))
        record(db,cur.lastrowid,"Ticket created by "+item.requester)
        return ticket_or_404(db,cur.lastrowid)

@app.patch("/tickets/{ticket_id}")
def update_ticket(ticket_id:int, item:UpdateIn):
    if item.status is not None and item.status not in STATUSES: raise HTTPException(422,"Invalid status")
    if item.priority is not None and item.priority not in PRIORITIES: raise HTTPException(422,"Invalid priority")
    with connect() as db:
        old=ticket_or_404(db,ticket_id)
        changes = {k:v for k,v in item.model_dump().items() if v is not None and v!=old[k]}
        if changes:
            parts=", ".join(k+"=?" for k in changes)
            db.execute("UPDATE tickets SET "+parts+", updated_at=? WHERE id=?",(*changes.values(),now(),ticket_id))
            record(db,ticket_id,"; ".join(k+": "+str(old[k])+" -> "+str(v) for k,v in changes.items()))
        return ticket_or_404(db,ticket_id)

@app.post("/tickets/{ticket_id}/comments",status_code=201)
def add_comment(ticket_id:int,item:CommentIn):
    with connect() as db:
        ticket_or_404(db,ticket_id)
        cur=db.execute("INSERT INTO comments(ticket_id,author,body,created_at) VALUES (?,?,?,?)",(ticket_id,item.author,item.body,now()))
        record(db,ticket_id,"Comment added by "+item.author)
        return dict(db.execute("SELECT * FROM comments WHERE id=?",(cur.lastrowid,)).fetchone())

@app.get("/assets")
def assets():
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM assets ORDER BY asset_tag")]

@app.get("/knowledge")
def knowledge():
    with connect() as db: return [dict(r) for r in db.execute("SELECT * FROM articles ORDER BY id")]

@app.get("/dashboard")
def dashboard():
    with connect() as db:
        counts = {s:db.execute("SELECT COUNT(*) FROM tickets WHERE status=?",(s,)).fetchone()[0] for s in STATUSES}
        return {"total":sum(counts.values()),"status":counts}

@app.get("/lab/directory/{username}")
def directory_lookup(username:str):
    """SYNTHETIC DIRECTORY ONLY. Not connected to Active Directory."""
    entry = DIRECTORY.get(username.lower())
    if not entry: raise HTTPException(404,"Synthetic user not found")
    return {"source":"mock-fixture","connected_to_ad":False,**entry}
