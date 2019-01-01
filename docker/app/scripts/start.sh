#!/bin/bash

echo Starting Gunicorn
exec gunicorn game_recommendations.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${N_GUNICORN_WORKERS} \
