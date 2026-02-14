package com.horseracing.api.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;
import lombok.extern.slf4j.Slf4j;
import java.util.Map;

@RestController
@RequestMapping("/api/chat")
@CrossOrigin(origins = "*")
@Slf4j
@Tag(name = "Chat", description = "AI racing expert chat powered by RAG + LLM")
public class ChatController {

    private final RestTemplate restTemplate;
    private static final String MCP_SERVICE_URL = "http://localhost:5002";

    public ChatController() {
        this.restTemplate = new RestTemplate();
    }

    @PostMapping
    @Operation(
            summary = "Chat with AI racing expert",
            description = "Send a message to the AI racing expert. Optionally provide race_id for race-specific analysis."
    )
    public ResponseEntity<Map> chat(@RequestBody Map<String, Object> request) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);

            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(request, headers);

            ResponseEntity<Map> response = restTemplate.postForEntity(
                    MCP_SERVICE_URL + "/chat",
                    entity,
                    Map.class
            );

            return ResponseEntity.ok(response.getBody());

        } catch (Exception e) {
            log.error("Chat error: {}", e.getMessage());
            return ResponseEntity.internalServerError().body(Map.of(
                    "error", "Chat service unavailable: " + e.getMessage()
            ));
        }
    }

    @GetMapping("/health")
    @Operation(summary = "Check MCP chat service health")
    public ResponseEntity<Map> health() {
        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(
                    MCP_SERVICE_URL + "/health",
                    Map.class
            );
            return ResponseEntity.ok(response.getBody());
        } catch (Exception e) {
            return ResponseEntity.ok(Map.of(
                    "status", "unavailable",
                    "error", e.getMessage()
            ));
        }
    }
}