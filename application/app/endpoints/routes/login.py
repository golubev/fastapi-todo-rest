from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import generate_access_token
from app.endpoints.dependencies import CurrentUserDependency, SessionDependency
from app.models import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserResponse
from app.services import user_service

router = APIRouter()


@router.post("/login/access-token")
def login_for_access_token(
    db: SessionDependency,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenResponse:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = user_service.get_by_credentials_verified(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    subject_user_id: int = user.id  # type: ignore
    return TokenResponse(
        access_token=generate_access_token(subject_user_id), token_type="bearer"
    )


@router.get("/login/who-am-i", response_model=UserResponse)
def read_current_user(
    *,
    current_user: CurrentUserDependency,
) -> User:
    """
    Get current user. Endpoint used to test the auth flow.
    """
    return current_user