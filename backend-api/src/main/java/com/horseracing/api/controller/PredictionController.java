package com.horseracing.api.controller;

import com.horseracing.api.service.PredictionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import lombok.extern.slf4j.Slf4j;
import java.util.Map;

@RestController
@RequestMapping("/api/predictions")
@CrossOrigin(origins = "*")
@Slf4j
public class PredictionController {

    private final PredictionService predictionService;

    public PredictionController(PredictionService predictionService) {
        this.predictionService = predictionService;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> mlHealth() {
        boolean healthy = predictionService.isHealthy();
        return ResponseEntity.ok(Map.of(
                "ml_service_available", healthy,
                "status", healthy ? "connected" : "unavailable"
        ));
    }

    @GetMapping("/race/{raceId}")
    public ResponseEntity<Map<String, Object>> predictRace(
            @PathVariable Long raceId
    ) {
        try {
            Map<String, Object> predictions = predictionService.predictRace(raceId);
            return ResponseEntity.ok(predictions);
        } catch (Exception e) {
            log.error("Prediction failed for race {}: {}", raceId, e.getMessage());
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", e.getMessage(),
                    "race_id", raceId
            ));
        }
    }
}