package com.horseracing.api.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "horses", schema = "racing")
@Data
@NoArgsConstructor
public class Horse {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", nullable = false)
    private String name;

    @Column(name = "registration_number")
    private String registrationNumber;

    @Column(name = "sire_name")
    private String sireName;

    @Column(name = "dam_name")
    private String damName;

    @Column(name = "dam_sire_name")
    private String damSireName;

    @Column(name = "breeder_name")
    private String breederName;

    @Column(name = "breed")
    private String breed;
}