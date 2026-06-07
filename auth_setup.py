"""Run once from the command line to generate token.json for YouTube OAuth."""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]

def main():
    secrets_file = os.environ.get("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
    token_file = os.environ.get("YOUTUBE_TOKEN_FILE", "token.json")

    if not os.path.exists(secrets_file):
        raise FileNotFoundError(
            f"{secrets_file} not found. Download it from Google Cloud Console "
            "(APIs & Services -> Credentials -> OAuth 2.0 Client IDs -> Desktop app -> Download JSON)."
        )

    flow = InstalledAppFlow.from_client_secrets_file(secrets_file, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(token_file, "wb") as f:
        pickle.dump(creds, f)
    print(f"Token saved to {token_file}")

if __name__ == "__main__":
    main()
