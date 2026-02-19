#!/bin/bash
set -e

MODEL_DIR=models/llama3
ENGINE_OUT=build/engine

mkdir -p $ENGINE_OUT

echo "Build TRT-LLM engine..."
# TRT-LLM build command placeholder

tar -czf models.tar.gz $MODEL_DIR

echo "Upload to Artifactory"
curl -u user:token -T models.tar.gz https://artifactory.example.com/llm/models.tar.gz

echo "Upload to S3"
aws s3 cp models.tar.gz s3://mybucket/llm/models.tar.gz
