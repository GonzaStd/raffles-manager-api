# Composite Primary Keys Implementation

## Overview

This document describes the implementation of composite primary keys across all entities in the raffles manager system. The implementation ensures that each entity has their own isolated numbering sequence starting from 1.

## Architecture

### Entity-Manager System
- `entities(id)` → Main organizational units
- `managers(entity_id, manager_number)` → Per-entity numbering 1,2,3...
- `buyers(entity_id, buyer_number)` → Per-entity numbering 1,2,3...
- `projects(entity_id, project_number)` → Per-entity numbering 1,2,3...
- `raffle_sets(entity_id, project_number, set_number)` → Per-project numbering 1,2,3...
- `raffles(entity_id, project_number, raffle_number)` → Per-project numbering 1,2,3...

## Benefits

### Entity Experience
- **Predictable URLs**: `/buyer/1` always refers to the entity's first buyer
- **Intuitive numbering**: Each entity sees their resources numbered from 1
- **Privacy**: Entities cannot infer system usage from ID gaps

### Security
- **Information hiding**: Total system usage is not exposed through IDs
- **Entity isolation**: Perfect conceptual separation between entities
- **No ID enumeration**: Cannot guess valid IDs from other entities

### Technical
- **Scalable**: Each entity has independent numbering space
- **Maintainable**: Clear relationship hierarchy
- **Database efficient**: Proper indexing on composite keys

## Implementation Details

### Models
All models use composite primary keys with proper foreign key relationships:

```python
# Entity Model
class Entity(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

# Manager Model  
class Manager(Base):
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    manager_number = Column(Integer, primary_key=True)

# Buyer Model
class Buyer(Base):
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    buyer_number = Column(Integer, primary_key=True)
    
# Project Model  
class Project(Base):
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)

# RaffleSet Model
class RaffleSet(Base):
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    set_number = Column(Integer, primary_key=True)

# Raffle Model
class Raffle(Base):
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    raffle_number = Column(Integer, primary_key=True)
```

### Auto-increment Functions
Specialized functions handle per-entity/per-project numbering:

```python
def get_next_buyer_number(db: Session, entity_id: int) -> int
def get_next_project_number(db: Session, entity_id: int) -> int
def get_next_manager_number(db: Session, entity_id: int) -> int
def get_next_set_number(db: Session, entity_id: int, project_number: int) -> int
def get_next_raffle_number(db: Session, entity_id: int, project_number: int) -> int
```

### URL Structure
The API uses hierarchical URLs that reflect the data structure:

```
# Authentication
POST /auth/entity/register
POST /auth/entity/login
POST /auth/manager/register
POST /auth/manager/login

# Buyers (per entity)
GET /buyer/{buyer_number}
POST /buyer
PUT /buyer
DELETE /buyer/{buyer_number}

# Projects (per entity)  
GET /project/{project_number}
POST /project
PUT /project
DELETE /project/{project_number}

# Managers (per entity)
GET /manager/{manager_number}
GET /managers
PUT /manager
DELETE /manager/{manager_number}

# Raffle Sets (per project)
POST /project/{project_number}/raffleset
GET /project/{project_number}/raffleset/{set_number}
GET /project/{project_number}/rafflesets

# Raffles (per project)
GET /project/{project_number}/raffle/{raffle_number}
POST /project/{project_number}/raffles  # Filtered search
POST /project/{project_number}/raffle/{raffle_number}/sell
```

## Database Schema

The database structure maintains referential integrity with proper foreign key constraints:

```sql
-- Composite foreign keys ensure data consistency
FOREIGN KEY (entity_id, project_number) REFERENCES projects(entity_id, project_number)
FOREIGN KEY (entity_id, project_number, set_number) REFERENCES raffle_sets(entity_id, project_number, set_number)
FOREIGN KEY (buyer_entity_id, buyer_number) REFERENCES buyers(entity_id, buyer_number)
FOREIGN KEY (sold_by_entity_id, sold_by_manager_number) REFERENCES managers(entity_id, manager_number)
```

## Manager Sale Tracking

### Automatic Attribution
- When managers sell raffles, their identity is automatically recorded
- Entities can manually assign sales to specific managers
- Full audit trail of who sold what

### Reporting Capabilities
- Sales performance by manager
- Commission calculations
- Activity tracking per manager

---

*This implementation provides entity-isolated multi-tenancy with manager accountability while maintaining data integrity and performance.*
