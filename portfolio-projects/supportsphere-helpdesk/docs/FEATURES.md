# SupportSphere feature matrix

| Feature | Status |
|---|---|
| Ticket creation, listing and details | Implemented in demo API |
| Priority, status and technician assignment | Implemented in demo API |
| Comments and ticket change history | Implemented in demo API |
| Asset inventory and knowledge articles | Implemented as demo read-only endpoints |
| Fictional Active Directory account lookup | Implemented as mock fixtures, not real AD |
| Secure login, RBAC, audit security | Not implemented |
| Windows Server AD domain | Not built or verified |
| Production deployment | Not implemented |

**Security:** This application intentionally has no authentication. Only run on a local development environment with synthetic data. Do not deploy publicly. The lab lookup returns hardcoded fictional records and cannot administer real accounts.
