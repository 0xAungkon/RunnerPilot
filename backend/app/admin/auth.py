from starlette.requests import Request
from sqladmin.authentication import AuthenticationBackend
from app.core.config import settings
import jwt

class AdminAuth(AuthenticationBackend):
    """
    Custom authentication backend for SQLAdmin
    Uses the same JWT token mechanism as the main app
    """
    
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        # Replace this with your actual authentication logic
        # For example, validate against admin users in the database
        if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
            # Set the auth cookie
            token = self._create_token(username)
            request.session.update({"token": token})
            return True
        
        return False

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        
        if not token:
            return False
            
        # Validate the token
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET_KEY, 
                algorithms=[settings.ALGORITHM]
            )
            username = payload.get("sub")
            if username != settings.ADMIN_USERNAME:
                return False
                
            return True
        except jwt.PyJWTError:
            return False
            
    def _create_token(self, username: str) -> str:
        """Create a JWT token for the admin session"""
        to_encode = {"sub": username}
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt