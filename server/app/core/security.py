from fastapi.security import OAuth2PasswordBearer

# auto_error=False allows the dependency to return None instead of raising 401
# This lets us check cookies first before falling back to header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/token", auto_error=False)
