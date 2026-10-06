from fastapi import APIRouter, status

from app.api.deps import (
    AuthServiceDep,
    CurrentMembership,
    CurrentOrganization,
    CurrentUser,
)
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    RegisterRequest,
    RegistrationResponse,
    TokenResponse,
)
from app.schemas.organization import OrganizationMembershipRead, OrganizationRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth")


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    auth_service: AuthServiceDep,
) -> RegistrationResponse:
    result = auth_service.register(payload)
    return RegistrationResponse(
        user=UserRead.model_validate(result.user),
        organization=OrganizationRead.model_validate(result.organization),
        membership=OrganizationMembershipRead.model_validate(result.membership),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, auth_service: AuthServiceDep) -> TokenResponse:
    return auth_service.login(payload)


@router.get("/me", response_model=CurrentUserResponse)
def get_me(
    user: CurrentUser,
    membership: CurrentMembership,
    organization: CurrentOrganization,
) -> CurrentUserResponse:
    return CurrentUserResponse(
        user=UserRead.model_validate(user),
        organization=OrganizationRead.model_validate(organization),
        membership=OrganizationMembershipRead.model_validate(membership),
    )
