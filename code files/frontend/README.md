# EduGenie Frontend

This is the separate frontend for the EduGenie project. It intentionally uses plain HTML, CSS, and JavaScript so there is no Node/npm dependency for the standard setup.

## Run

From the repository root:

```powershell
.\run_frontend_windows.ps1
```

Then open:

```text
http://127.0.0.1:5500
```

The frontend calls the FastAPI backend at `http://127.0.0.1:8000` by default. To change it, edit `config.js`.
