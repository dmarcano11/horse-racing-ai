package com.horseracing.api.controller;

import com.horseracing.api.dto.TrackDto;
import com.horseracing.api.repository.TrackRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/tracks")
@CrossOrigin(origins = "*")
@Tag(name = "Tracks", description = "Race track information")
public class TrackController {

    private final TrackRepository trackRepository;

    public TrackController(TrackRepository trackRepository) {
        this.trackRepository = trackRepository;
    }

    @GetMapping
    @Operation(
            summary = "Get all tracks",
            description = "Returns all 21 race tracks in the system"
    )
    public ResponseEntity<List<TrackDto>> getAllTracks() {
        List<TrackDto> tracks = trackRepository.findAll()
                .stream()
                .map(TrackDto::from)
                .toList();
        return ResponseEntity.ok(tracks);
    }

    @GetMapping("/{id}")
    @Operation(
            summary = "Get track by ID",
            description = "Returns a single track by its database ID"
    )
    public ResponseEntity<TrackDto> getTrackById(
            @Parameter(description = "Track database ID", example = "1")
            @PathVariable Long id
    ) {
        return trackRepository.findById(id)
                .map(TrackDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}