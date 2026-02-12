package com.horseracing.api.dto;

import com.horseracing.api.entity.Meet;
import lombok.Data;
import java.time.LocalDate;

@Data
public class MeetDto {
    private Long id;
    private String meetId;
    private LocalDate date;
    private String trackName;
    private String trackCode;

    public static MeetDto from(Meet meet) {
        MeetDto dto = new MeetDto();
        dto.setId(meet.getId());
        dto.setMeetId(meet.getMeetId());
        dto.setDate(meet.getDate());
        dto.setTrackName(meet.getTrack().getTrackName());
        dto.setTrackCode(meet.getTrack().getTrackId());
        return dto;
    }
}