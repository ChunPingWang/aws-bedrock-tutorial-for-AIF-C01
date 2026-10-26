#!/usr/bin/env bash
# Step 10：啟用「模型調用日誌記錄」(Model invocation logging) 到 CloudWatch Logs
# AIF-C01 Domain 5（安全、合規、治理）常考：如何稽核/監控 FM 的請求與回應
set -euo pipefail
source "$(dirname "$0")/00_env.sh"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "== 1. 建立 CloudWatch Log Group =="
aws logs create-log-group --log-group-name "$LOG_GROUP" 2>/dev/null || echo "(已存在)"
aws logs put-retention-policy --log-group-name "$LOG_GROUP" --retention-in-days 7

echo "== 2. 建立讓 Bedrock 寫入 Logs 的 IAM Role =="
cat > /tmp/bedrock-trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "bedrock.amazonaws.com"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {"aws:SourceAccount": "${ACCOUNT_ID}"},
      "ArnLike": {"aws:SourceArn": "arn:aws:bedrock:${AWS_REGION}:${ACCOUNT_ID}:*"}
    }
  }]
}
EOF
cat > /tmp/bedrock-logs-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
    "Resource": "arn:aws:logs:${AWS_REGION}:${ACCOUNT_ID}:log-group:${LOG_GROUP}:log-stream:aws/bedrock/modelinvocations"
  }]
}
EOF
aws iam create-role --role-name "$LOG_ROLE_NAME" \
  --assume-role-policy-document file:///tmp/bedrock-trust.json >/dev/null 2>&1 || echo "(Role 已存在)"
aws iam put-role-policy --role-name "$LOG_ROLE_NAME" \
  --policy-name BedrockInvocationLogsWrite \
  --policy-document file:///tmp/bedrock-logs-policy.json
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${LOG_ROLE_NAME}"
echo "Role: $ROLE_ARN"
sleep 10  # 等 IAM 生效

echo "== 3. 設定 Bedrock 模型調用日誌（區域層級設定）=="
aws bedrock put-model-invocation-logging-configuration --logging-config "{
  \"cloudWatchConfig\": {\"logGroupName\": \"${LOG_GROUP}\", \"roleArn\": \"${ROLE_ARN}\"},
  \"textDataDeliveryEnabled\": true,
  \"imageDataDeliveryEnabled\": false,
  \"embeddingDataDeliveryEnabled\": false
}"
aws bedrock get-model-invocation-logging-configuration

echo "完成！再執行一次 scripts/02_converse_cli.sh，然後用下列指令查看日誌："
echo "aws logs tail \"$LOG_GROUP\" --since 10m --format short"
