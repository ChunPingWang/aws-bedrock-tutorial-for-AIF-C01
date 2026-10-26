#!/usr/bin/env bash
# Step 4：使用 AWS CLI 呼叫 Converse API（統一的對話 API，適用所有支援的模型）
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

PROMPT="${1:-請用三點說明 Amazon Bedrock 與 Amazon SageMaker AI 的差異（繁體中文，每點 30 字以內）}"

aws bedrock-runtime converse \
  --model-id "$MODEL_ID" \
  --system '[{"text":"你是 AWS 認證講師，回答要精簡、正確。"}]' \
  --messages "[{\"role\":\"user\",\"content\":[{\"text\":\"${PROMPT}\"}]}]" \
  --inference-config '{"maxTokens":512,"temperature":0.2,"topP":0.9}' \
  --query '{answer:output.message.content[0].text, stopReason:stopReason, usage:usage, latencyMs:metrics.latencyMs}'
