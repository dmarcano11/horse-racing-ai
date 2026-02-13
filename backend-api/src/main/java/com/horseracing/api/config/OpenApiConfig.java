package com.horseracing.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("Horse Racing AI API")
                        .description("""
                    REST API for the Horse Racing AI prediction system.
                    
                    ## Features
                    - Race cards and entries for any date
                    - Historical race results
                    - ML-powered win probability predictions
                    - Track and meet information
                    
                    ## ML Model
                    - Random Forest classifier (0.604 ROC-AUC)
                    - 55 features per runner
                    - Trained on 1,300+ historical races
                    """)
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("David Marcano")
                                .email("dmarcano11@example.com"))
                        .license(new License()
                                .name("MIT License")))
                .servers(List.of(
                        new Server()
                                .url("http://localhost:8080")
                                .description("Local Development")
                ));
    }
}