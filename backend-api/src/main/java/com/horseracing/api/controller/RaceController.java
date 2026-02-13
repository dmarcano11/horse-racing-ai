package com.horseracing.api.controller;

import com.horseracing.api.dto.RaceDto;
import com.horseracing.api.dto.RunnerDto;
import com.horseracing.api.dto.RaceCardDto;
import com.horseracing.api.service.RaceCardService;
import com.horseracing.api.repository.RaceRepository;
import com.horseracing.api.repository.RunnerRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/races")
@CrossOrigin(origins = "*")
@Tag(name = "Races", description = "Race cards, entries and results")
public class RaceController {

    private final RaceRepository raceRepository;
    private final RunnerRepository runnerRepository;
    private final RaceCardService raceCardService;

    public RaceController(
            RaceRepository raceRepository,
            RunnerRepository runnerRepository,
            RaceCardService raceCardService
    ) {
        this.raceRepository = raceRepository;
        this.runnerRepository = runnerRepository;
        this.raceCardService = raceCardService;
    }

    @GetMapping
    @Operation(
            summary = "Get races by date",
            description = "Returns all races for a specific date across all tracks"
    )
    public ResponseEntity<List<RaceDto>> getRacesByDate(
            @Parameter(description = "Race date (YYYY-MM-DD)", example = "2026-02-07")
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<RaceDto> races = raceRepository
                .findByDateOrderByMeetAndRaceNumber(date)
                .stream()
                .map(RaceDto::from)
                .toList();
        return ResponseEntity.ok(races);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get race by ID")
    public ResponseEntity<RaceDto> getRaceById(
            @Parameter(description = "Race database ID", example = "502")
            @PathVariable Long id
    ) {
        return raceRepository.findById(id)
                .map(RaceDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{id}/runners")
    @Operation(
            summary = "Get runners for a race",
            description = "Returns all non-scratched runners with jockey and trainer info"
    )
    public ResponseEntity<List<RunnerDto>> getRunnersForRace(
            @Parameter(description = "Race database ID", example = "502")
            @PathVariable Long id
    ) {
        List<RunnerDto> runners = runnerRepository
                .findActiveRunnersByRaceId(id)
                .stream()
                .map(RunnerDto::from)
                .toList();
        return ResponseEntity.ok(runners);
    }

    @GetMapping("/completed")
    @Operation(
            summary = "Get completed races by date",
            description = "Returns only races that have official results"
    )
    public ResponseEntity<List<RaceDto>> getCompletedRacesByDate(
            @Parameter(description = "Race date (YYYY-MM-DD)", example = "2026-02-06")
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<RaceDto> races = raceRepository
                .findCompletedRacesByDate(date)
                .stream()
                .map(RaceDto::from)
                .toList();
        return ResponseEntity.ok(races);
    }

    @GetMapping("/{id}/card")
    @Operation(
            summary = "Get complete race card",
            description = """
        Returns everything needed to display a race:
        - Race details (distance, surface, purse)
        - All active runners with jockey and trainer
        - ML win probability predictions (sorted by model rank)
        - Official results if race is completed
        """
    )
    public ResponseEntity<RaceCardDto> getRaceCard(
            @Parameter(description = "Race database ID", example = "502")
            @PathVariable Long id,
            @Parameter(description = "Include ML predictions", example = "true")
            @RequestParam(defaultValue = "true") boolean predictions
    ) {
        try {
            RaceCardDto raceCard = raceCardService.getRaceCard(id, predictions);
            return ResponseEntity.ok(raceCard);
        } catch (RuntimeException e) {
            return ResponseEntity.notFound().build();
        }
    }
}