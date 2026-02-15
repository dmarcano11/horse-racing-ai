"""Flask ML microservice for horse racing predictions"""
import logging
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add data-ingestion to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'data-ingestion'))

from predictor import predictor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from Spring Boot


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify(predictor.health_check())


@app.route('/predict/race', methods=['POST'])
def predict_race():
    """
    Predict win probabilities for all runners in a race.

    Request body:
    {
        "race_id": 123,
        "runners": [
            {
                "runner_id": 456,
                "jockey_win_rate": 0.15,
                "trainer_win_rate": 0.12,
                "horse_win_rate": 0.10,
                "ml_odds_decimal": 5.0,
                "post_position": 3,
                "field_size": 8,
                ... (all feature columns)
            },
            ...
        ]
    }

    Response:
    {
        "race_id": 123,
        "predictions": [
            {
                "runner_id": 456,
                "win_probability": 0.2341,
                "win_probability_normalized": 0.1823,
                "implied_odds": 3.27,
                "model_rank": 1
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        race_id = data.get('race_id')
        runners = data.get('runners', [])

        if not runners:
            return jsonify({'error': 'No runners provided'}), 400

        logger.info(f"Predicting race {race_id} with {len(runners)} runners")

        # Generate predictions
        predictions = predictor.predict_race(runners)

        return jsonify({
            'race_id': race_id,
            'runner_count': len(runners),
            'predictions': predictions
        })

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/predict/race/<int:race_id>', methods=['GET'])
def predict_race_from_db(race_id):
    """
    Generate predictions using full feature engineering pipeline.
    Fetches runner data directly from PostgreSQL.

    This is the preferred endpoint - uses real ML features!
    """
    try:
        logger.info(f"Generating full-feature predictions for race {race_id}")
        predictions = predictor.predict_race_from_db(race_id)

        if not predictions:
            return jsonify({
                'race_id': race_id,
                'error': 'No runners found or features could not be built'
            }), 404

        return jsonify({
            'race_id': race_id,
            'runner_count': len(predictions),
            'predictions': predictions,
            'model': 'RandomForest',
            'features': 'full_pipeline',
            'note': 'Predictions using complete 55-feature ML pipeline'
        })

    except Exception as e:
        logger.error(f"Full prediction failed for race {race_id}: {e}")
        return jsonify({
            'race_id': race_id,
            'error': str(e),
            'suggestion': 'Try POST /predict/race for basic predictions'
        }), 500


@app.route('/predict/runner/<int:runner_id>', methods=['GET'])
def predict_runner(runner_id):
    """
    Get prediction for a single runner.
    Returns win probability and model rank within race.
    """
    # This would require fetching features from DB
    # For now return a placeholder
    return jsonify({
        'runner_id': runner_id,
        'message': 'Use /predict/race for full race predictions'
    })

@app.route('/debug', methods=['GET'])
def debug():
    """Debug endpoint to check paths."""
    from pathlib import Path
    import os

    data_ingestion_exists = Path('/data-ingestion').exists()
    model_exists = Path('/data-ingestion/models/tuned/random_forest_tuned.pkl').exists()
    src_exists = Path('/data-ingestion/src').exists()

    return jsonify({
        'data_ingestion_dir': data_ingestion_exists,
        'model_file': model_exists,
        'src_dir': src_exists,
        'data_ingestion_contents': os.listdir('/data-ingestion') if data_ingestion_exists else [],
        'cwd': os.getcwd(),
        'app_contents': os.listdir('/app')
    })

@app.route('/debug/load', methods=['POST'])
def debug_load():
    """Try to load model and report exact error."""
    from pathlib import Path
    import pickle
    import traceback

    try:
        model_path = Path('/data-ingestion/models/tuned/random_forest_tuned.pkl')
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return jsonify({'status': 'success', 'model_type': str(type(model))})
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        })


if __name__ == '__main__':
    logger.info("Starting Horse Racing ML Service...")

    # Load model
    try:
        predictor.load()
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        logger.warning("Service starting without model - predictions will fail")

    # Start server
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )