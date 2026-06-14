# Reel Truth Checker ML Pipeline & Serving 🧠📊

This directory contains the machine learning modules, dataset pre-processing pipelines, RAG retriever, explainability frameworks, and the inference API server.

---

## 📂 ML Module Directory Structure

```directory
backend/ml/
├── evaluation/            # Scripts to compute model F1, accuracy, and latency
├── explainability/        # LIME & SHAP feature importance analyzers
├── models/                # Core neural net architectures:
│   ├── claim_extractor.py # Claim boundaries parsing (NER/LLM)
│   ├── claim_verifier.py  # Fact database alignment (RAG retriever)
│   ├── misinfo_classifier.py # Misinformation confidence score predictor
│   └── multimodal_fusion.py  # Concatenation of text, audio, and visual embeddings
├── rag/                   # Qdrant client, document indexing, and similarity retrieval
├── serving/               # FastAPI application code and Dockerfile (Port 8080)
└── requirements.txt       # ML-specific Python packages (PyTorch, Transformers, etc.)
```

---

## 🔬 ML Core Architectures

### 1. Claim Extractor
*   **Purpose**: Extracts distinct, factual assertions from raw video transcripts.
*   **Technique**: Named Entity Recognition (NER) and syntactic parsing (using transformer-based token classifiers) to isolate testable statements.

### 2. Claim Verifier (RAG & Qdrant)
*   **Purpose**: Connects extracted claims to verified reference sources.
*   **Technique**: Text chunks are embedded using `sentence-transformers` and queried against **Qdrant Vector DB** using cosine similarity. Retrieved facts are used to generate verification scores and citation links.

### 3. Misinformation Classifier & Multimodal Fusion
*   **Purpose**: Computes truth probability.
*   **Technique**: Merges text embeddings (from claim transcripts) and visual embeddings (from video frames) using a Multi-Head Attention Fusion network. A classification head then outputs a probability score representing trust/risk.

### 4. Explainable AI (XAI)
*   **Purpose**: Provides interpretability.
*   **Technique**: Leverages **LIME** (Local Interpretable Model-agnostic Explanations) and **SHAP** (SHapley Additive exPlanations) to trace back the output probability to specific words or video frames, showing a breakdown of positive/negative attributions.

---

## ⚙️ Requirements

The ML module runs on Python 3.10 to ensure wide compatibility with ML toolkits (e.g. SHAP, PyTorch, Sentence-Transformers).

### Dependencies
Installed via `requirements.txt`:
*   `torch` & `transformers` & `accelerate` (Deep Learning frameworks)
*   `sentence-transformers` (Dense vector embeddings)
*   `qdrant-client` (Vector DB client)
*   `shap` & `lime` (Explainable AI)
*   `scikit-learn` & `pandas` & `numpy` (Evaluation & manipulation)
*   `opencv-python-headless` & `pillow` (Video frame extraction)
*   `fastapi` & `uvicorn` (Serving engine)

---

## 🛠️ Run Serving API Locally

### 1. Setup Virtual Environment
```bash
cd backend/ml
python -m venv venv-ml
source venv-ml/bin/activate  # On Windows: .\venv-ml\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Qdrant Vector DB
Launch a local Qdrant instance via Docker:
```bash
docker run -d -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant:latest
```

### 3. Start Inference Engine
With environment variables configured (`QDRANT_HOST` and `QDRANT_PORT`):
```bash
# Add current directory to pythonpath
export PYTHONPATH=$PYTHONPATH:$(pwd)/../..   # Linux/macOS
# On Windows (Powershell):
$env:PYTHONPATH = "E:\Reel Truth Checker"

uvicorn backend.ml.serving.app:app --host 127.0.0.1 --port 8080 --reload
```
View the endpoint documentation at [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs).


---

## 🧪 Evaluation

Run model evaluation against the test split:
```bash
python -m backend.ml.evaluation.evaluate_models
```
