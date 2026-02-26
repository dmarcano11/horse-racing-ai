package com.horseracing.api.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.horseracing.api.entity.Runner;
import com.horseracing.api.repository.RunnerRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.RestTemplate;

import java.util.*;

import lombok.extern.slf4j.Slf4j;

@Service
@Slf4j
public class PredictionService {

    private static final int SNIPPET_LEN = 400;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;
    private final RunnerRepository runnerRepository;

    @Value("${ML_SERVICE_URL:http://localhost:5001}")
    private String mlServiceUrl;

    public PredictionService(RunnerRepository runnerRepository, ObjectMapper objectMapper) {
        this.restTemplate = new RestTemplate();
        this.objectMapper = objectMapper;
        this.runnerRepository = runnerRepository;
    }

    public boolean isHealthy() {
        try {
            ResponseEntity<String> response = restTemplate.getForEntity(
                    mlServiceUrl + "/health",
                    String.class
            );
            return response.getStatusCode() == HttpStatus.OK && isJson(response.getBody());
        } catch (Exception e) {
            log.warn("ML service health check failed: {}", e.getMessage());
            return false;
        }
    }

    public Map<String, Object> predictRace(Long raceId) {
        // Try full feature pipeline first
        try {
            log.info("Attempting full feature prediction for race {}", raceId);
            Map<String, Object> result = callMlServiceGet(mlServiceUrl + "/predict/race/" + raceId);
            if (result != null) {
                log.info("✓ Full feature prediction successful for race {}", raceId);
                return result;
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

    /**
     * Call ML service GET and parse JSON. If response is HTML or non-JSON, logs snippet and throws.
     * On 4xx/5xx returns null so caller can fall back to basic prediction.
     */
    private Map<String, Object> callMlServiceGet(String url) {
        HttpHeaders headers = new HttpHeaders();
        headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));
        HttpEntity<Void> request = new HttpEntity<>(headers);

        try {
            ResponseEntity<String> response = restTemplate.exchange(
                    url,
                    HttpMethod.GET,
                    request,
                    String.class
            );
            return parseMlResponse(url, response.getStatusCode(), response.getBody(), response.getHeaders().getContentType());
        } catch (HttpStatusCodeException e) {
            String snippet = e.getResponseBodyAsString();
            if (snippet != null && snippet.length() > SNIPPET_LEN) {
                snippet = snippet.substring(0, SNIPPET_LEN) + "...";
            }
            log.warn("ML GET {} failed: {} - body: {}", url, e.getStatusCode(), snippet);
            return null;
        }
    }

    private Map<String, Object> callMlServicePost(
            Long raceId,
            List<Map<String, Object>> runners
    ) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setAccept(Collections.singletonList(MediaType.APPLICATION_JSON));

            Map<String, Object> body = new HashMap<>();
            body.put("race_id", raceId);
            body.put("runners", runners);

            HttpEntity<Map<String, Object>> request = new HttpEntity<>(body, headers);

            ResponseEntity<String> response = restTemplate.exchange(
                    mlServiceUrl + "/predict/race",
                    HttpMethod.POST,
                    request,
                    String.class
            );

            Map<String, Object> result = parseMlResponse(
                    mlServiceUrl + "/predict/race",
                    response.getStatusCode(),
                    response.getBody(),
                    response.getHeaders().getContentType()
            );
            if (result == null) {
                throw new RuntimeException("ML service returned empty response");
            }
            result.put("note", "Basic prediction using morning line odds only");
            result.put("features", "basic");
            return result;

        } catch (HttpStatusCodeException e) {
            String snippet = e.getResponseBodyAsString();
            if (snippet != null && snippet.length() > SNIPPET_LEN) {
                snippet = snippet.substring(0, SNIPPET_LEN) + "...";
            }
            log.error("ML service call failed: {} {} - body: {}", e.getStatusCode(), e.getStatusText(), snippet);
            throw new RuntimeException("ML service unavailable: " + e.getStatusCode() + " " + e.getStatusText() + " (check ML_SERVICE_URL and that ml-service returns JSON)");
        } catch (Exception e) {
            log.error("ML service call failed: {}", e.getMessage());
            throw new RuntimeException("ML service unavailable: " + e.getMessage());
        }
    }

    private Map<String, Object> parseMlResponse(String url, HttpStatusCode status, String body, MediaType contentType) {
        if (body == null || body.isBlank()) {
            log.error("ML service returned null/empty body for {} (status={})", url, status);
            return null;
        }
        if (!isJson(body)) {
            String snippet = body.length() > SNIPPET_LEN ? body.substring(0, SNIPPET_LEN) + "..." : body;
            log.error("ML service returned non-JSON (content-type={}) for {}. Snippet: {}", contentType, url, snippet);
            throw new RuntimeException("ML service returned HTML or non-JSON (check ML_SERVICE_URL points to ml-service and service is running)");
        }
        try {
            return objectMapper.readValue(body, new TypeReference<Map<String, Object>>() {});
        } catch (Exception e) {
            log.error("Failed to parse ML response as JSON: {}", e.getMessage());
            throw new RuntimeException("ML service returned invalid JSON: " + e.getMessage());
        }
    }

    private static boolean isJson(String body) {
        return body != null && body.trim().startsWith("{");
    }
}