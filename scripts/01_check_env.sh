#!/usr/bin/env bash
# Step 2：確認身分、列出可用的基礎模型 (FM) 與推論設定檔
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

echo "== 1. 目前使用的 IAM 身分 =="
aws sts get-caller-identity --output table

echo "== 2. 此區域可用的 Amazon 文字模型 (On-Demand) =="
aws bedrock list-foundation-models \
  --by-provider amazon \
  --by-output-modality TEXT \
  --query 'modelSummaries[].{id:modelId,name:modelName,input:join(`,`,inputModalities),inference:join(`,`,inferenceTypesSupported)}' \
  --output table

echo "== 3. 系統定義的跨區域推論設定檔 (前 20 筆) =="
aws bedrock list-inference-profiles \
  --type-equals SYSTEM_DEFINED \
  --query 'inferenceProfileSummaries[:20].{id:inferenceProfileId,name:inferenceProfileName,status:status}' \
  --output table

echo "== 4. 單一模型詳細資訊 =="
aws bedrock get-foundation-model --model-identifier amazon.nova-lite-v1:0 \
  --query 'modelDetails.{id:modelId,provider:providerName,input:inputModalities,output:outputModalities,customizations:customizationsSupported,streaming:responseStreamingSupported}'
