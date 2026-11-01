import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
type Status = "Open" | "In Progress" | "Resolved" | "Closed";
type Ticket = {id:number;title:string;description:string;priority:string;status:Status;created_at:string};
const API="http://127.0.0.1:8000";
function App() {
  const [tickets,setTickets]=useState<Ticket[]>([]);
  const [title,setTitle]=useState("");
  const [description,setDescription]=useState("");
  const [priority,setPriority]=useState("Medium");
  const [error,setError]=useState("");
  const refresh=async()=>{
    try { const r=await fetch(API+"/tickets");if(!r.ok)throw Error("API returned an error");setTickets(await r.json());setError(""); }
    catch {setError("Cannot reach the local API. Start FastAPI on port 8000.");}
  };
  useEffect(()=>{void refresh();},[]);
  const create=async(e:React.FormEvent)=>{
    e.preventDefault();
    try {
      const r=await fetch(API+"/tickets",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({title,description,priority})});
      if(!r.ok) throw Error("Ticket not created. Check the form.");
      setTitle("");setDescription("");await refresh();
    } catch(e) {setError(String(e));}
  };
  const change=async(id:number,status:Status)=>{
    try{const r=await fetch(API+`/tickets/${id}/status`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status})});if(!r.ok)throw Error("Update failed");await refresh();}
    catch(e){setError(String(e));}
  };
  return <main className="container">
    <header><div><span className="eyebrow">LOCAL PORTFOLIO DEMO</span><h1>SupportSphere</h1><p>IT service desk • Ticket management</p></div><span className="pill">Version 0.1</span></header>
    <section className="metrics"><div><strong>{tickets.length}</strong><span>Total tickets</span></div><div><strong>{tickets.filter(t=>t.status==="Open").length}</strong><span>Open</span></div><div><strong>{tickets.filter(t=>t.status==="Resolved"||t.status==="Closed").length}</strong><span>Resolved / Closed</span></div></section>
    {error&&<p className="error" role="alert">{error}</p>}
    <div className="layout"><section className="panel"><h2>Create ticket</h2><form onSubmit={create}><label>Issue title<input value={title} onChange={e=>setTitle(e.target.value)} required minLength={3} maxLength={120} placeholder="e.g. Cannot sign in"/></label><label>Description<textarea value={description} onChange={e=>setDescription(e.target.value)} required minLength={5} rows={5}/></label><label>Priority<select value={priority} onChange={e=>setPriority(e.target.value)}><option>Low</option><option>Medium</option><option>High</option></select></label><button type="submit">Submit ticket</button></form></section><section className="panel"><h2>Ticket queue</h2>{tickets.length===0?<p>No tickets yet.</p>:tickets.map(t=><article key={t.id} className="ticket"><div className="ticket-head"><strong>#{t.id} · {t.title}</strong><small>{t.priority}</small></div><p>{t.description}</p><label>Status <select aria-label={`Status for ticket ${t.id}`} value={t.status} onChange={e=>void change(t.id,e.target.value as Status)}>{["Open","In Progress","Resolved","Closed"].map(v=><option key={v}>{v}</option>)}</select></label></article>)}</section></div>
    <footer>Demo only • No authentication or real company data • Do not expose publicly</footer>
  </main>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
