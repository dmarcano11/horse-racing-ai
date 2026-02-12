package com.horseracing.api.controller;

import com.horseracing.api.dto.MeetDto;
import com.horseracing.api.repository.MeetRepository;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDate;
import java.util.List;

@RestController
@RequestMapping("/api/meets")
@CrossOrigin(origins = "*")
public class MeetController {

    private final MeetRepository meetRepository;

    public MeetController(MeetRepository meetRepository) {
        this.meetRepository = meetRepository;
    }

    @GetMapping
    public ResponseEntity<List<MeetDto>> getMeetsByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date
    ) {
        List<MeetDto> meets = meetRepository.findByDateWithTrack(date)
                .stream()
                .map(MeetDto::from)
                .toList();
        return ResponseEntity.ok(meets);
    }

    @GetMapping("/{id}")
    public ResponseEntity<MeetDto> getMeetById(@PathVariable Long id) {
        return meetRepository.findById(id)
                .map(MeetDto::from)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}