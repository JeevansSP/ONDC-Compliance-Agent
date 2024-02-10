import requests
from Auth.config import *
from DatabaseHandler import *
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def google_auth(code:str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    access_token = response.json().get("access_token")
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    userDetails = user_info.json()
    userDetails['access_token'] = access_token

    
    # We'll check if the user already exists
    query_check = f"SELECT * FROM {user_table} WHERE user_id='{userDetails['id']}'"

    # fetch the user details
    fetch_user_details = executeQueryAndReturnJson(query_check)
    print(fetch_user_details)
    # checks if the user exists
    if len(fetch_user_details) <= 0:
        query = f"""INSERT INTO {user_table} (user_id,user_name,user_email) VALUES (?,?,?)"""
        values = (userDetails['id'], userDetails['name'], userDetails['email'])
        executeNonSelectQuery(query, values)
        
    
    return access_token

def loginUrl():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={GOOGLE_CLIENT_ID}&redirect_uri={GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email&access_type=offline"
    }

def get_user_info(access_token: str):
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    query = f"SELECT * FROM {user_table} WHERE user_id='{user_info.json()['id']}' LIMIT 1 ;"
    print("User info "+ user_info.json()['id'])
    userDetails = executeQueryAndReturnJson(query)
    
    if user_info.status_code != 200 or userDetails is None:
        raise HTTPException(status_code=user_info.status_code, detail="Failed to fetch user info")
    print(userDetails)
    return userDetails[0]

def verify_access_token(access_token:str) -> bool:
    user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    if user_info.status_code != 200:
        return False
    return True
    