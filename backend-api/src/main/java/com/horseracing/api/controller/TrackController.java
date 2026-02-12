package com.horseracing.api.controller;

import com.horseracing.api.dto.TrackDto;
import com.horseracing.api.repository.TrackRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/tracks")
@CrossOrigin(origins = "*")
public class TrackController {

    private final TrackRepository trackRepository;

    public TrackController(TrackRepository trackRepository) {
        this.trackRepository = trackRepository;
    }

    @GetMapping
    public ResponseEntity<List<TrackDto>> getAllTracks() {
        List<TrackDto> tracks = trackRepository.findAll()
                .stream()
                .map(TrackDto::from)
                .toList();
        return ResponseEntity.ok(tracks);
    }

    @GetMapping("/{id}")
    public ResponseEntity<TrackDto> getTrackById(@PathVariable Long id) {
        return trackRepository.findById(id)
                .map(TrackDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}