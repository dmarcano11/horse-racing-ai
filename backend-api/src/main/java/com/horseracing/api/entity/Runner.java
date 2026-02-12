package com.horseracing.api.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "runners", schema = "racing")
@Data
@NoArgsConstructor
public class Runner {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "race_id", nullable = false)
    private Race race;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "horse_id", nullable = false)
    private Horse horse;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "jockey_id")
    private Jockey jockey;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "trainer_id")
    private Trainer trainer;

    @Column(name = "program_number")
    private String programNumber;

    @Column(name = "post_position")
    private String postPosition;

    @Column(name = "morning_line_odds")
    private String morningLineOdds;

    @Column(name = "morning_line_decimal")
    private Double morningLineDecimal;

    @Column(name = "live_odds")
    private String liveOdds;

    @Column(name = "live_odds_decimal")
    private Double liveOddsDecimal;

    @Column(name = "weight")
    private Integer weight;

    @Column(name = "claiming_price")
    private Integer claimingPrice;

    @Column(name = "equipment")
    private String equipment;

    @Column(name = "medication")
    private String medication;

    @Column(name = "is_scratched")
    private Boolean isScratched;

    @Column(name = "scratch_indicator")
    private String scratchIndicator;
}