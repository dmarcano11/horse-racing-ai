package com.horseracing.api.controller;

import com.horseracing.api.dto.RaceDto;
import com.horseracing.api.dto.RunnerDto;
import com.horseracing.api.repository.RaceRepository;
import com.horseracing.api.repository.RunnerRepository;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/races")
@CrossOrigin(origins = "*")
public class RaceController {

    private final RaceRepository raceRepository;
    private final RunnerRepository runnerRepository;

    public RaceController(RaceRepository raceRepository, RunnerRepository runnerRepository) {
        this.raceRepository = raceRepository;
        this.runnerRepository = runnerRepository;
    }

    @GetMapping
    public ResponseEntity<List<RaceDto>> getRacesByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<RaceDto> races = raceRepository.findByDateOrderByMeetAndRaceNumber(date)
                .stream()
                .map(RaceDto::from)
                .toList();
        return ResponseEntity.ok(races);
    }

    @GetMapping("/{id}")
    public ResponseEntity<RaceDto> getRaceById(@PathVariable Long id) {
        return raceRepository.findById(id)
                .map(RaceDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{id}/runners")
    public ResponseEntity<List<RunnerDto>> getRunnersForRace(@PathVariable Long id) {
        List<RunnerDto> runners = runnerRepository.findActiveRunnersByRaceId(id)
                .stream()
                .map(RunnerDto::from)
                .toList();
        return ResponseEntity.ok(runners);
    }

    @GetMapping("/completed")
    public ResponseEntity<List<RaceDto>> getCompletedRacesByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<RaceDto> races = raceRepository.findCompletedRacesByDate(date)
                .stream()
                .map(RaceDto::from)
                .toList();
        return ResponseEntity.ok(races);
    }
}