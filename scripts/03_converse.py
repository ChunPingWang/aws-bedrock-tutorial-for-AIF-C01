"""
Step 4：使用 boto3 呼叫 Converse API 與 ConverseStream（串流）
用法：
    python scripts/03_converse.py "你的問題"
    python scripts/03_converse.py --stream "你的問題"
"""
import argparse
import os

import boto3

REGION = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID = os.getenv("MODEL_ID", "eu.amazon.nova-lite-v1:0")

client = boto3.client("bedrock-runtime", region_name=REGION)

SYSTEM = [{"text": "你是 AWS 認證講師，用繁體中文回答，精簡且正確。"}]
INFERENCE_CONFIG = {"maxTokens": 512, "temperature": 0.3, "topP": 0.9}


def converse(prompt: str) -> None:
    resp = client.converse(
        modelId=MODEL_ID,
        system=SYSTEM,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig=INFERENCE_CONFIG,
    )
    print(resp["output"]["message"]["content"][0]["text"])
    u = resp["usage"]
    print(
        f"\n[stopReason={resp['stopReason']}] "
        f"input={u['inputTokens']} output={u['outputTokens']} tokens, "
        f"latency={resp['metrics']['latencyMs']} ms"
    )


def converse_stream(prompt: str) -> None:
    resp = client.converse_stream(
        modelId=MODEL_ID,
        system=SYSTEM,
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig=INFERENCE_CONFIG,
    )
    for event in resp["stream"]:
        if "contentBlockDelta" in event:
            print(event["contentBlockDelta"]["delta"].get("text", ""), end="", flush=True)
        elif "metadata" in event:
            u = event["metadata"]["usage"]
            print(f"\n\n[input={u['inputTokens']} output={u['outputTokens']} tokens]")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("prompt", nargs="?", default="什麼是 Foundation Model？請用 3 句話說明。")
    p.add_argument("--stream", action="store_true")
    a = p.parse_args()
    (converse_stream if a.stream else converse)(a.prompt)
