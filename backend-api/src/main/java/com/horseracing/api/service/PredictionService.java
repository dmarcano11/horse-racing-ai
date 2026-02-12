package com.horseracing.api.service;

import com.horseracing.api.entity.Runner;
import com.horseracing.api.repository.RunnerRepository;
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
    private static final String ML_SERVICE_URL = "http://localhost:5001";

    public PredictionService(RunnerRepository runnerRepository) {
        this.restTemplate = new RestTemplate();
        this.runnerRepository = runnerRepository;
    }

    public boolean isHealthy() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                    ML_SERVICE_URL + "/health",
                    Map.class
            );
            return response.getStatusCode() == HttpStatus.OK;
        } catch (Exception e) {
            log.warn("ML service health check failed: {}", e.getMessage());
            return false;
        }
    }

    public Map<String, Object> predictRace(Long raceId) {
        // Get active runners for this race
        List<Runner> runners = runnerRepository.findActiveRunnersByRaceId(raceId);

        if (runners.isEmpty()) {
            return Map.of(
                    "race_id", raceId,
                    "error", "No active runners found for this race"
            );
        }

        // Build feature maps for each runner
        List<Map<String, Object>> runnerFeatures = new ArrayList<>();
        for (Runner runner : runners) {
            runnerFeatures.add(buildRunnerFeatures(runner));
        }

        // Call Flask ML service
        return callMlService(raceId, runnerFeatures);
    }

    private Map<String, Object> buildRunnerFeatures(Runner runner) {
        Map<String, Object> features = new HashMap<>();

        features.put("runner_id", runner.getId());

        // Odds features
        double mlOdds = runner.getMorningLineDecimal() != null
                ? runner.getMorningLineDecimal() : 0.0;
        features.put("ml_odds_decimal", mlOdds);
        features.put("ml_odds_prob", mlOdds > 0 ? 1.0 / (mlOdds + 1.0) : 0.0);

        // Post position
        int postPos = 0;
        try {
            if (runner.getPostPosition() != null) {
                postPos = Integer.parseInt(runner.getPostPosition().trim());
            }
        } catch (NumberFormatException e) {
            postPos = 0;
        }
        features.put("post_position", postPos);

        // Default remaining features to 0 - Flask will handle missing values
        // These would ideally come from the feature engineering pipeline
        String[] defaultFeatures = {
                "jockey_win_rate", "jockey_total_races", "jockey_roi",
                "jockey_track_win_rate", "jockey_track_races",
                "jockey_win_rate_7d", "jockey_races_7d",
                "jockey_win_rate_30d", "jockey_races_30d",
                "jockey_win_rate_90d", "jockey_races_90d",
                "trainer_win_rate", "trainer_total_races", "trainer_roi",
                "trainer_track_win_rate", "trainer_track_races",
                "trainer_win_rate_7d", "trainer_races_7d",
                "trainer_win_rate_30d", "trainer_races_30d",
                "trainer_win_rate_90d", "trainer_races_90d",
                "horse_win_rate", "horse_total_races",
                "horse_avg_finish", "horse_days_since_last_race",
                "horse_career_earnings",
                "field_size", "post_position_normalized",
                "race_distance", "race_distance_furlongs",
                "race_purse", "race_min_claim_price", "race_max_claim_price",
                "is_graded_stakes", "weight_carried",
                "surface_dirt", "surface_turf", "surface_synthetic",
                "race_type_maiden", "race_type_claiming",
                "race_type_allowance", "race_type_stakes",
                "ml_odds_rank", "is_favorite",
                "odds_category_heavy_favorite", "odds_category_favorite",
                "odds_category_second_tier", "odds_category_mid_price",
                "odds_category_longshot", "odds_category_extreme_longshot",
                "odds_category_unknown"
        };

        for (String feature : defaultFeatures) {
            features.putIfAbsent(feature, 0.0);
        }

        return features;
    }

    private Map<String, Object> callMlService(
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
                    ML_SERVICE_URL + "/predict/race",
                    request,
                    Map.class
            );

            // Enrich predictions with runner info
            Map<String, Object> result = new HashMap<>(response.getBody());
            result.put("race_id", raceId);
            result.put("note", "Predictions based on morning line odds only. " +
                    "Full feature predictions require historical data.");

            return result;

        } catch (Exception e) {
            log.error("ML service call failed: {}", e.getMessage());
            throw new RuntimeException("ML service unavailable: " + e.getMessage());
        }
    }
}