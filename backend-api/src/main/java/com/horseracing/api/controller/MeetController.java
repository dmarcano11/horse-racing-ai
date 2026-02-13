package com.horseracing.api.controller;

import com.horseracing.api.dto.MeetDto;
import com.horseracing.api.repository.MeetRepository;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/meets")
@CrossOrigin(origins = "*")
@Tag(name = "Meets", description = "Race meet information by date")
public class MeetController {

    private final MeetRepository meetRepository;

    public MeetController(MeetRepository meetRepository) {
        this.meetRepository = meetRepository;
    }

    @GetMapping
    @Operation(
            summary = "Get meets by date",
            description = "Returns all race meets for a specific date"
    )
    public ResponseEntity<List<MeetDto>> getMeetsByDate(
            @Parameter(description = "Race date (YYYY-MM-DD)", example = "2026-02-07")
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<MeetDto> meets = meetRepository.findByDateWithTrack(date)
                .stream()
                .map(MeetDto::from)
                .toList();
        return ResponseEntity.ok(meets);
    }

    @GetMapping("/{id}")
    @Operation(summary = "Get meet by ID")
    public ResponseEntity<MeetDto> getMeetById(
            @Parameter(description = "Meet database ID", example = "87")
            @PathVariable Long id
    ) {
        return meetRepository.findById(id)
                .map(MeetDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}