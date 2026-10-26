# AIF-C01 Amazon Bedrock 重點筆記（Knowledge Base 練習用文件）

## Bedrock 是什麼
Amazon Bedrock 是全受管、無伺服器的生成式 AI 服務，透過單一 API 存取多家供應商的基礎模型（Amazon Nova、Anthropic Claude、Meta Llama、Mistral 等）。
使用者的提示與回應不會被用來訓練基礎模型，也不會分享給模型供應商。

## 客製化方法（成本由低到高）
1. 提示工程（Prompt Engineering）：零樣本、少樣本、思維鏈（Chain-of-Thought）。不改變模型權重。
2. RAG（檢索增強生成）：用 Knowledge Base 把企業資料轉成向量，查詢時檢索相關片段再交給模型。不改變模型權重，資料可即時更新。
3. 微調（Fine-tuning）：使用「已標註」的提示/回應配對資料調整模型權重。
4. 持續預訓練（Continued Pre-training）：使用「未標註」的領域資料調整模型權重。

## 計價模式
- On-Demand：依輸入/輸出 Token 計費，適合變動或不可預期的流量。
- Batch：非即時大量處理，支援的模型通常比 On-Demand 便宜（官方標示約 50% 折扣，依模型而異）。
- Provisioned Throughput：購買 Model Unit，保證吞吐量；自訂（微調）模型推論必須使用。

## Guardrails
可設定內容篩選、拒絕的主題、單詞篩選、敏感資訊（PII）遮罩、內容關聯依據檢查（降低幻覺）、自動推理檢查。
