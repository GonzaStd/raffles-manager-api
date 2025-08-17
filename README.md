## Getting Started
Run the command `git clone https://github.com/GonzaStd/raffles-manager-api/` and then run `pip install -r requirements.txt` 

(You may need to first create a virtual environment with `python -m venv .venv` and run pip from `.venv/bin/pip`)

Install mariadb-server: `sudo apt-get install mariadb-server` for Debian.

Get your JWT secret with this command: `python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"`
and paste it in your .env file. WARNING: Don't share this secret with anyone, don't upload it to your repository.

## Run localhost api server
Use `python -m uvicorn main:app` to start it.

## Documentation
You have more information [here](docs/english)

You can see the FastAPI automatic documentation of the API on: `http://127.0.0.1:8000/docs`

---

# Devlog 4: Big System Review and Architecture Improvements

I have focused on user isolation, database reliability, optimal and efficient code.  
Changes introduced: primary keys, functions, good database initialization, and timezone-aware authentication systems.

---

## 🏗️ Architectural Changes

### 1. Database Schema Revolution: Composite Primary Keys

**Problem Solved**  
Original system used global auto-increment IDs, had security issues, lack of user isolation.

**Solution Implemented**  
Composite primary key architecture.

**Benefits Achieved**
- Good User Isolation: Each user sees their entities numbered from 1  
- Security Enhancement: Prevents user enumeration and information leakage  
- Predictable URLs: `/buyer/1` always refers to the user's first buyer  
- Scalable Architecture: Each user operates in their own numbering space  

---

### 2. Universal Helper Functions System

**Problem Solved**  
Repetitive database operations across different models with inconsistent patterns and error handling.

**Solution Implemented**  
Universal functions in `routes/__init__.py`.

**Benefits**
- Code Reusability: Single functions handle all models consistently  
- Error Handling: Centralized exception management and HTTP responses  
- Maintainability: Changes to database logic only need to be made in one place  
- Type Safety: Proper parameter validation and return types  

---

### 3. Advanced Raffle Filtering

**Problem Solved**  
Limited ability to filter and search raffles for drawings and sales management.

**Solution Implemented**  
Enhanced raffle filtering system.

**Benefits Achieved**
- Sales Management: Quick identification of available/sold raffles  
- Performance: Efficient querying with proper indexing  
- Flexibility: Multiple filter combinations for different use cases  

---

### 4. Robust Database Initialization System

**Problem Solved**  
Application failures when database doesn't exist, inconsistent table creation across environments.

**Solution Implemented**  
Intelligent database initialization.

**Features Implemented**
- Environment Detection: Different behavior for local vs. production  
- Graceful Failure Handling: Continues operation even with initialization warnings  
- Multiple Creation Strategies: SQLAlchemy metadata + SQL fallback  
- Verification System: Always confirms all required tables exist  

---

### 5. JWT Authentication Timezone Fix

**Problem Solved**  
JWT tokens were immediately expiring due to timezone mismatches between token creation (local time) and validation (UTC time).

**Solution Implemented**  
Timezone-aware token creation.

**Benefits Achieved**
- Reliable Authentication: Tokens work correctly  
- User Experience: No unexpected authentication failures  

---

## 🧰 Technical Improvements

### Code Quality and Maintainability
1. Consolidated Error Handling: Centralized exception management across all routes  
2. Consistent API Patterns: All endpoints follow the same structure and response format  

### Performance Optimizations
1. Efficient Querying: Optimized database queries with proper filtering and indexing  
2. Batch Operations: Bulk raffle creation for raffle sets  
3. Connection Pooling: Proper database connection management  

### Development Experience
1. Zero Configuration Setup: Database and tables created automatically  
2. Clear Error Messages: Detailed feedback for troubleshooting  
3. Environment Flexibility: Works seamlessly in local and production environments  
4. Comprehensive Testing: All major functions include error handling and validation  
