package com.horseracing.api.dto;

import lombok.Data;
import java.util.List;

@Data
public class RaceCardDto {

    private RaceDto race;
    private List<RaceCardRunnerDto> runners;
    private boolean hasResults;
    private boolean predictionsAvailable;

    @Data
    public static class RaceCardRunnerDto {
        // Runner info
        private Long runnerId;
        private String programNumber;
        private String postPosition;
        private String morningLineOdds;
        private Double morningLineDecimal;
        private Integer weight;
        private Boolean isScratched;

        // Horse
        private String horseName;

        // Jockey
        private String jockeyName;

        // Trainer
        private String trainerName;

        // ML Prediction
        private Double winProbability;
        private Double winProbabilityNormalized;
        private Double impliedOdds;
        private Integer modelRank;
        private Boolean usingRealFeatures;

        // Result (if race is finished)
        private Integer finishPosition;
        private Double winPayoff;
        private Double placePayoff;
        private Double showPayoff;
    }
}