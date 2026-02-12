package com.horseracing.api.dto;

import com.horseracing.api.entity.RunnerResult;
import lombok.Data;

@Data
public class RunnerResultDto {
    private Long id;
    private Integer finishPosition;
    private Double winPayoff;
    private Double placePayoff;
    private Double showPayoff;
    // Runner info
    private Long runnerId;
    private String programNumber;
    private String horseName;
    private String jockeyName;
    private String trainerName;

    public static RunnerResultDto from(RunnerResult result) {
        RunnerResultDto dto = new RunnerResultDto();
        dto.setId(result.getId());
        dto.setFinishPosition(result.getFinishPosition());
        dto.setWinPayoff(result.getWinPayoff());
        dto.setPlacePayoff(result.getPlacePayoff());
        dto.setShowPayoff(result.getShowPayoff());

        if (result.getRunner() != null) {
            dto.setRunnerId(result.getRunner().getId());
            dto.setProgramNumber(result.getRunner().getProgramNumber());

            if (result.getRunner().getHorse() != null) {
                dto.setHorseName(result.getRunner().getHorse().getName());
            }
            if (result.getRunner().getJockey() != null) {
                dto.setJockeyName(result.getRunner().getJockey().getFullName());
            }
            if (result.getRunner().getTrainer() != null) {
                dto.setTrainerName(result.getRunner().getTrainer().getFullName());
            }
        }

        return dto;
    }
}