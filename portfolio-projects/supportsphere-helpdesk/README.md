# SupportSphere — IT Helpdesk Portfolio Application

**Current status: coded local demo. Not deployed, not tested in a Windows environment, and not production-ready.** The backend stores tickets in a local SQLite database. The app contains **no real user logins or access controls**. Do not expose it publicly.

![Illustrative dashboard mockup](docs/dashboard-mockup.svg)

## Implemented source-code features
- React + TypeScript ticketing dashboard.
- Ticket creation, searchable queue and detailed view.
- Priority, status transitions and technician assignment.
- Comments and persistent ticket change history.
- Synthetic IT asset register and troubleshooting knowledge base.
- Fictional directory account lookup explicitly identified as **mock data**, not Windows Active Directory.
- Basic automated API test cases.

## Local installation (Windows 11)
Required tools: Python 3.11+, Node.js LTS, Git. No installation has been performed on your PC.

```powershell
git clone https://github.com/lavishlyyx/Hello-I-m-Zakaria-.git
cd Hello-I-m-Zakaria-/portfolio-projects/supportsphere-helpdesk/backend
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open another PowerShell window in `portfolio-projects/supportsphere-helpdesk/frontend`:

```powershell
npm install
npm run dev
```

Visit the URL printed by Vite (usually http://127.0.0.1:5173). The API documentation is at http://127.0.0.1:8000/docs.

## Automated tests (backend)
```powershell
cd portfolio-projects/supportsphere-helpdesk/backend
.\.venv\Scripts\python.exe -m unittest discover -p "test_*.py"
```

## Known limitations and next engineering steps
- Add secure authentication, role-based access control and per-ticket authorization before deployment.
- Add API security testing, proper migrations and PostgreSQL.
- Add more frontend tests and verify TypeScript production build.
- Replace mock account lookup **only** with a reviewed, authenticated, read-only service on an isolated test network.
- Record real screenshots only after running and testing.

See [features](docs/FEATURES.md), [demo scenarios](docs/demo-scenarios.md), and [Northstar lab](../northstar-ad-lab/README.md).
