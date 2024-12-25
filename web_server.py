from fastapi import FastAPI, Request
from database import requests1 as db
import requests

app = FastAPI()

HH_CLIENT_ID = ""
HH_CLIENT_SECRET = ""
HH_AUTHORIZATION_URL = ""
HH_TOKEN_URL = ""
HH_REDIRECT_URI = ""


@app.get("/")
def read_root():
    return {"Hello": "Navigate to /redirect to simulate the OAuth redirect."}

def get_access_token(code):
    token_url = "https://hh.ru/oauth/token"
    data = {
        'grant_type': 'authorization_code',
        'client_id': HH_CLIENT_ID,
        'client_secret': HH_CLIENT_SECRET,
        'code': code,
        'redirect_uri': HH_REDIRECT_URI
    }
    response = requests.post(token_url, data=data)
    return response.json()['access_token']

@app.get("/redirect")
async def read_code(request: Request):
    user_id = request.query_params.get('state')
    code = request.query_params.get('code')
    if code and user_id:
        token = get_access_token(code)
        print(token)
        await db.insert_token(user_id, token)
        return 'Вы авторизировались'
    return {"Error": "Required parameters are missing."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)