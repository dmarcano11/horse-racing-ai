package com.horseracing.api.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "jockeys", schema = "racing")
@Data
@NoArgsConstructor
public class Jockey {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "api_id")
    private String apiId;

    @Column(name = "first_name")
    private String firstName;

    @Column(name = "last_name", nullable = false)
    private String lastName;

    @Column(name = "middle_name")
    private String middleName;

    public String getFullName() {
        if (firstName != null && !firstName.isBlank()) {
            return firstName + " " + lastName;
        }
        return lastName;
    }
}