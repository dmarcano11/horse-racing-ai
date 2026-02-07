"""Useful database queries."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import date

from src.db.session import get_db_context
from src.db.models import (
    Track, Meet, Race, Runner, Horse, Jockey, Trainer,
    RaceResult, RunnerResult, Payoff
)


def get_database_stats():
    """Print database statistics."""
    with get_db_context() as db:
        print("\n" + "=" * 60)
        print("DATABASE STATISTICS")
        print("=" * 60)

        # Count records
        tracks_count = db.query(Track).count()
        meets_count = db.query(Meet).count()
        races_count = db.query(Race).count()
        horses_count = db.query(Horse).count()
        jockeys_count = db.query(Jockey).count()
        trainers_count = db.query(Trainer).count()
        runners_count = db.query(Runner).count()
        results_count = db.query(RaceResult).count()
        payoffs_count = db.query(Payoff).count()

        print(f"\nTracks:         {tracks_count:,}")
        print(f"Meets:          {meets_count:,}")
        print(f"Races:          {races_count:,}")
        print(f"Horses:         {horses_count:,}")
        print(f"Jockeys:        {jockeys_count:,}")
        print(f"Trainers:       {trainers_count:,}")
        print(f"Runners:        {runners_count:,}")
        print(f"Race Results:   {results_count:,}")
        print(f"Payoffs:        {payoffs_count:,}")

        # Calculate averages using subquery approach
        # Average races per meet
        from sqlalchemy import select
        subq = select(
            Meet.id,
            func.count(Race.id).label('race_count')
        ).join(Race).group_by(Meet.id).subquery()

        avg_races = db.query(func.avg(subq.c.race_count)).scalar()

        # Average runners per race
        subq2 = select(
            Race.id,
            func.count(Runner.id).label('runner_count')
        ).join(Runner).group_by(Race.id).subquery()

        avg_runners = db.query(func.avg(subq2.c.runner_count)).scalar()

        if avg_races:
            print(f"\nAvg Races per Meet:    {avg_races:.1f}")
        if avg_runners:
            print(f"Avg Runners per Race:  {avg_runners:.1f}")

        # Date range
        first_meet = db.query(Meet).order_by(Meet.date.asc()).first()
        last_meet = db.query(Meet).order_by(Meet.date.desc()).first()

        if first_meet and last_meet:
            print(f"\nDate Range: {first_meet.date} to {last_meet.date}")

        # Completion percentage
        if races_count > 0:
            completion_pct = (results_count / races_count) * 100
            print(f"Results Completion: {completion_pct:.1f}% ({results_count}/{races_count})")

        print("=" * 60)


def show_recent_races(limit: int = 10):
    """Show recent races with runners."""
    with get_db_context() as db:
        races = db.query(Race).join(Race.meet).order_by(
            Meet.date.desc(), Race.race_number.asc()
        ).limit(limit).all()

        print("\n" + "=" * 60)
        print(f"RECENT RACES (Last {limit})")
        print("=" * 60)

        for race in races:
            runners_count = db.query(Runner).filter(Runner.race_id == race.id).count()
            results = db.query(RaceResult).filter(RaceResult.race_id == race.id).first()

            print(f"\n{race.meet.track.track_name} - {race.meet.date}")
            print(f"  Race {race.race_number}: {race.race_name or 'N/A'}")
            print(f"  {race.distance_value} {race.distance_unit} - {race.surface_description}")
            print(f"  Runners: {runners_count}, Has Results: {race.has_results}")

            if results:
                winner = db.query(RunnerResult).join(RunnerResult.runner).filter(
                    RunnerResult.race_result_id == results.id,
                    RunnerResult.finish_position == 1
                ).first()

                if winner:
                    print(
                        f"  Winner: {winner.runner.horse.name} (${winner.win_payoff:.2f})" if winner.win_payoff else f"  Winner: {winner.runner.horse.name}")


def show_top_jockeys(limit: int = 10):
    """Show jockeys with most wins."""
    with get_db_context() as db:
        # Count wins per jockey
        jockey_wins = db.query(
            Jockey,
            func.count(RunnerResult.id).label('wins')
        ).join(
            Runner, Runner.jockey_id == Jockey.id
        ).join(
            RunnerResult, RunnerResult.runner_id == Runner.id
        ).filter(
            RunnerResult.finish_position == 1
        ).group_by(
            Jockey.id
        ).order_by(
            func.count(RunnerResult.id).desc()
        ).limit(limit).all()

        print("\n" + "=" * 60)
        print(f"TOP JOCKEYS BY WINS")
        print("=" * 60)

        for jockey, wins in jockey_wins:
            total_rides = db.query(Runner).filter(Runner.jockey_id == jockey.id).count()
            win_pct = (wins / total_rides * 100) if total_rides > 0 else 0
            print(f"{jockey.first_name} {jockey.last_name:20s} {wins:3d} wins ({win_pct:.1f}%) in {total_rides} rides")


if __name__ == "__main__":
    get_database_stats()
    show_recent_races(5)
    show_top_jockeys(10)