import subprocess
import sys

def setup_mysql():
    try:
        subprocess.run(['mysql', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Please, install mysql and try again.")
        sys.exit(1)

    try:
        subprocess.run(['systemctl', 'is-active', 'mysql'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        try:
            subprocess.run(['systemctl', 'is-active', 'mariadb'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            print("MySQL/MariaDB server isn't running or doesn't exist. If it doesn't, install it and try again.")
            sys.exit(1)

    check_user_cmd = "SELECT COUNT(*) FROM mysql.user WHERE user='raffles-manager' AND host='localhost';"
    result = subprocess.run([
        'sudo', 'mysql', '-u', 'root', '-e', check_user_cmd
    ], check=True, capture_output=True, text=True)

    user_exists = '1' in result.stdout

    if not user_exists:
        create_user_commands = [
            "CREATE USER 'raffles-manager'@'localhost' IDENTIFIED BY 'raffles';",
            "GRANT ALL PRIVILEGES ON *.* TO 'raffles-manager'@'localhost';",
            "FLUSH PRIVILEGES;"
        ]

        for cmd in create_user_commands:
            try:
                subprocess.run([
                    'sudo', 'mysql', '-u', 'root', '-e', cmd
                ], check=True, capture_output=True)
            except Exception as e:
                print(f"There was a problem creating \"raffles_manager\" user on mysql:\n{e}\n\nCommands used:\n"
                      + c for c in create_user_commands)
    return True