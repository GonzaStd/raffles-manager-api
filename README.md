# Raffles Manager API
![Front Page](https://raw.githubusercontent.com/GonzaStd/raffles-manager-api/master/.github/multimedia/FrontPage.png)

A REST API for managing raffle projects, raffle sets, individual raffle numbers, buyers, and user accounts.

The project is designed around the organization of raffles into projects and sets, while keeping each user's data isolated.

## Example case

### Scout group
![Example case](https://raw.githubusercontent.com/GonzaStd/raffles-manager-api/master/.github/multimedia/Example.png)

## Features

### Project Management

- Create and manage raffle projects per user.
- Organize raffle sets within each project.
- Example: a project such as `Father's Day Raffle` can contain multiple raffle sets.

### Raffle System

- Create raffle sets for physical or virtual raffles.
- Generate individual raffle numbers automatically.
- Configure the number of tickets and unit price.
- Manage raffle number ranges.
- Track raffle number status:
  - `available`
  - `reserved`
  - `paid`
- Easily retrieve sold numbers for raffle draws.

> A raffle set being physical or virtual refers to how the raffle is sold, not to the payment method.

### Buyer Management

- Register buyers and their personal information.
- Validate email addresses and phone numbers.
- Keep track of buyer purchase history.
- Associate purchases with individual raffle numbers.

### Authentication

- User registration and login.
- JWT-based authentication.
- Bearer token authentication for protected endpoints.
- Password hashing with bcrypt.

### User Data Isolation

Each user's projects, raffle sets, raffles, and buyers are isolated from other users.

The database uses user-aware identifiers and relationships to keep entities scoped to their owner.

## Typical Usage Flow

A typical workflow looks like this:

1. An administrator registers or logs in.
2. The administrator creates a project, for example `Scout Camp Raffle`.
3. Raffle sets are created inside the project.
4. The system automatically generates the requested number of raffle numbers.
5. Buyers are registered.
6. Raffle numbers are assigned to buyers.
7. Numbers are marked as paid when the purchase is completed.
8. The system can retrieve the sold numbers when the raffle is ready to be drawn.

A raffle set does not necessarily represent a specific prize. It is primarily a way to organize groups of raffle numbers within a project.

## Data Model

The main entities are:

```text
User
 ├── Projects
 │    └── RaffleSets
 │         └── Raffles
 │
 └── Buyers
      └── Purchases
````

The main database tables are:

* `users`
* `projects`
* `rafflesets`
* `raffles`
* `buyers`

Relationships between these entities are handled through SQLAlchemy.

## Technologies

* **Python**
* **FastAPI** — REST API framework
* **SQLAlchemy** — ORM and database modeling
* **MySQL / MariaDB** — relational database
* **Pydantic** — data validation
* **JWT** — authentication
* **bcrypt** — password hashing
* **Uvicorn** — ASGI server

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/GonzaStd/raffles-manager-api/
cd raffles-manager-api

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

On Debian-based systems, install MariaDB with:

```bash
sudo apt install mariadb-server
```

Create a JWT secret:

```bash
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
```

Add the generated value to your `.env` file.

**Do not commit your JWT secret or other credentials to the repository.**

## Running the API

Start the development server with:

```bash
python -m uvicorn main:app
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

## Project Status

This is a personal backend project focused on building a practical REST API and exploring:

* API design with FastAPI
* Relational database modeling
* Authentication and authorization
* Data validation
* User-scoped data
* Raffle and purchase management
