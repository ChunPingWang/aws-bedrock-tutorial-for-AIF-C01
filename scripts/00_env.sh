#!/usr/bin/env bash
# 共用環境變數：其他 .sh 腳本會 `source` 這個檔案
# 用法：source scripts/00_env.sh

# 本教學以法蘭克福區域為例（與截圖一致），可自行改成 us-east-1 / ap-northeast-1 等
export AWS_REGION="${AWS_REGION:-eu-central-1}"
export AWS_DEFAULT_REGION="$AWS_REGION"

# 跨區域推論設定檔 (Cross-Region Inference Profile)
#   eu.  => 在歐洲區域之間路由；us. => 美國；apac. => 亞太
# Amazon Nova 系列不需填寫 use-case 表單，最適合拿來練習
export MODEL_ID="${MODEL_ID:-eu.amazon.nova-lite-v1:0}"

# 練習用資源名稱（cleanup 會用到）
export GUARDRAIL_NAME="${GUARDRAIL_NAME:-aif-c01-demo-guardrail}"
export LOG_GROUP="${LOG_GROUP:-/aws/bedrock/aif-c01-invocation-logs}"
export LOG_ROLE_NAME="${LOG_ROLE_NAME:-AifC01BedrockInvocationLoggingRole}"

echo "AWS_REGION=$AWS_REGION"
echo "MODEL_ID=$MODEL_ID"
