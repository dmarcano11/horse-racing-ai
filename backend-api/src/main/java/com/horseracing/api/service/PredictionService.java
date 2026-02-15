package com.horseracing.api.service;

import com.horseracing.api.entity.Runner;
import com.horseracing.api.repository.RunnerRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;
import java.util.*;
import lombok.extern.slf4j.Slf4j;

@Service
@Slf4j
public class PredictionService {

    private final RestTemplate restTemplate;
    private final RunnerRepository runnerRepository;

    @Value("${ML_SERVICE_URL:http://localhost:5001}")
    private String mlServiceUrl;

    public PredictionService(RunnerRepository runnerRepository) {
        this.restTemplate = new RestTemplate();
        this.runnerRepository = runnerRepository;
    }

    public boolean isHealthy() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                    mlServiceUrl + "/health",
                    Map.class
            );
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.warn("ML service health check failed: {}", e.getMessage());
            return false;
        }
    }

    public Map<String, Object> predictRace(Long raceId) {
        // Try full feature pipeline first
        try {
            log.info("Attempting full feature prediction for race {}", raceId);
            ResponseEntity<Map> response = restTemplate.getForEntity(
                    mlServiceUrl + "/predict/race/" + raceId,
                    Map.class
            );
            if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
                log.info("✓ Full feature prediction successful for race {}", raceId);
                return response.getBody();
            }
        } catch (Exception e) {
            log.warn("Full feature prediction failed, falling back: {}", e.getMessage());
        }

        // Fallback to basic prediction using morning line odds
        log.info("Using basic prediction for race {}", raceId);
        return basicPrediction(raceId);
    }

    private Map<String, Object> basicPrediction(Long raceId) {
        List<Runner> runners = runnerRepository.findActiveRunnersByRaceId(raceId);

        if (runners.isEmpty()) {
            return Map.of(
                    "race_id", raceId,
                    "error", "No active runners found"
            );
        }

        List<Map<String, Object>> runnerFeatures = runners.stream()
                .map(this::buildBasicFeatures)
                .toList();

        return callMlServicePost(raceId, runnerFeatures);
    }

    private Map<String, Object> buildBasicFeatures(Runner runner) {
        Map<String, Object> features = new HashMap<>();
        features.put("runner_id", runner.getId());

        double mlOdds = runner.getMorningLineDecimal() != null
                ? runner.getMorningLineDecimal() : 0.0;
        features.put("ml_odds_decimal", mlOdds);
        features.put("ml_odds_prob", mlOdds > 0 ? 1.0 / (mlOdds + 1.0) : 0.0);

        int postPos = 0;
        try {
            if (runner.getPostPosition() != null) {
                postPos = Integer.parseInt(runner.getPostPosition().trim());
            }
        } catch (NumberFormatException e) {
            postPos = 0;
        }
        features.put("post_position", postPos);

        return features;
    }

    private Map<String, Object> callMlServicePost(
            Long raceId,
            List<Map<String, Object>> runners
    ) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            Map<String, Object> body = new HashMap<>();
            body.put("race_id", raceId);
            body.put("runners", runners);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    mlServiceUrl + "/predict/race",
                    request,
                    Map.class
            );

            // Add null check
            if (response.getBody() == null) {
                log.error("ML service returned null body for race {}", raceId);
                throw new RuntimeException("ML service returned empty response");
            }

            Map<String, Object> result = new HashMap<>(response.getBody());
            result.put("note", "Basic prediction using morning line odds only");
            result.put("features", "basic");
            return result;

        } catch (Exception e) {
            log.error("ML service call failed: {}", e.getMessage());
            throw new RuntimeException("ML service unavailable: " + e.getMessage());
        }
    }
}