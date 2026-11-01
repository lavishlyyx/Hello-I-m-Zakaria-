# Run SupportSphere entirely in the browser

This project has a GitHub Codespaces configuration. You do not need to install tools on Windows.

1. Open the repository: https://github.com/lavishlyyx/Hello-I-m-Zakaria-
2. Select **Code → Codespaces → Create codespace on main**. GitHub must allow Codespaces for your account; billing/usage limits may apply.
3. Wait for the setup to finish. It installs backend and frontend dependencies into the cloud workspace.
4. Open the terminal in the Codespace and run:

```bash
bash portfolio-projects/supportsphere-helpdesk/scripts/start.sh
```

5. In **Ports**, select the forwarded port **5173**, then **Open in Browser**. The port should remain **Private**.
6. Create a test ticket, change its status, assign a technician and add a comment.
7. Run tests in another Codespaces terminal:

```bash
cd portfolio-projects/supportsphere-helpdesk/backend
.venv/bin/python -m unittest discover -p 'test_*.py'
cd ../frontend
npm run build
```

## Important limitations
- The app is a **local development demo** with no real authentication. Do not change port visibility to public or put real personal/company data into the demo.
- The directory view uses **hardcoded fictional accounts**. It is **not** a live Active Directory connection.
- Codespaces can be stopped or deleted and may use account quota.
- The standalone Windows Server domain lab cannot run in this browser Codespace. It still requires a Windows virtualization environment.
