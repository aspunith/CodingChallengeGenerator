from fastapi import HTTPException
from clerk_backend_api import Clerk, AuthenticateRequestOptions
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

clerk_sdk = Clerk(bearer_auth=os.getenv("CLERK_API_KEY"))

def authenticate_and_get_user_details(request):
    """
    Authenticate the user using Clerk and return user details.
    """
    try:
        request_state = clerk_sdk.authenticate_request(
            request,
            AuthenticateRequestOptions(
                authorized_parties = ["http://localhost:5173", "http://localhost:5174"],
                jwt_key=os.getenv("JWT_KEY")  # Ensure JWT_KEY is set in your environment variables, this is used to verify the JWT token, which is fast and network independent
                
            )
        )
        
        if not request_state.is_signed_in:
            raise HTTPException(status_code=401, detail="Invalid Token")
        
        if request_state.payload is None:
            raise HTTPException(status_code=500, detail="Invalid payload")
        
        user_id = request_state.payload.get("sub")
        
        return {"user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invalid credentials")