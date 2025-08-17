.# Composite Primary Keys Implementation

## Overview

This document describes the implementation of composite primary keys across all entities in the raffles manager system. The implementation ensures that each user has their own isolated numbering sequence starting from 1.

## Architecture Changes

### Before (Simple PKs)
- `buyers.id` → Global auto-increment
- `projects.id` → Global auto-increment  
- `raffle_sets.id` → Global auto-increment
- `raffles.number` → Global auto-increment

### After (Composite PKs)
- `buyers(user_id, buyer_number)` → Per-user numbering 1,2,3...
- `projects(user_id, project_number)` → Per-user numbering 1,2,3...
- `raffle_sets(user_id, project_number, set_number)` → Per-project numbering 1,2,3...
- `raffles(user_id, project_number, raffle_number)` → Per-project numbering 1,2,3...

## Benefits

### User Experience
- **Predictable URLs**: `/buyer/1` always refers to the user's first buyer
- **Intuitive numbering**: Each user sees their entities numbered from 1
- **Privacy**: Users cannot infer system usage from ID gaps

### Security
- **Information hiding**: Total system usage is not exposed through IDs
- **User isolation**: Perfect conceptual separation between users
- **No ID enumeration**: Attackers cannot guess valid IDs from other users

### Technical
- **Scalable**: Each user has independent numbering space
- **Maintainable**: Clear relationship hierarchy
- **Database efficient**: Proper indexing on composite keys

## Implementation Details

### Models
All models now use composite primary keys with proper foreign key relationships:

```python
# Buyer Model
class Buyer(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    buyer_number = Column(Integer, primary_key=True)  # Auto-increment per user
    
# Project Model  
class Project(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)  # Auto-increment per user

# RaffleSet Model
class RaffleSet(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    set_number = Column(Integer, primary_key=True)  # Auto-increment per project

# Raffle Model
class Raffle(Base):
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    raffle_number = Column(Integer, primary_key=True)  # Auto-increment per project
```

### Auto-increment Functions
Specialized functions handle per-user/per-project numbering:

```python
def get_next_buyer_number(db: Session, user_id: int) -> int
def get_next_project_number(db: Session, user_id: int) -> int
def get_next_set_number(db: Session, user_id: int, project_number: int) -> int
def get_next_raffle_number(db: Session, user_id: int, project_number: int) -> int
```

### URL Structure
The new API uses hierarchical URLs that reflect the data structure:

```
# Buyers (per user)
GET /buyer/{buyer_number}
POST /buyer
PUT /buyer
DELETE /buyer/{buyer_number}

# Projects (per user)  
GET /project/{project_number}
POST /project
PUT /project
DELETE /project/{project_number}

# Raffle Sets (per project)
POST /project/{project_number}/raffleset
GET /project/{project_number}/raffleset/{set_number}
GET /project/{project_number}/rafflesets

# Raffles (per project)
GET /project/{project_number}/raffle/{raffle_number}
POST /project/{project_number}/raffles  # Filtered search
POST /project/{project_number}/raffle/{raffle_number}/sell
```

## Migration Considerations

### Breaking Changes
- **URL structure changed**: All endpoints now use composite identifiers
- **Schema changes**: Database schema completely restructured
- **API contracts**: Request/response schemas updated

### Backward Compatibility
- Legacy `get_record()` function provides limited compatibility
- Simple ID lookups mapped to composite keys where possible
- Clear error messages for unsupported operations

## Database Schema

The database structure maintains referential integrity with proper foreign key constraints:

```sql
-- Composite foreign keys ensure data consistency
FOREIGN KEY (user_id, project_number) REFERENCES projects(user_id, project_number)
FOREIGN KEY (user_id, project_number, set_number) REFERENCES raffle_sets(user_id, project_number, set_number)
FOREIGN KEY (buyer_user_id, buyer_number) REFERENCES buyers(user_id, buyer_number)
```

## Testing Strategy

### Unit Tests
- Auto-increment functions return correct sequences
- Composite key lookups work correctly
- User isolation is maintained

### Integration Tests  
- End-to-end workflows with multiple users
- Concurrent user operations don't interfere
- Foreign key constraints are enforced

### Performance Tests
- Query performance with composite indexes
- Bulk operations scaling
- Memory usage under load

## Future Considerations

### Potential Optimizations
- Consider partitioning large tables by user_id
- Index optimization for common query patterns
- Caching strategies for auto-increment values

### Extension Points
- Easy to add tenant-level isolation above user level
- Prepared for horizontal scaling by user_id
- Supports multi-regional deployments

---

*This implementation provides a solid foundation for user-isolated multi-tenancy while maintaining data integrity and performance.*
