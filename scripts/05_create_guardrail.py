"""
Step 7：用 API 建立 Amazon Bedrock Guardrail（防護機制）並發布版本
涵蓋 AIF-C01 Domain 4 (Responsible AI) 常考的 5 種政策：
  1. Content filters      內容篩選（仇恨、侮辱、色情、暴力、不當行為、提示攻擊）
  2. Denied topics        拒絕的主題
  3. Word filters         單詞篩選 / 髒話清單
  4. Sensitive info (PII) 敏感資訊篩選（遮罩或封鎖）
  5. Contextual grounding 內容關聯依據檢查（降低幻覺，用於 RAG）

用法：python scripts/05_create_guardrail.py
輸出：guardrail_id 與 version，會寫入 .guardrail.env 供後續腳本使用
"""
import os

import boto3

REGION = os.getenv("AWS_REGION", "eu-central-1")
NAME = os.getenv("GUARDRAIL_NAME", "aif-c01-demo-guardrail")
bedrock = boto3.client("bedrock", region_name=REGION)

BLOCKED_MSG = "抱歉，這個問題違反了使用政策，無法回答。"

resp = bedrock.create_guardrail(
    name=NAME,
    description="AIF-C01 練習用：投資建議拒答 + PII 遮罩 + 內容篩選",
    blockedInputMessaging=BLOCKED_MSG,
    blockedOutputsMessaging=BLOCKED_MSG,
    # 1. 內容篩選：strength = NONE | LOW | MEDIUM | HIGH
    contentPolicyConfig={
        "filtersConfig": [
            {"type": "HATE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "INSULTS", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "SEXUAL", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "VIOLENCE", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            {"type": "MISCONDUCT", "inputStrength": "HIGH", "outputStrength": "HIGH"},
            # 提示攻擊（Jailbreak / Prompt Injection）只作用在輸入，output 必須是 NONE
            {"type": "PROMPT_ATTACK", "inputStrength": "HIGH", "outputStrength": "NONE"},
        ]
    },
    # 2. 拒絕的主題：用自然語言定義 + 範例
    topicPolicyConfig={
        "topicsConfig": [
            {
                "name": "InvestmentAdvice",
                "definition": "針對個股、基金、加密貨幣等金融商品提供買賣建議或報酬預測。",
                "examples": ["我應該買台積電股票嗎？", "推薦我明年會漲的基金", "比特幣現在可以進場嗎？"],
                "type": "DENY",
            }
        ]
    },
    # 3. 單詞篩選
    wordPolicyConfig={
        "wordsConfig": [{"text": "內線消息"}],
        "managedWordListsConfig": [{"type": "PROFANITY"}],
    },
    # 4. 敏感資訊：ANONYMIZE = 遮罩、BLOCK = 直接封鎖
    sensitiveInformationPolicyConfig={
        "piiEntitiesConfig": [
            {"type": "EMAIL", "action": "ANONYMIZE"},
            {"type": "PHONE", "action": "ANONYMIZE"},
            {"type": "CREDIT_DEBIT_CARD_NUMBER", "action": "BLOCK"},
        ],
        # 自訂 Regex：台灣身分證字號格式
        "regexesConfig": [
            {
                "name": "TW_National_ID",
                "description": "台灣身分證字號",
                "pattern": "[A-Z][12]\\d{8}",
                "action": "ANONYMIZE",
            }
        ],
    },
    # 5. Contextual grounding：分數低於門檻的回應會被擋下（RAG 場景）
    contextualGroundingPolicyConfig={
        "filtersConfig": [
            {"type": "GROUNDING", "threshold": 0.75},
            {"type": "RELEVANCE", "threshold": 0.5},
        ]
    },
)

gid = resp["guardrailId"]
print(f"Created guardrail: id={gid} arn={resp['guardrailArn']} (DRAFT)")

# DRAFT 版本可在 Console 測試；正式呼叫建議使用固定版本號
ver = bedrock.create_guardrail_version(guardrailIdentifier=gid, description="v1 for AIF-C01 lab")
version = ver["version"]
print(f"Published version: {version}")

with open(".guardrail.env", "w") as f:
    f.write(f"export GUARDRAIL_ID={gid}\nexport GUARDRAIL_VERSION={version}\n")
print("已寫入 .guardrail.env，執行 `source .guardrail.env` 後即可使用")
