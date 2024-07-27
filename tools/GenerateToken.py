
import uuid
def generate_token(user) -> str:
    token =  str(uuid.uuid4().hex)
    user['token'] = token
    return token