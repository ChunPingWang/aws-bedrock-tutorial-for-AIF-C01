"""
Step 5：推論參數實驗 —— 觀察 temperature / topP / maxTokens / stopSequences 的影響
(AIF-C01 Domain 2/3 常考：「如何讓輸出更具確定性 / 更有創意」)

用法：python scripts/04_inference_params_lab.py
"""
import os

import boto3

REGION = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID = os.getenv("MODEL_ID", "eu.amazon.nova-lite-v1:0")
client = boto3.client("bedrock-runtime", region_name=REGION)

PROMPT = "幫一家台灣手搖飲店想一個品牌標語，只輸出標語本身。"

EXPERIMENTS = [
    ("低 temperature（確定性高）", {"temperature": 0.0, "topP": 0.9, "maxTokens": 60}),
    ("高 temperature（創意/多樣）", {"temperature": 1.0, "topP": 0.9, "maxTokens": 60}),
    ("低 topP（只從最可能的字詞取樣）", {"temperature": 0.7, "topP": 0.1, "maxTokens": 60}),
    ("maxTokens=10（輸出被截斷）", {"temperature": 0.7, "topP": 0.9, "maxTokens": 10}),
    ("stopSequences=['。']（遇到句號即停止）", {"temperature": 0.7, "topP": 0.9, "maxTokens": 60, "stopSequences": ["。"]}),
]


def ask(cfg: dict) -> tuple[str, str]:
    r = client.converse(
        modelId=MODEL_ID,
        messages=[{"role": "user", "content": [{"text": PROMPT}]}],
        inferenceConfig=cfg,
    )
    return r["output"]["message"]["content"][0]["text"].strip(), r["stopReason"]


for title, cfg in EXPERIMENTS:
    print(f"\n=== {title}  {cfg}")
    for i in range(3):  # 每組跑 3 次，觀察輸出是否穩定
        text, stop = ask(cfg)
        print(f"  #{i + 1} [{stop}] {text}")
