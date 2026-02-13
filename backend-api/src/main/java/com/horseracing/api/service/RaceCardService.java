package com.horseracing.api.service;

import com.horseracing.api.dto.RaceCardDto;
import com.horseracing.api.dto.RaceDto;
import com.horseracing.api.entity.Runner;
import com.horseracing.api.entity.RunnerResult;
import com.horseracing.api.repository.RaceRepository;
import com.horseracing.api.repository.RunnerRepository;
import com.horseracing.api.repository.RunnerResultRepository;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import java.util.*;

@Service
@Slf4j
public class RaceCardService {

    private final RaceRepository raceRepository;
    private final RunnerRepository runnerRepository;
    private final RunnerResultRepository runnerResultRepository;
    private final PredictionService predictionService;

    public RaceCardService(
            RaceRepository raceRepository,
            RunnerRepository runnerRepository,
            RunnerResultRepository runnerResultRepository,
            PredictionService predictionService
    ) {
        this.raceRepository = raceRepository;
        this.runnerRepository = runnerRepository;
        this.runnerResultRepository = runnerResultRepository;
        this.predictionService = predictionService;
    }

    public RaceCardDto getRaceCard(Long raceId, boolean includePredictions) {
        // Get race
        var race = raceRepository.findById(raceId)
                .orElseThrow(() -> new RuntimeException("Race not found: " + raceId));

        // Get runners
        List<Runner> runners = runnerRepository.findActiveRunnersByRaceId(raceId);

        // Get results if available
        Map<Long, RunnerResult> resultsByRunnerId = new HashMap<>();
        if (Boolean.TRUE.equals(race.getHasResults())) {
            runnerResultRepository.findByRaceIdOrderByPosition(raceId)
                    .forEach(rr -> resultsByRunnerId.put(rr.getRunner().getId(), rr));
        }

        // Get predictions if requested
        Map<Long, Map<String, Object>> predictionsByRunnerId = new HashMap<>();
        boolean predictionsAvailable = false;

        if (includePredictions) {
            try {
                Map<String, Object> predictionResponse =
                        predictionService.predictRace(raceId);

                List<Map<String, Object>> predictions =
                        (List<Map<String, Object>>) predictionResponse.get("predictions");

                if (predictions != null) {
                    predictions.forEach(p -> {
                        Long runnerId = ((Number) p.get("runner_id")).longValue();
                        predictionsByRunnerId.put(runnerId, p);
                    });
                    predictionsAvailable = true;
                }
            } catch (Exception e) {
                log.warn("Could not get predictions for race {}: {}", raceId, e.getMessage());
            }
        }

        // Build race card runners
        List<RaceCardDto.RaceCardRunnerDto> cardRunners = new ArrayList<>();
        for (Runner runner : runners) {
            RaceCardDto.RaceCardRunnerDto cardRunner = buildCardRunner(
                    runner,
                    predictionsByRunnerId.get(runner.getId()),
                    resultsByRunnerId.get(runner.getId())
            );
            cardRunners.add(cardRunner);
        }

        // Sort by model rank if predictions available, otherwise by post position
        if (predictionsAvailable) {
            cardRunners.sort(Comparator.comparingInt(r ->
                    r.getModelRank() != null ? r.getModelRank() : 99));
        }

        // Build response
        RaceCardDto raceCard = new RaceCardDto();
        raceCard.setRace(RaceDto.from(race));
        raceCard.setRunners(cardRunners);
        raceCard.setHasResults(!resultsByRunnerId.isEmpty());
        raceCard.setPredictionsAvailable(predictionsAvailable);

        return raceCard;
    }

    private RaceCardDto.RaceCardRunnerDto buildCardRunner(
            Runner runner,
            Map<String, Object> prediction,
            RunnerResult result
    ) {
        RaceCardDto.RaceCardRunnerDto dto = new RaceCardDto.RaceCardRunnerDto();

        // Runner basics
        dto.setRunnerId(runner.getId());
        dto.setProgramNumber(runner.getProgramNumber());
        dto.setPostPosition(runner.getPostPosition());
        dto.setMorningLineOdds(runner.getMorningLineOdds());
        dto.setMorningLineDecimal(runner.getMorningLineDecimal());
        dto.setWeight(runner.getWeight());
        dto.setIsScratched(runner.getIsScratched());

        // Horse, jockey, trainer
        if (runner.getHorse() != null) {
            dto.setHorseName(runner.getHorse().getName());
        }
        if (runner.getJockey() != null) {
            dto.setJockeyName(runner.getJockey().getFullName());
        }
        if (runner.getTrainer() != null) {
            dto.setTrainerName(runner.getTrainer().getFullName());
        }

        // Predictions
        if (prediction != null) {
            dto.setWinProbability(
                    ((Number) prediction.get("win_probability")).doubleValue());
            dto.setWinProbabilityNormalized(
                    ((Number) prediction.get("win_probability_normalized")).doubleValue());
            dto.setImpliedOdds(
                    ((Number) prediction.get("implied_odds")).doubleValue());
            dto.setModelRank(
                    ((Number) prediction.get("model_rank")).intValue());
            dto.setUsingRealFeatures(
                    (Boolean) prediction.getOrDefault("using_real_features", false));
        }

        // Results
        if (result != null) {
            dto.setFinishPosition(result.getFinishPosition());
            dto.setWinPayoff(result.getWinPayoff());
            dto.setPlacePayoff(result.getPlacePayoff());
            dto.setShowPayoff(result.getShowPayoff());
        }

        return dto;
    }
}