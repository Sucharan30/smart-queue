import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.token import TokenDetailResponse, TokenEventResponse
from app.services.token_service import TokenService

router = APIRouter(prefix="/api/tokens", tags=["Tokens"])


@router.get(
    "/{token_id}",
    response_model=TokenDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Token Details",
    description="Returns public token details with masked patient privacy information.",
)
def get_token(
    token_id: uuid.UUID, db: Session = Depends(get_db)
) -> TokenDetailResponse:
    return TokenService.get_token_by_id(db=db, token_id=token_id)


@router.get(
    "/{token_id}/events",
    response_model=List[TokenEventResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Token Event History",
    description="Returns recorded event transition audit log for the token.",
)
def get_token_events(
    token_id: uuid.UUID, db: Session = Depends(get_db)
) -> List[TokenEventResponse]:
    return TokenService.get_token_events(db=db, token_id=token_id)
