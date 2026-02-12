package com.horseracing.api.dto;

import com.horseracing.api.entity.Race;
import lombok.Data;

@Data
public class RaceDto {
    private Long id;
    private Integer raceNumber;
    private String raceName;
    private Integer distanceValue;
    private String distanceUnit;
    private String distanceDescription;
    private String surface;
    private String trackCondition;
    private String raceType;
    private String raceClass;
    private String grade;
    private Integer purse;
    private Integer minClaimPrice;
    private Integer maxClaimPrice;
    private Boolean hasResults;
    private Boolean hasFinished;
    // Meet info flattened
    private Long meetId;
    private String trackName;
    private String trackCode;

    public static RaceDto from(Race race) {
        RaceDto dto = new RaceDto();
        dto.setId(race.getId());
        dto.setRaceNumber(race.getRaceNumber());
        dto.setRaceName(race.getRaceName());
        dto.setDistanceValue(race.getDistanceValue());
        dto.setDistanceUnit(race.getDistanceUnit());
        dto.setDistanceDescription(race.getDistanceDescription());
        dto.setSurface(race.getSurface());
        dto.setTrackCondition(race.getTrackCondition());
        dto.setRaceType(race.getRaceType());
        dto.setRaceClass(race.getRaceClass());
        dto.setGrade(race.getGrade());
        dto.setPurse(race.getPurse());
        dto.setMinClaimPrice(race.getMinClaimPrice());
        dto.setMaxClaimPrice(race.getMaxClaimPrice());
        dto.setHasResults(race.getHasResults());
        dto.setHasFinished(race.getHasFinished());
        dto.setMeetId(race.getMeet().getId());
        dto.setTrackName(race.getMeet().getTrack().getTrackName());
        dto.setTrackCode(race.getMeet().getTrack().getTrackId());
        return dto;
    }
}