package com.horseracing.api.repository;

import com.horseracing.api.entity.RunnerResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface RunnerResultRepository extends JpaRepository<RunnerResult, Long> {

    @Query("""
        SELECT rr FROM RunnerResult rr
        JOIN FETCH rr.runner r
        JOIN FETCH r.horse
        WHERE rr.raceResult.race.id = :raceId
        ORDER BY rr.finishPosition
        """)
    List<RunnerResult> findByRaceIdOrderByPosition(Long raceId);
}