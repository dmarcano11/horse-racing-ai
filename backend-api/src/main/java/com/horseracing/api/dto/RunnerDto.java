package com.horseracing.api.dto;

import com.horseracing.api.entity.Runner;
import lombok.Data;

@Data
public class RunnerDto {
    private Long id;
    private String programNumber;
    private String postPosition;
    private String morningLineOdds;
    private Double morningLineDecimal;
    private Integer weight;
    private Boolean isScratched;
    // Horse info
    private Long horseId;
    private String horseName;
    // Jockey info
    private Long jockeyId;
    private String jockeyName;
    // Trainer info
    private Long trainerId;
    private String trainerName;

    public static RunnerDto from(Runner runner) {
        RunnerDto dto = new RunnerDto();
        dto.setId(runner.getId());
        dto.setProgramNumber(runner.getProgramNumber());
        dto.setPostPosition(runner.getPostPosition());
        dto.setMorningLineOdds(runner.getMorningLineOdds());
        dto.setMorningLineDecimal(runner.getMorningLineDecimal());
        dto.setWeight(runner.getWeight());
        dto.setIsScratched(runner.getIsScratched());

        if (runner.getHorse() != null) {
            dto.setHorseId(runner.getHorse().getId());
            dto.setHorseName(runner.getHorse().getName());
        }

        if (runner.getJockey() != null) {
            dto.setJockeyId(runner.getJockey().getId());
            dto.setJockeyName(runner.getJockey().getFullName());
        }

        if (runner.getTrainer() != null) {
            dto.setTrainerId(runner.getTrainer().getId());
            dto.setTrainerName(runner.getTrainer().getFullName());
        }

        return dto;
    }
}