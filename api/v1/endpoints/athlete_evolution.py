from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from core.database import get_session
from core.security import get_current_user
from models.users import User
from schemas.athlete_evolution import CompetitionCreate, CompetitionOut, DailyJournalCreate, GameStatsCreate, GoalCreate
from repositories.athlete_evolution_repository import AthleteEvolutionRepository

router = APIRouter(prefix="/athlete", tags=["Evolução do Atleta"])

def require_premium(user: User = Depends(get_current_user)):
    if not user.premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta funcionalidade é exclusiva para usuários Premium do Ballers085."
        )
    return user

# --- DIÁRIO DO ATLETA ---
@router.post("/journal", status_code=status.HTTP_201_CREATED)
def create_or_update_journal(
    data: DailyJournalCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.save_daily_journal(current_user.id, data)

@router.get("/journal")
def get_journal(
    days: int = 90,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.get_daily_journals(current_user.id, days)

# --- ESTATÍSTICAS DE JOGOS ---
@router.post("/game", status_code=status.HTTP_201_CREATED)
def create_game_stats(
    data: GameStatsCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    try:
        return repo.save_game_stats(current_user.id, data)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.get("/game")
def get_games(
    limit: int = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.get_game_stats(current_user.id, limit)

@router.delete("/game/{game_id}")
def delete_game(
    game_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    success = repo.delete_game_stats(current_user.id, game_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Partida não encontrada.")
    return {"message": "Partida removida com sucesso"}

@router.post("/competitions", status_code=status.HTTP_201_CREATED)
def create_competition(
    data: CompetitionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    try:
        return repo.save_competition(current_user.id, data)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))

@router.get("/competitions")
def get_competitions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.get_competitions(current_user.id)

@router.delete("/competitions/{competition_id}")
def delete_competition(
    competition_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    competition = repo.delete_competition(current_user.id, competition_id)
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competição não encontrada.")
    if competition.active is False:
        return {"message": "Competição desativada porque existem partidas vinculadas."}
    return {"message": "Competição removida com sucesso."}

# --- METAS ---
# @router.post("/goals", status_code=status.HTTP_201_CREATED)
# def create_goal(
#     data: GoalCreate,
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     repo = AthleteEvolutionRepository(session)
#     return repo.save_goal(current_user.id, data)
# 
# @router.get("/goals")
# def get_goals(
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     repo = AthleteEvolutionRepository(session)
#     return repo.get_goals(current_user.id)
# 
# @router.delete("/goals/{goal_id}")
# def delete_goal(
#     goal_id: int,
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     repo = AthleteEvolutionRepository(session)
#     success = repo.delete_goal(current_user.id, goal_id)
#     if not success:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada.")
#     return {"message": "Meta removida com sucesso"}
# 
# @router.patch("/goals/{goal_id}/toggle")
# def toggle_goal(
#     goal_id: int,
#     current_user: User = Depends(get_current_user),
#     session: Session = Depends(get_session)
# ):
#     repo = AthleteEvolutionRepository(session)
#     goal = repo.toggle_goal_completed(current_user.id, goal_id)
#     if not goal:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meta não encontrada.")
#     return goal

# --- DASHBOARD DE EVOLUÇÃO ---
@router.get("/dashboard")
def get_dashboard(
    days: int = 30,
    current_user: User = Depends(require_premium),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.get_dashboard_data(current_user.id, days)

# --- COMPETIÇÕES ---
@router.post("/competitions", status_code=status.HTTP_201_CREATED, response_model=CompetitionOut)
def create_competition(
    data: CompetitionCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    try:
        return repo.save_competition(current_user.id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/competitions", response_model=list[CompetitionOut])
def list_competitions(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    return repo.get_competitions(current_user.id)

@router.delete("/competitions/{competition_id}")
def delete_competition(
    competition_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    repo = AthleteEvolutionRepository(session)
    competition = repo.delete_competition(current_user.id, competition_id)
    if not competition:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Competição não encontrada.")
    return {"message": "Competição removida ou desativada com sucesso"}

