package com.horseracing.api.controller;

import com.horseracing.api.dto.RunnerResultDto;
import com.horseracing.api.repository.RunnerResultRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/results")
@CrossOrigin(origins = "*")
@Tag(name = "Results", description = "Official race results and payoffs")
public class ResultController {

    private final RunnerResultRepository runnerResultRepository;

    public ResultController(RunnerResultRepository runnerResultRepository) {
        this.runnerResultRepository = runnerResultRepository;
    }

    @GetMapping("/race/{raceId}")
    @Operation(
            summary = "Get results for a race",
            description = "Returns finish positions and payoffs for completed races"
    )
    public ResponseEntity<List<RunnerResultDto>> getResultsForRace(
            @Parameter(description = "Race database ID", example = "502")
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