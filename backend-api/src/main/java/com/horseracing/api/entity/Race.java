package com.horseracing.api.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "races", schema = "racing")
@Data
@NoArgsConstructor
public class Race {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "meet_id", nullable = false)
    private Meet meet;

    @Column(name = "race_number", nullable = false)
    private Integer raceNumber;

    @Column(name = "race_name")
    private String raceName;

    @Column(name = "distance_value")
    private Integer distanceValue;

    @Column(name = "distance_unit")
    private String distanceUnit;

    @Column(name = "distance_description")
    private String distanceDescription;

    @Column(name = "surface", columnDefinition = "varchar")
    private String surface;

    @Column(name = "track_condition")
    private String trackCondition;

    @Column(name = "race_type", columnDefinition = "varchar")
    private String raceType;

    @Column(name = "race_class")
    private String raceClass;

    @Column(name = "grade")
    private String grade;

    @Column(name = "age_restriction")
    private String ageRestriction;

    @Column(name = "sex_restriction")
    private String sexRestriction;

    @Column(name = "purse")
    private Integer purse;

    @Column(name = "min_claim_price")
    private Integer minClaimPrice;

    @Column(name = "max_claim_price")
    private Integer maxClaimPrice;

    @Column(name = "has_results")
    private Boolean hasResults;

    @Column(name = "has_finished")
    private Boolean hasFinished;

    @Column(name = "is_cancelled")
    private Boolean isCancelled;
}