package com.horseracing.api.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "runner_results", schema = "racing")
@Data
@NoArgsConstructor
public class RunnerResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "race_result_id", nullable = false)
    private RaceResult raceResult;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "runner_id", nullable = false)
    private Runner runner;

    @Column(name = "finish_position")
    private Integer finishPosition;

    @Column(name = "win_payoff")
    private Double winPayoff;

    @Column(name = "place_payoff")
    private Double placePayoff;

    @Column(name = "show_payoff")
    private Double showPayoff;
}