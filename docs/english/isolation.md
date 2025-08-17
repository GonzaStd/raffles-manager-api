# User Isolation System - Documentation

## Introduction

This system implements **complete data isolation per user**, ensuring that each user can only access, modify, and delete their own data. No user can view or interact with information from other users.

## System Architecture

### Hierarchical Data Structure

```
USER (users)
    ↓
PROJECTS (projects) 
    ↓
RAFFLE SETS (raffle_sets)
    ↓
INDIVIDUAL RAFFLES (raffles)

BUYERS (buyers) ← Independent but linked to user
```

### Important Differences in Email Handling

- **USERS (System users)**: NO email - authentication only with `username` and `password`
- **BUYERS (Customers)**: YES email - contact information for the actual buyer

## How Isolation Works

### 1. Base Level - User
- Each user registers with `username` and `password` only
- Receives a unique ID that becomes the foundation of the entire hierarchy
- No email stored to simplify authentication

### 2. Level 1 - Projects
- Each project MUST have an assigned `user_id`
- A user can only view/modify projects where `user_id = their_id`
- Impossible to access other users' projects

### 3. Level 2 - Raffle Sets
- Belong to a specific project
- **Automatic TRIGGER** assigns the `user_id` from the parent project
- Guarantees the set belongs to the same user as the project

### 4. Level 3 - Individual Raffles
- Belong to a specific set
- **Automatic TRIGGER** assigns the `user_id` from the parent set
- Maintains the ownership chain intact

### 5. Independent Level - Buyers
- Each buyer MUST have a `user_id` assigned directly
- Includes `email` for contact information
- A user can only view/use buyers where `user_id = their_id`

## Practical Example

### Scenario
- **User A**: ID=1, username="store_admin"
- **User B**: ID=2, username="local_seller"

### Data Flow

#### 1. User A creates a project
```sql
INSERT INTO projects (name, description, user_id) 
VALUES ('Christmas Raffle 2024', 'Fundraising raffle for Christmas', 1);
-- Result: project_id = 101, user_id = 1
```

#### 2. User A creates a set in their project
```sql
INSERT INTO raffle_sets (name, project_id, init, final, unit_price) 
VALUES ('Main Set', 101, 1, 100, 50);
-- TRIGGER automatically assigns user_id = 1
-- Result: set_id = 501, user_id = 1 (automatic)
```

#### 3. User A creates raffles in their set
```sql
INSERT INTO raffles (number, set_id) VALUES (1, 501);
INSERT INTO raffles (number, set_id) VALUES (2, 501);
-- TRIGGER automatically assigns user_id = 1 to each raffle
```

#### 4. User B tries to access User A's data
```sql
-- This query returns NOTHING for User B:
SELECT * FROM projects WHERE user_id = 2;  -- EMPTY

-- Neither does this:
SELECT * FROM raffle_sets WHERE user_id = 2;  -- EMPTY

-- User B CANNOT see User A's data
```

## Code Implementation

### Safe Queries
```python
# ✅ CORRECT - Always filter by user_id
def get_user_projects(db: Session, current_user_id: int):
    return db.query(Project).filter(Project.user_id == current_user_id).all()

# ❌ INCORRECT - No user filter (UNSAFE)
def get_all_projects(db: Session):
    return db.query(Project).all()  # Returns data from ALL users
```

### Ownership Validation
```python
def delete_project(db: Session, project_id: int, current_user_id: int):
    # Verify the project belongs to the current user
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user_id  # KEY: validate ownership
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found or you don't have permissions")
    
    db.delete(project)
    db.commit()
```

## Security Flow

### 1. Authentication
- User registers/authenticates with `username` and `password`
- Receives JWT token containing their `user_id`
- No email required for authentication process

### 2. Authorization
- Each request validates the JWT token
- Extracts the `user_id` from the token
- All queries filter by that `user_id`

### 3. Isolation
- Impossible to access other users' data
- Automatic triggers maintain integrity
- Indexes optimize queries per user

## Implemented Protections

### Database Level
- ✅ Each table contains `user_id`
- ✅ Automatic triggers propagate ownership
- ✅ Composite indexes optimize user queries
- ✅ Referential integrity constraints
- ✅ Simplified authentication without email

### Application Level
- ✅ All queries filter by `user_id`
- ✅ Ownership validation before modify/delete
- ✅ JWT contains authenticated user's `user_id`
- ✅ Security middleware on all routes
- ✅ Registration and login only with username and password

## System Advantages

1. **Complete Isolation**: Impossible cross-access between users
2. **Automation**: Triggers handle ownership propagation
3. **Scalability**: Works efficiently for thousands of users
4. **Simplicity**: Authentication only with username, no email complexity
5. **Auditing**: Complete record of access and modifications
6. **Performance**: Optimized indexes for user queries
7. **Flexibility**: Buyers can have email for contact

## Use Cases

### User Registration
```python
# Only requires username and password
user_data = {
    "username": "my_online_store",
    "password": "my_secure_password"
}
```

### Buyer Creation
```python
# Can include email for contact
buyer_data = {
    "name": "John Doe",
    "email": "john.doe@email.com",  # For contact
    "phone": "+1234567890"
}
```

## Database Triggers

### Auto-assign user_id in raffle_sets
```sql
CREATE TRIGGER tr_raffle_sets_user_id
    BEFORE INSERT ON raffle_sets
    FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL THEN
        SELECT user_id INTO NEW.user_id
        FROM projects
        WHERE id = NEW.project_id;
    END IF;
END
```

### Auto-assign user_id in raffles
```sql
CREATE TRIGGER tr_raffles_user_id
    BEFORE INSERT ON raffles
    FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL THEN
        SELECT user_id INTO NEW.user_id
        FROM raffle_sets
        WHERE id = NEW.set_id;
    END IF;
END
```

## Security Policies

### Always Use User Filtering
```python
# ✅ Secure pattern for all queries
def get_user_data(db: Session, user_id: int):
    projects = db.query(Project).filter(Project.user_id == user_id).all()
    buyers = db.query(Buyer).filter(Buyer.user_id == user_id).all()
    return {"projects": projects, "buyers": buyers}
```

### Validate Ownership Before Operations
```python
def update_raffle_set(db: Session, set_id: int, user_id: int, update_data: dict):
    # First, verify ownership
    raffle_set = db.query(RaffleSet).filter(
        RaffleSet.id == set_id,
        RaffleSet.user_id == user_id
    ).first()
    
    if not raffle_set:
        raise HTTPException(403, "Access denied")
    
    # Then update
    for key, value in update_data.items():
        setattr(raffle_set, key, value)
    
    db.commit()
```

## Conclusion

This system guarantees that each user operates in a completely isolated environment, where they can only access their own data. The differentiation between users (no email) and buyers (with email) allows for simple authentication while maintaining the contact information necessary for business operations.

The automatic triggers and comprehensive indexing ensure both security and performance, making this system suitable for production environments with multiple concurrent users.
