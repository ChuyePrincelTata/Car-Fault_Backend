import urllib.parse

# Your original password
password = "Pelko%12345.."

# URL encode the password
encoded_password = urllib.parse.quote(password, safe='')

print(f"Original password: {password}")
print(f"URL-encoded password: {encoded_password}")

# Create the full connection string
username = "postgres.qxwqdhvoujwmilunpftd"
host = "aws-0-us-east-2.pooler.supabase.com"
port = "6543"
database = "postgres"

connection_string = f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
print(f"\nFull connection string:")
print(connection_string)
