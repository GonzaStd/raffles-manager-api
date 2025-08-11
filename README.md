## Getting Started
Run the command `git clone https://github.com/GonzaStd/raffles-manager-api/` and then run `pip install -r requirements.txt` 

(You may need to first create a virtual environment with `python -m venv .venv` and run pip from `.venv/bin/pip`)

Install mariadb-server: `sudo apt-get install mariadb-server` for Debian.

Get your JWT secret with this command: `python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"`
and paste it in your .env file. WARNING: Don't share this secret with anyone, don't upload it to your repository.

## Run localhost api server
Use `python -m uvicorn main:app` to start it.

## Documentation
You can see the FastAPI automatic documentation of the API on: `http://127.0.0.1:8000/docs`
