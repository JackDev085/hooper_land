from fastapi import APIRouter, status, HTTPException, Depends
from repositories.user_repository import UserRepository
from repositories.reviews_repository import ReviewsRepository
from models.review import Reviews
from core.security import get_current_user
from models.users import User
from sqlmodel import Session
from core.database import get_session
from schemas.review import ReviewsPosCreate, ReviewsPreCreate

router = APIRouter(tags=["Avaliação"])

@router.post("/create/pos")
async def create_pos_review(review: ReviewsPosCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)): 
    """Cria uma nova avaliação pós-treino para o usuário"""
    review_repository = ReviewsRepository(session)
    response = review_repository.create_pos_review(review, current_user.id)

    if response is True:
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Avaliação criada com sucesso")

    if isinstance(response, dict) and "detail" in response: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["detail"])

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar avaliação")

@router.post("/create/pre")
async def create_pre_review(review: ReviewsPreCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)): 
    """Cria uma nova avaliação pré-treino para o usuário"""
    review_repository = ReviewsRepository(session)
    response = review_repository.create_pre_review(review, current_user.id)

    if response is True:
        raise HTTPException(status_code=status.HTTP_201_CREATED, detail="Avaliação criada com sucesso")

    if isinstance(response, dict) and "detail" in response: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response["detail"])

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar avaliação")
