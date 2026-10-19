import gspread
from google.oauth2.service_account import Credentials

from config.config import SERVICE_ACCOUNT

creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
client = gspread.authorize(creds)
