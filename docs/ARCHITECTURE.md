# Architecture
```mermaid
flowchart LR
  U[Engineer / Quality user] --> UI[Streamlit or Low-Code UI]
  UI --> S[Python services]
  S --> E[Rules and extraction]
  S --> R[TF-IDF retrieval]
  S --> A[Action record]
  E --> H[Human review gate]
  R --> C[Cited evidence]
  A --> H
  H --> X[Approved export / downstream system]
```

## Production evolution
Place APIs behind authentication, store approved records in a governed database, ingest only released documents, add observability, version prompts/models/rules, and integrate with QMS/MES/CMMS through approved interfaces.
