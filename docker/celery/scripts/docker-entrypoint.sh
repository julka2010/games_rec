#! /usr/bin/env sh

celery worker -A game_recommendations -Q gpu-bound --concurrency=1 --loglevel=INFO
celery worker -A game_recommendations -Q celery --loglevel=INFO
