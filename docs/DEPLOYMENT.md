# Deploying LifeFlow (Day 5 concept: Deployability)

You are **not required** to deploy for the capstone — judges only need to see
this documented (per the competition's Technical Implementation criteria).
If you want to actually deploy, here's the path using `adk deploy`, which
packages the agent for Cloud Run.

## 1. Prerequisites
- A Google Cloud project with billing enabled (use the $300 free trial if
  you haven't used it, per the course FAQ).
- `gcloud` CLI installed and authenticated: `gcloud auth login`
- Your `GOOGLE_API_KEY` set as a Cloud Run environment variable / secret —
  never baked into the container image.

## 2. Deploy with the ADK CLI
```bash
adk deploy cloud_run \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --service_name=lifeflow-concierge \
  --with_ui \
  agent
```
This builds a container from the `agent/` package, pushes it, and deploys
it to Cloud Run with the ADK dev UI attached.

## 3. Environment variables on Cloud Run
Set these in the Cloud Run service config (not in code):
- `GOOGLE_API_KEY`
- `GOOGLE_GENAI_USE_VERTEXAI=FALSE` (or configure Vertex AI credentials
  instead, if you prefer service-account auth over an API key)

## 4. Clean up (avoid surprise charges)
```bash
gcloud run services delete lifeflow-concierge --region=us-central1
gcloud projects delete YOUR_PROJECT_ID   # if this was a throwaway project
```
Also delete any API keys created specifically for this deployment.

## Note on the MCP server in production
`mcp_server/server.py` currently runs as a local subprocess over stdio,
launched by `agent/mcp_connection.py`. For a Cloud Run deployment this
still works because the MCP server ships inside the same container and
subprocess launch works the same way in the cloud sandbox. For a
multi-instance production setup, the MCP server could instead be deployed
as its own Cloud Run service using the `StreamableHTTPConnectionParams`
transport instead of stdio — noted here as the next architectural step,
not implemented in this submission to keep the demo simple and reviewable.
