# token_al.py — kendi bilgisayarınızda bir kez çalıştırın:
#   pip install google-auth-oauthlib && python token_al.py
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", ["https://www.googleapis.com/auth/youtube.upload"])
creds = flow.run_local_server(port=0)
print(creds.refresh_token)
