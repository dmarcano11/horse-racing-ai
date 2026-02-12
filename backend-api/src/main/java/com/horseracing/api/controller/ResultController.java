package com.horseracing.api.controller;

import com.horseracing.api.dto.RunnerResultDto;
import com.horseracing.api.repository.RunnerResultRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/results")
@CrossOrigin(origins = "*")
public class ResultController {

    private final RunnerResultRepository runnerResultRepository;

    public ResultController(RunnerResultRepository runnerResultRepository) {
        this.runnerResultRepository = runnerResultRepository;
    }

    @GetMapping("/race/{raceId}")
    public ResponseEntity<List<RunnerResultDto>> getResultsForRace(
            @PathVariable Long raceId
    ) {
        List<RunnerResultDto> results = runnerResultRepository
                .findByRaceIdOrderByPosition(raceId)
                .stream()
                .map(RunnerResultDto::from)
                .toList();

        if (results.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok(results);
    }
}