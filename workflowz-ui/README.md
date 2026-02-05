# Workflowz UI (Streamlit)

This is a Streamlit UI for the Workflowz.ai FastAPI backend.

## Requirements
Install dependencies:

```bash
pip install -r workflowz-ui/requirements.txt
```

## Configuration
Set the backend URL using an environment variable:

```bash
export API_BASE_URL="http://localhost:8000"
```

You can also place `API_BASE_URL` in a `.env` file at the repo root or inside `workflowz-ui/`.

## Run
```bash
streamlit run workflowz-ui/app.py
```

## Notes
- You must be logged in to access pages. The login uses `/api/auth/token`.
- Superusers should provide an organization name in the sidebar to access org-scoped data.
