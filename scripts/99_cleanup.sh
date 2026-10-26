#!/usr/bin/env bash
# Step 13：清除練習資源，避免持續計費
# 注意：Knowledge Base 的向量存放區（例如 OpenSearch Serverless）會持續計費，務必刪除！
set -uo pipefail
source "$(dirname "$0")/00_env.sh"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "== 1. 刪除 Guardrail =="
GID=$(aws bedrock list-guardrails --query "guardrails[?name=='${GUARDRAIL_NAME}'].id | [0]" --output text)
if [[ "$GID" != "None" && -n "$GID" ]]; then
  aws bedrock delete-guardrail --guardrail-identifier "$GID" && echo "deleted $GID"
fi
rm -f .guardrail.env

echo "== 2. 關閉模型調用日誌並刪除 Log Group / IAM Role =="
aws bedrock delete-model-invocation-logging-configuration || true
aws logs delete-log-group --log-group-name "$LOG_GROUP" 2>/dev/null || true
aws iam delete-role-policy --role-name "$LOG_ROLE_NAME" --policy-name BedrockInvocationLogsWrite 2>/dev/null || true
aws iam delete-role --role-name "$LOG_ROLE_NAME" 2>/dev/null || true

echo "== 3. Knowledge Base（若有設定 KB_ID）=="
if [[ -n "${KB_ID:-}" ]]; then
  aws bedrock-agent delete-knowledge-base --knowledge-base-id "$KB_ID" && echo "deleted KB $KB_ID"
  echo "請到 OpenSearch Serverless / S3 Vectors 主控台確認向量集合已刪除"
fi

echo "== 4. 檢查是否仍有佈建輸送量（按小時計費）=="
aws bedrock list-provisioned-model-throughputs --query 'provisionedModelSummaries[].{name:provisionedModelName,status:status}' --output table

echo "清除完成（account ${ACCOUNT_ID}, region ${AWS_REGION}）"
