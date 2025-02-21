# core-api/src/user/elo_service.py

import requests
import logging
from typing import Dict, Any
from flask import current_app
import os, re
from ollama import Client
from src.user.elo_context import ELO_SYSTEM_PROMPT

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Client configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://192.168.1.31:11434')
client = Client(host=OLLAMA_HOST, timeout=90)

print(f"Ollama Host: {OLLAMA_HOST}")

def calculate_elo(params: Dict[str, Any]) -> float:
    """
    Calculate the ELO score using the Ollama AI model.
    """
    # Basic data validation
    required_fields = ['last_month_miles', 'total_miles', 'age', 
                      'heart_rate_avg', 'braking_events', 'avg_speed',
                      'stress_level', 'sleep_quality']
    
    # Validate
    for field in required_fields:
        if field not in params or params[field] is None:
            raise ValueError(f"Missing required field: {field}")

    # Prompt construction structure
    system_prompt = ELO_SYSTEM_PROMPT

    user_prompt = f"""Rider data:
    - Last month miles: {params['last_month_miles']}
    - Total miles: {params['total_miles']}
    - Age: {params['age']}
    - Avg heart rate: {params['heart_rate_avg']} bpm
    - Hard braking events: {params['braking_events']}
    - Average speed: {params['avg_speed']} mph
    - Stress level: {params['stress_level']}/100
    - Sleep quality: {params['sleep_quality']}/10"""

    try:
        response = client.chat(
            model="llama3:latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            stream=False,
            options={
                    "temperature": 0.1,
                    # "num_predict": 128,
                    # "top_p": 0.9
            }
        )
        
        # Extract raw response
        raw = response['message']['content']
        print(f'raw_response = {raw}')
        # Find first float number in response
        numbers = re.findall(r"\d+\.\d+", raw)

        # Fallback to manual calculation
        manual_elo = calculate_fallback_elo(params)
        print(f'Manual ELO = {manual_elo}')

        # Convert first number to float
        try:
            ai_elo = float(numbers[0])
            ai_elo = max(0.0, min(100.0, ai_elo))  # Limit to 0-100
            print(f'AI ELO = {ai_elo}')
            return round(ai_elo, 1)
        except ValueError as e:
            logger.error(f"Error converting AI ELO to float: {str(e)}")
            return manual_elo

    except Exception as e:
        logger.error(f"AI Error: {str(e)}")
        manual_elo = calculate_fallback_elo(params)
        print(f'Fallback to manual ELO = {manual_elo}')
        return manual_elo

def calculate_fallback_elo(params: Dict[str, Any]) -> float:
    # Normalized factors
    factors = {
        'last_month': min(params['last_month_miles'] / 500, 1.0),
        'total': min(params['total_miles'] / 5000, 1.0),  # Ajustado a 5000
        'age': 1.0 if 25 <= params['age'] <= 45 else 0.8 if 18 <= params['age'] < 25 else 0.6 if params['age'] > 60 else 0.4,
        'heart': 1.0 if 60 <= params['heart_rate_avg'] <= 100 else 0.8 if 50 <= params['heart_rate_avg'] < 60 else 0.6 if 100 < params['heart_rate_avg'] <= 120 else 0.4,
        'brakes': max(1.0 - params['braking_events'] / 20, 0.0),  # Más tolerante
        'speed': 1.0 if 40 <= params['avg_speed'] <= 70 else 0.8 if 30 <= params['avg_speed'] < 40 else 0.6 if 70 < params['avg_speed'] <= 80 else 0.4,
        'stress': 1.0 if params['stress_level'] < 30 else 0.8 if params['stress_level'] <= 50 else 0.6 if params['stress_level'] <= 70 else 0.4,
        'sleep': 1.0 if params['sleep_quality'] >= 8 else 0.8 if 6 <= params['sleep_quality'] < 8 else 0.6 if 4 <= params['sleep_quality'] < 6 else 0.4
    }
    
    # Weights
    weights = {
        'last_month': 0.2,
        'total': 0.1,
        'age': 0.15,
        'heart': 0.15,
        'brakes': 0.15,
        'speed': 0.1,
        'stress': 0.05,
        'sleep': 0.05
    }
    
    # ELO calculation
    total = sum(factors[factor] * weights[factor] for factor in factors)
    
    # ELO range: 0-100
    return round(total * 100, 1)