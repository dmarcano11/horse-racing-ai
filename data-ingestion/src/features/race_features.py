"""Race context feature calculator."""
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.db.models import Race, Runner, Meet
from src.features.base import FeatureCalculator


class RaceFeatureCalculator(FeatureCalculator):
    """Calculate race context features."""

    def calculate_race_features(
            self,
            race: Race,
            runner: Runner
    ) -> Dict[str, float]:
        """
        Calculate race context features.

        Args:
            race: Race object
            runner: Runner object

        Returns:
            Dictionary of features
        """
        features = {}

        # Distance features
        features['race_distance'] = float(race.distance_value or 0)
        features['race_distance_furlongs'] = self._convert_to_furlongs(
            race.distance_value,
            race.distance_unit
        )

        # Surface features (one-hot encoding)
        surface = race.surface.value if race.surface else 'Unknown'
        features['surface_dirt'] = 1.0 if surface == 'Dirt' else 0.0
        features['surface_turf'] = 1.0 if surface == 'Turf' else 0.0
        features['surface_synthetic'] = 1.0 if surface == 'Synthetic' else 0.0

        # Race type features (one-hot encoding)
        race_type = race.race_type.value if race.race_type else 'Unknown'
        features['race_type_maiden'] = 1.0 if race_type == 'Maiden' else 0.0
        features['race_type_claiming'] = 1.0 if race_type == 'Claiming' else 0.0
        features['race_type_allowance'] = 1.0 if race_type == 'Allowance' else 0.0
        features['race_type_stakes'] = 1.0 if race_type == 'Stakes' else 0.0

        # Class indicators
        features['race_purse'] = float(race.purse or 0)
        features['race_min_claim_price'] = float(race.min_claim_price or 0)
        features['race_max_claim_price'] = float(race.max_claim_price or 0)

        # Stakes grade
        features['is_graded_stakes'] = 1.0 if race.grade and race.grade.startswith('G') else 0.0

        # Field size
        field_size = self.db.query(Runner).filter(
            Runner.race_id == race.id,
            Runner.is_scratched == False
        ).count()
        features['field_size'] = float(field_size)

        # Post position
        try:
            post_pos = int(runner.post_position) if runner.post_position else 0
        except ValueError:
            post_pos = 0
        features['post_position'] = float(post_pos)

        # Normalize post position by field size
        if field_size > 0:
            features['post_position_normalized'] = post_pos / field_size
        else:
            features['post_position_normalized'] = 0.0

        # Weight carried
        features['weight_carried'] = float(runner.weight or 120)

        return features

    def _convert_to_furlongs(
            self,
            distance_value: Optional[int],
            distance_unit: Optional[str]
    ) -> float:
        """
        Convert distance to furlongs.

        Args:
            distance_value: Distance value
            distance_unit: Distance unit

        Returns:
            Distance in furlongs
        """
        if not distance_value:
            return 0.0

        if not distance_unit:
            return float(distance_value)

        unit_lower = distance_unit.lower()

        # Convert to furlongs
        if 'furlong' in unit_lower or unit_lower == 'f':
            return float(distance_value)
        elif 'mile' in unit_lower or unit_lower == 'm':
            return float(distance_value) * 8  # 1 mile = 8 furlongs
        elif 'yard' in unit_lower or unit_lower == 'y':
            return float(distance_value) / 220  # 1 furlong = 220 yards
        elif 'meter' in unit_lower:
            return float(distance_value) / 201.168  # 1 furlong ≈ 201.168 meters
        else:
            return float(distance_value)