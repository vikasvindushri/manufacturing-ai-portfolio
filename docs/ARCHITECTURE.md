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


## Phase 2 configuration architecture - Contract 1.1

```mermaid
flowchart LR
  B[Future point-and-click builders] --> D[Workflow Definition 1.1]
  D --> V[Strict model and compatibility validation]
  V --> R[Rules and routing]
  V --> P[Prompt and output references]
  V --> G[Classification, AI and approval policy]
  V --> T[Synthetic preview cases]
  R --> X[Future configuration-driven runtime]
  P --> X
  G --> X
  T --> X
```

Increment 2.1 establishes the configuration contract and validation boundary. It does not yet replace the Phase 1 runtime or add the Workflow Studio user interface.
