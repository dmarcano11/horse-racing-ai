package com.horseracing.api.dto;

import com.horseracing.api.entity.Track;
import lombok.Data;

@Data
public class TrackDto {
    private Long id;
    private String trackId;
    private String trackName;
    private String country;

    public static TrackDto from(Track track) {
        TrackDto dto = new TrackDto();
        dto.setId(track.getId());
        dto.setTrackId(track.getTrackId());
        dto.setTrackName(track.getTrackName());
        dto.setCountry(track.getCountry());
        return dto;
    }
}