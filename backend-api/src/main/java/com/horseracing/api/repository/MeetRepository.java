package com.horseracing.api.repository;

import com.horseracing.api.entity.Meet;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.time.LocalDate;
import java.util.List;

@Repository
public interface MeetRepository extends JpaRepository<Meet, Long> {

    List<Meet> findByDateOrderByIdAsc(LocalDate date);

    List<Meet> findByDateBetweenOrderByDateAsc(LocalDate startDate, LocalDate endDate);

    @Query("SELECT m FROM Meet m JOIN FETCH m.track WHERE m.date = :date")
    List<Meet> findByDateWithTrack(LocalDate date);
}