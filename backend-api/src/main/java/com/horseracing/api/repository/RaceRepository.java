package com.horseracing.api.repository;

import com.horseracing.api.entity.Race;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface RaceRepository extends JpaRepository<Race, Long> {

    List<Race> findByMeetIdOrderByRaceNumberAsc(Long meetId);

    @Query("""
        SELECT r FROM Race r
        JOIN r.meet m
        WHERE m.date = :date
        ORDER BY m.id, r.raceNumber
        """)
    List<Race> findByDateOrderByMeetAndRaceNumber(LocalDate date);

    @Query("""
        SELECT r FROM Race r
        JOIN r.meet m
        WHERE m.date = :date
        AND r.hasResults = true
        ORDER BY m.id, r.raceNumber
        """)
    List<Race> findCompletedRacesByDate(LocalDate date);
}