# Mermaid Snippets

## Contents
- C4 Context (Level 1)
- C4 Container (Level 2)
- C4 Component (Level 3)
- Sequence diagram
- ERD (data model)
- BPMN-style flow
- Embedding notes

Copy these snippets, replace the placeholders, and verify they render at https://mermaid.live or in the target environment.

## C4 Context (Level 1)

Shows the system in relation to its users and external systems. Always include in the FTD.

```mermaid
C4Context
    title [System name] — Context

    Person(user, "[User role]", "[What they do]")
    System(sys, "[System name]", "[One-line description]")
    System_Ext(ext1, "[External system]", "[What it provides]")

    Rel(user, sys, "[Action]")
    Rel(sys, ext1, "[Integration]", "[Protocol]")
```

## C4 Container (Level 2)

Shows the containers (apps, services, datastores) and their relationships. Mandatory for project and enterprise.

```mermaid
C4Container
    title [System name] — Containers

    Container(webApp, "Web app", "Tech: [framework]", "[Description]")
    Container(api, "API service", "Tech: [language/framework]", "[Description]")
    ContainerDb(db, "Database", "Tech: [Postgres/...]", "[Description]")
    Container_Ext(ext, "External API", "Tech: [REST/...]", "[Description]")

    Rel(webApp, api, "Calls", "HTTPS/REST")
    Rel(api, db, "Reads/writes", "SQL")
    Rel(api, ext, "Fetches", "HTTPS")
```

## C4 Component (Level 3)

Shows components within a single container. Mandatory for enterprise; optional for project.

```mermaid
C4Component
    title [Container name] — Components

    Container_Boundary(api, "API service")

    Component(controller, "[Name]Controller", "[framework]", "[Description]")
    Component(service, "[Name]Service", "[language]", "[Description]")
    Component(repo, "[Name]Repository", "[ORM]", "[Description]")

    Rel(controller, service, "Calls")
    Rel(service, repo, "Uses")
```

## Sequence diagram

Shows the message flow between actors and components for a specific use case. Mandatory for project and enterprise (key flows).

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Web as Web app
    participant API as API service
    participant DB as Database

    User->>Web: [Action]
    Web->>API: POST /endpoint
    activate API
    API->>DB: [Query]
    DB-->>API: [Result]
    API-->>Web: 200 OK [payload]
    deactivate API
    Web-->>User: [Response]

    alt Error case
        API-->>Web: 4xx [error]
        Web-->>User: [Error message]
    end
```

## ERD (data model)

Shows entities, attributes, and relationships. Mandatory for project and enterprise.

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    CUSTOMER {
        int id PK
        string email
        string name
        timestamp created_at
    }
    ORDER {
        int id PK
        int customer_id FK
        string status
        decimal total
        timestamp placed_at
    }
    LINE_ITEM {
        int id PK
        int order_id FK
        string product
        int quantity
        decimal price
    }
```

## BPMN-style flow

For business process flows. Mermaid does not have native BPMN, but a flowchart approximates it.

```mermaid
flowchart TD
    Start([Start: user submits form]) --> Validate{Validation OK?}
    Validate -- No --> Error[Show error]
    Error --> Start
    Validate -- Yes --> Save[Persist to DB]
    Save --> Notify[Send notification]
    Notify --> End([End])
```

## Embedding notes

- **Markdown mode:** Mermaid code blocks render natively in GitHub, GitLab, and most modern markdown renderers. In Confluence, use the Mermaid Editor plugin or paste the rendered SVG.
- **HTML mode:** Mermaid is loaded via CDN with a fallback. See [html-scaffold.md](html-scaffold.md) for the embedding pattern.
- **Diagram per flow:** do not cram every flow into one diagram. One sequence diagram per key use case; one ERD; one C4 per level.
- **Labels in the user's chosen language:** diagram labels follow the FTD language choice. Technical identifiers (entity names, endpoint paths) stay in English.
