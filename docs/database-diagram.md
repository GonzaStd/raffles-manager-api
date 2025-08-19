# Database Schema Diagram

## Entity Relationship Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        varchar username UK
        varchar hashed_password
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    BUYERS {
        int user_id PK,FK
        int buyer_number PK
        varchar name
        varchar phone
        varchar email
        datetime created_at
        datetime updated_at
    }
    
    PROJECTS {
        int user_id PK,FK
        int project_number PK
        varchar name
        text description
        datetime created_at
        datetime updated_at
    }
    
    RAFFLE_SETS {
        int user_id PK,FK
        int project_number PK,FK
        int set_number PK
        varchar name
        varchar type
        int init
        int final
        int unit_price
        datetime created_at
        datetime updated_at
    }
    
    RAFFLES {
        int user_id PK,FK
        int project_number PK,FK
        int raffle_number PK
        int set_number FK
        int buyer_user_id FK
        int buyer_number FK
        varchar payment_method
        varchar state
        datetime created_at
        datetime updated_at
    }

    %% Relationships
    USERS ||--o{ BUYERS : "owns"
    USERS ||--o{ PROJECTS : "owns"
    USERS ||--o{ RAFFLE_SETS : "owns"
    USERS ||--o{ RAFFLES : "owns"
    
    PROJECTS ||--o{ RAFFLE_SETS : "contains"
    RAFFLE_SETS ||--o{ RAFFLES : "contains"
    
    BUYERS ||--o{ RAFFLES : "purchases"
```

## Composite Primary Key Structure

```mermaid
graph TD
    A[USERS] --> B[user_id = 1]
    B --> C[BUYERS<br/>user_id=1, buyer_number=1,2,3...]
    B --> D[PROJECTS<br/>user_id=1, project_number=1,2,3...]
    D --> E[RAFFLE_SETS<br/>user_id=1, project_number=1, set_number=1,2,3...]
    E --> F[RAFFLES<br/>user_id=1, project_number=1, raffle_number=1,2,3...]
    
    G[USERS] --> H[user_id = 2]
    H --> I[BUYERS<br/>user_id=2, buyer_number=1,2,3...]
    H --> J[PROJECTS<br/>user_id=2, project_number=1,2,3...]
    J --> K[RAFFLE_SETS<br/>user_id=2, project_number=1, set_number=1,2,3...]
    K --> L[RAFFLES<br/>user_id=2, project_number=1, raffle_number=1,2,3...]
    
    style A fill:#e1f5fe
    style G fill:#e1f5fe
    style C fill:#f3e5f5
    style I fill:#f3e5f5
    style D fill:#e8f5e8
    style J fill:#e8f5e8
    style E fill:#fff3e0
    style K fill:#fff3e0
    style F fill:#fce4ec
    style L fill:#fce4ec
```

## User Isolation Visualization

```mermaid
graph LR
    subgraph "User 1 Namespace"
        U1[User 1]
        B1[Buyer 1,2,3...]
        P1[Project 1,2,3...]
        RS1[RaffleSet 1,2,3...]
        R1[Raffle 1,2,3...]
    end
    
    subgraph "User 2 Namespace"
        U2[User 2]
        B2[Buyer 1,2,3...]
        P2[Project 1,2,3...]
        RS2[RaffleSet 1,2,3...]
        R2[Raffle 1,2,3...]
    end
    
    subgraph "User N Namespace"
        UN[User N]
        BN[Buyer 1,2,3...]
        PN[Project 1,2,3...]
        RSN[RaffleSet 1,2,3...]
        RN[Raffle 1,2,3...]
    end
    
    U1 --> B1
    U1 --> P1
    P1 --> RS1
    RS1 --> R1
    
    U2 --> B2
    U2 --> P2
    P2 --> RS2
    RS2 --> R2
    
    UN --> BN
    UN --> PN
    PN --> RSN
    RSN --> RN
    
    style U1 fill:#e3f2fd
    style U2 fill:#e8f5e8
    style UN fill:#fff3e0
```

## Foreign Key Constraints

```mermaid
graph TD
    A[USERS.id] --> B[BUYERS.user_id]
    A --> C[PROJECTS.user_id]
    A --> D[RAFFLE_SETS.user_id]
    A --> E[RAFFLES.user_id]
    
    F[PROJECTS: user_id, project_number] --> G[RAFFLE_SETS: user_id, project_number]
    H[RAFFLE_SETS: user_id, project_number, set_number] --> I[RAFFLES: user_id, project_number, set_number]
    J[BUYERS: user_id, buyer_number] --> K[RAFFLES: buyer_user_id, buyer_number]
    
    style A fill:#ffeb3b
    style F fill:#4caf50
    style H fill:#ff9800
    style J fill:#9c27b0
```

## Auto-increment Scoping

```mermaid
flowchart TD
    A[New Buyer Creation] --> B{Get max buyer_number for user_id}
    B --> C[Add 1 to max number]
    C --> D[Create buyer with new number]
    
    E[New Project Creation] --> F{Get max project_number for user_id}
    F --> G[Add 1 to max number]
    G --> H[Create project with new number]
    
    I[New RaffleSet Creation] --> J{Get max set_number for user_id + project_number}
    J --> K[Add 1 to max number]
    K --> L[Create raffle set with new number]
    
    M[New Raffle Creation] --> N{Get max raffle_number for user_id + project_number}
    N --> O[Add 1 to max number]
    O --> P[Create raffle with new number]
```

## Benefits Summary

### 🔒 Security Benefits
- **No ID enumeration**: Users can't guess other users' entity IDs
- **Complete isolation**: Zero possibility of cross-user data access
- **Information hiding**: System usage patterns are hidden

### 👤 User Experience Benefits  
- **Intuitive numbering**: Each user's entities start from 1
- **Predictable URLs**: `/buyer/1` always means "my first buyer"
- **Logical hierarchy**: Clear parent-child relationships in URLs

### 🏗️ Technical Benefits
- **Scalability**: Ready for horizontal partitioning by user_id
- **Maintainability**: Universal functions work across all models
- **Performance**: Efficient queries with proper composite indexing
- **Flexibility**: Easy to add new entity types following same pattern

### 📊 Data Integrity Benefits
- **Referential integrity**: Composite foreign keys prevent orphaned records
- **Consistent numbering**: No gaps in user-scoped sequences
- **Audit trails**: Clear ownership and modification tracking
- **Backup/restore**: User-scoped data can be backed up independently

