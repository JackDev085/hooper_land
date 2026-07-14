from sqlmodel import Session, select
from models.athlete_evolution import Competition, DailyJournal, GameStats, Goal
from models.users import WorkoutLog
from schemas.athlete_evolution import CompetitionCreate, DailyJournalCreate, GameStatsCreate, GoalCreate
from datetime import datetime, timedelta
from typing import Optional
import logging

class AthleteEvolutionRepository:
    def __init__(self, session: Session):
        self.session = session

    # --- DIÁRIO DO ATLETA ---
    def save_daily_journal(self, user_id: int, data: DailyJournalCreate) -> DailyJournal:
        # Check if entry already exists for this date
        entry = self.session.exec(
            select(DailyJournal).where(DailyJournal.user_id == user_id, DailyJournal.date == data.date)
        ).first()

        if entry:
            # Update existing
            entry.sleep_hours = data.sleep_hours
            entry.water_liters = data.water_liters
            entry.stretched = data.stretched
            entry.mobility = data.mobility
            entry.trained_basketball = data.trained_basketball
            entry.gym = data.gym
            entry.cardio = data.cardio
            entry.energy = data.energy
            entry.muscle_pain = data.muscle_pain
            entry.motivation = data.motivation
            entry.confidence = data.confidence
            entry.notes = data.notes
        else:
            # Create new
            entry = DailyJournal(
                user_id=user_id,
                date=data.date,
                sleep_hours=data.sleep_hours,
                water_liters=data.water_liters,
                stretched=data.stretched,
                mobility=data.mobility,
                trained_basketball=data.trained_basketball,
                gym=data.gym,
                cardio=data.cardio,
                energy=data.energy,
                muscle_pain=data.muscle_pain,
                motivation=data.motivation,
                confidence=data.confidence,
                notes=data.notes
            )
        
        try:
            self.session.add(entry)
            self.session.commit()
            self.session.refresh(entry)
            return entry
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao salvar diário: {e}")
            raise e

    def get_daily_journals(self, user_id: int, days_limit: int = 90) -> list[DailyJournal]:
        cutoff_date = (datetime.now() - timedelta(days=days_limit)).strftime("%Y-%m-%d")
        statement = (
            select(DailyJournal)
            .where(DailyJournal.user_id == user_id, DailyJournal.date >= cutoff_date)
            .order_by(DailyJournal.date.asc())
        )
        return self.session.exec(statement).all()

    # --- ESTATÍSTICAS DE JOGOS ---
    def save_game_stats(self, user_id: int, data: GameStatsCreate) -> GameStats:
        if data.competition_id is not None:
            competition = self.session.exec(
                select(Competition).where(
                    Competition.id == data.competition_id,
                    Competition.user_id == user_id,
                    Competition.active == True
                )
            ).first()
            if not competition:
                raise ValueError("Competição inválida para este usuário.")

        entry = GameStats(
            user_id=user_id,
            competition_id=data.competition_id,
            date=data.date,
            opponent=data.opponent,
            result=data.result,
            points=data.points,
            ft_made=data.ft_made,
            ft_attempted=data.ft_attempted,
            fg2_made=data.fg2_made,
            fg2_attempted=data.fg2_attempted,
            fg3_made=data.fg3_made,
            fg3_attempted=data.fg3_attempted,
            assists=data.assists,
            turnovers=data.turnovers,
            offensive_rebounds=data.offensive_rebounds,
            defensive_rebounds=data.defensive_rebounds,
            steals=data.steals,
            blocks=data.blocks,
            fouls_committed=data.fouls_committed,
            fouls_drawn=data.fouls_drawn
        )
        try:
            self.session.add(entry)
            self.session.commit()
            self.session.refresh(entry)
            return entry
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao salvar estatísticas de jogo: {e}")
            raise e

    # --- COMPETIÇÕES ---
    def save_competition(self, user_id: int, data: CompetitionCreate) -> Competition:
        normalized_name = data.name.strip()
        if not normalized_name:
            raise ValueError("Nome da competição é obrigatório.")

        existing = self.session.exec(
            select(Competition).where(
                Competition.user_id == user_id,
                Competition.name == normalized_name
            )
        ).first()
        if existing:
            if existing.active:
                raise ValueError("Já existe uma competição com esse nome.")
            existing.active = True
            existing.season = data.season
            try:
                self.session.add(existing)
                self.session.commit()
                self.session.refresh(existing)
                return existing
            except Exception as e:
                self.session.rollback()
                logging.error(f"Erro ao reativar competição: {e}")
                raise e

        competition = Competition(
            user_id=user_id,
            name=normalized_name,
            season=data.season,
            active=True
        )
        try:
            self.session.add(competition)
            self.session.commit()
            self.session.refresh(competition)
            return competition
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao salvar competição: {e}")
            raise e

    def get_competitions(self, user_id: int) -> list[Competition]:
        statement = (
            select(Competition)
            .where(Competition.user_id == user_id)
            .order_by(Competition.active.desc(), Competition.name.asc())
        )
        return self.session.exec(statement).all()

    def delete_competition(self, user_id: int, competition_id: int) -> Optional[Competition]:
        competition = self.session.exec(
            select(Competition).where(
                Competition.user_id == user_id,
                Competition.id == competition_id
            )
        ).first()
        if not competition:
            return None

        linked_game = self.session.exec(
            select(GameStats.id).where(
                GameStats.user_id == user_id,
                GameStats.competition_id == competition_id
            )
        ).first()

        try:
            if linked_game:
                competition.active = False
                self.session.add(competition)
            else:
                self.session.delete(competition)
            self.session.commit()
            if linked_game:
                self.session.refresh(competition)
            return competition
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao remover competição: {e}")
            raise e

    def get_game_stats(self, user_id: int, limit: int = None) -> list[GameStats]:
        statement = select(GameStats).where(GameStats.user_id == user_id).order_by(GameStats.date.desc())
        if limit:
            statement = statement.limit(limit)
        # We fetch desc for averages, but we'll return in chronological order (asc) or desc depending on view
        games = self.session.exec(statement).all()
        return games

    def delete_game_stats(self, user_id: int, game_id: int) -> bool:
        game = self.session.exec(
            select(GameStats).where(GameStats.user_id == user_id, GameStats.id == game_id)
        ).first()
        if not game:
            return False
        try:
            self.session.delete(game)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao deletar jogo: {e}")
            raise e

    # --- METAS ---
    def save_goal(self, user_id: int, data: GoalCreate) -> Goal:
        entry = Goal(
            user_id=user_id,
            name=data.name,
            goal_type=data.goal_type,
            metric=data.metric,
            target_value=data.target_value,
            start_date=data.start_date,
            end_date=data.end_date,
            completed=False
        )
        try:
            self.session.add(entry)
            self.session.commit()
            self.session.refresh(entry)
            return entry
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao salvar meta: {e}")
            raise e

    def get_goals(self, user_id: int) -> list[Goal]:
        return self.session.exec(select(Goal).where(Goal.user_id == user_id).order_by(Goal.end_date.asc())).all()

    def delete_goal(self, user_id: int, goal_id: int) -> bool:
        goal = self.session.exec(
            select(Goal).where(Goal.user_id == user_id, Goal.id == goal_id)
        ).first()
        if not goal:
            return False
        try:
            self.session.delete(goal)
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao deletar meta: {e}")
            raise e

    def toggle_goal_completed(self, user_id: int, goal_id: int) -> Optional[Goal]:
        goal = self.session.exec(
            select(Goal).where(Goal.user_id == user_id, Goal.id == goal_id)
        ).first()
        if not goal:
            return None
        goal.completed = not goal.completed
        try:
            self.session.add(goal)
            self.session.commit()
            self.session.refresh(goal)
            return goal
        except Exception as e:
            self.session.rollback()
            logging.error(f"Erro ao alternar status da meta: {e}")
            raise e

    # --- COMPUTAÇÃO DE STREAKS E DASHBOARD ---
    def get_journal_streak(self, user_id: int) -> int:
        journals = self.session.exec(
            select(DailyJournal).where(DailyJournal.user_id == user_id).order_by(DailyJournal.date.desc())
        ).all()
        if not journals:
            return 0
        
        recorded_dates = {j.date for j in journals}
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        today_str = today.strftime("%Y-%m-%d")
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        if today_str not in recorded_dates and yesterday_str not in recorded_dates:
            return 0
            
        current_date = today if today_str in recorded_dates else yesterday
        streak = 0
        
        while current_date.strftime("%Y-%m-%d") in recorded_dates:
            streak += 1
            current_date -= timedelta(days=1)
            
        return streak

    def get_dashboard_data(self, user_id: int, days: int = 30) -> dict:
        journals = self.get_daily_journals(user_id, days)
        games = self.get_game_stats(user_id) # all games, sorted by date desc

        # Consistency
        streak = self.get_journal_streak(user_id)
        
        # Workouts in current month
        current_year = datetime.now().year
        current_month = datetime.now().month
        workout_logs = self.session.exec(
            select(WorkoutLog).where(WorkoutLog.user_id == user_id)
        ).all()
        
        workouts_this_month = 0
        for log in workout_logs:
            # check both datetime and str formats safely
            if isinstance(log.completed_at, datetime):
                log_date = log.completed_at
            else:
                try:
                    log_date = datetime.fromisoformat(str(log.completed_at))
                except Exception:
                    continue
            if log_date.year == current_year and log_date.month == current_month:
                workouts_this_month += 1

        # Weekly frequency (logs/workouts in the last 7 days)
        cutoff_7_days = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        recent_journals = [j for j in journals if j.date >= cutoff_7_days]
        weekly_frequency = len([
            j for j in recent_journals 
            if j.trained_basketball or j.gym or j.cardio
        ])

        # Habit tracking charts (chronological order)
        habits_data = []
        for j in journals:
            habits_data.append({
                "date": j.date,
                "sleep_hours": j.sleep_hours,
                "water_liters": j.water_liters,
                "energy": j.energy,
                "muscle_pain": j.muscle_pain,
                "motivation": j.motivation,
                "confidence": j.confidence,
                "trained": j.trained_basketball or j.gym or j.cardio,
                "stretched": j.stretched,
                "mobility": j.mobility,
                "trained_basketball": j.trained_basketball,
                "gym": j.gym,
                "cardio": j.cardio,
                "notes": j.notes
            })

        # Game statistics charts (chronological order for chart rendering)
        games_chronological = sorted(games, key=lambda g: g.date)
        game_stats_data = []
        for g in games_chronological:
            total_rebounds = g.offensive_rebounds + g.defensive_rebounds
            ft_pct = (g.ft_made / g.ft_attempted * 100) if g.ft_attempted else None
            fg2_pct = (g.fg2_made / g.fg2_attempted * 100) if g.fg2_attempted else None
            fg3_pct = (g.fg3_made / g.fg3_attempted * 100) if g.fg3_attempted else None
            game_stats_data.append({
                "id": g.id,
                "date": g.date,
                "opponent": g.opponent,
                "result": g.result,
                "points": g.points,
                "assists": g.assists,
                "rebounds": total_rebounds,
                "steals": g.steals,
                "blocks": g.blocks,
                "fg3_pct": round(fg3_pct, 1) if fg3_pct is not None else None,
                "ft_pct": round(ft_pct, 1) if ft_pct is not None else None,
                "fg2_pct": round(fg2_pct, 1) if fg2_pct is not None else None
            })

        # Monthly comparison: current month vs previous month
        comparison = self.get_monthly_comparison(games)

        return {
            "consistency": {
                "streak": streak,
                "workouts_this_month": workouts_this_month,
                "weekly_frequency": weekly_frequency
            },
            "habits": habits_data,
            "game_stats": game_stats_data,
            "monthly_comparison": comparison
        }

    def get_monthly_comparison(self, games: list[GameStats]) -> dict:
        today = datetime.now()
        
        # Current month range
        cur_year, cur_month = today.year, today.month
        # Previous month range
        if cur_month == 1:
            prev_year, prev_month = cur_year - 1, 12
        else:
            prev_year, prev_month = cur_year, cur_month - 1

        cur_games = []
        prev_games = []

        for g in games:
            try:
                g_date = datetime.strptime(g.date, "%Y-%m-%d")
            except Exception:
                continue
            if g_date.year == cur_year and g_date.month == cur_month:
                cur_games.append(g)
            elif g_date.year == prev_year and g_date.month == prev_month:
                prev_games.append(g)

        def calc_averages(game_list: list[GameStats]):
            if not game_list:
                return {"points": 0, "assists": 0, "fg3_pct": 0}
            total_points = sum(g.points for g in game_list)
            total_assists = sum(g.assists for g in game_list)
            total_fg3_made = sum(g.fg3_made for g in game_list)
            total_fg3_att = sum((g.fg3_attempted or 0) for g in game_list)
            
            fg3_pct = (total_fg3_made / total_fg3_att * 100) if total_fg3_att > 0 else 0
            return {
                "points": total_points / len(game_list),
                "assists": total_assists / len(game_list),
                "fg3_pct": fg3_pct
            }

        cur_avgs = calc_averages(cur_games)
        prev_avgs = calc_averages(prev_games)

        def calc_pct_change(curr, prev):
            if prev == 0:
                return 0 if curr == 0 else 100
            return round(((curr - prev) / prev) * 100, 1)

        return {
            "points_pct": calc_pct_change(cur_avgs["points"], prev_avgs["points"]),
            "assists_pct": calc_pct_change(cur_avgs["assists"], prev_avgs["assists"]),
            "fg3_pct": calc_pct_change(cur_avgs["fg3_pct"], prev_avgs["fg3_pct"]),
            "has_data": len(cur_games) > 0 or len(prev_games) > 0
        }
