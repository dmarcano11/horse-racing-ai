package com.horseracing.api.repository;

import com.horseracing.api.entity.Runner;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface RunnerRepository extends JpaRepository<Runner, Long> {

    @Query("""
        SELECT r FROM Runner r
        JOIN FETCH r.horse
        LEFT JOIN FETCH r.jockey
        LEFT JOIN FETCH r.trainer
        WHERE r.race.id = :raceId
        AND (r.isScratched = false OR r.isScratched IS NULL)
        ORDER BY r.postPosition
        """)
    List<Runner> findActiveRunnersByRaceId(Long raceId);
}