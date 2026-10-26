"""
Step 8：查詢 Knowledge Base（RAG）
  - retrieve           ：只做向量檢索，回傳相關片段與分數
  - retrieve_and_generate：檢索 + 交給 FM 生成答案，並附上引用來源 (citations)

前置：先依 README Step 8 在 Console 建立 Knowledge Base 並完成「同步」
用法：
    export KB_ID=XXXXXXXXXX
    python scripts/07_kb_rag.py "你的問題"
"""
import os
import sys

import boto3

REGION = os.getenv("AWS_REGION", "eu-central-1")
KB_ID = os.environ["KB_ID"]
# retrieve_and_generate 需要模型 ARN；跨區域推論設定檔使用 inference-profile ARN
ACCOUNT = boto3.client("sts").get_caller_identity()["Account"]
MODEL_ARN = os.getenv(
    "KB_MODEL_ARN",
    f"arn:aws:bedrock:{REGION}:{ACCOUNT}:inference-profile/eu.amazon.nova-lite-v1:0",
)

agent_rt = boto3.client("bedrock-agent-runtime", region_name=REGION)
question = sys.argv[1] if len(sys.argv) > 1 else "這份文件的重點是什麼？"

print("===== 1. Retrieve（只檢索）=====")
r = agent_rt.retrieve(
    knowledgeBaseId=KB_ID,
    retrievalQuery={"text": question},
    retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": 3}},
)
for i, item in enumerate(r["retrievalResults"], 1):
    uri = item.get("location", {}).get("s3Location", {}).get("uri", "-")
    print(f"#{i} score={item.get('score', 0):.3f} {uri}\n   {item['content']['text'][:120]}...")

print("\n===== 2. RetrieveAndGenerate（RAG）=====")
r = agent_rt.retrieve_and_generate(
    input={"text": question},
    retrieveAndGenerateConfiguration={
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {"knowledgeBaseId": KB_ID, "modelArn": MODEL_ARN},
    },
)
print(r["output"]["text"])
print("\n引用來源：")
for c in r.get("citations", []):
    for ref in c.get("retrievedReferences", []):
        print(" -", ref.get("location", {}).get("s3Location", {}).get("uri", "-"))
