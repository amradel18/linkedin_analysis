# Project Portfolio Summary

## Category Checklist
- [x] NLP / LLM
- [x] Retrieval-Augmented Generation (RAG)
- [x] Machine Learning
- [x] Deep Learning
- [x] Time Series Forecasting
- [x] MLOps / Deployment
- [x] Data Engineering / ETL
- [x] BI / Dashboarding
- [x] Optimization / Operations Research
- [x] Real-time Systems
- [x] Voice AI
- [x] CRM Analytics

## Janssen AI Agent
- **Categories:** NLP/LLM, RAG, Voice AI, Real-time Systems, MLOps/Deployment
- **Project Goal:** Build a multimodal intelligent customer-support agent for Janssen products that answers accurately within a controlled domain.
- **Implementation Details:** Built API services with FastAPI, integrated GPT-4o for response generation and Whisper for speech understanding, implemented retrieval with Qdrant for context grounding, enforced strict response governance, logged interactions in MySQL, and containerized deployment with Docker.
- **Tech Stack:** Python, FastAPI, OpenAI GPT-4o, Whisper-1, Qdrant, MySQL, Docker.

## C&S Data Pipeline
- **Categories:** Data Engineering/ETL, BI/Dashboarding
- **Project Goal:** Convert raw CRM operational data into reliable analytical tables ready for reporting.
- **Implementation Details:** Developed separate data pipelines for calls, customers, orders, and tickets, normalized nested JSON structures, generated stable IDs, cleaned fields, standardized date logic, and delivered final outputs to Excel with reference tables.
- **Tech Stack:** Python, pandas, Jupyter, Excel, JSON.

## Executive Proposal Automation System
- **Categories:** NLP/LLM, Automation, BI/Dashboarding
- **Project Goal:** Transform unstructured client requirement PDFs into executive-ready proposal decks and structured JSON outputs.
- **Implementation Details:** Extracted and structured PDF content using a MECE consulting framework, generated schema-constrained JSON, validated output with Pydantic, produced PowerPoint decks through MCP PowerPoint only, and exposed workflow via Streamlit.
- **Tech Stack:** Python, Streamlit, pdfplumber/PyPDF2, Pydantic, Ollama (gpt-oss:120b), MCP PowerPoint Server.

## Ecommerce Shipping Analysis & Delivery Time Prediction
- **Categories:** Machine Learning, BI/Dashboarding, Data Engineering/ETL
- **Project Goal:** Analyze e-commerce shipping operations, identify delay drivers, and prepare predictive delivery-time models.
- **Implementation Details:** Loaded and merged multiple CSV tables, ran quality checks and duplicate validation, performed comprehensive EDA, engineered operational features, and prepared training datasets for delivery-time prediction.
- **Tech Stack:** Python, pandas, seaborn, matplotlib, scikit-learn, Jupyter.

## Healthcare Analytics
- **Categories:** BI/Dashboarding, Machine Learning, NLP/LLM
- **Project Goal:** Build a professional healthcare analytics platform for risk exploration with AI-assisted reporting.
- **Implementation Details:** Designed modular data and visualization architecture, built Streamlit analysis pages, implemented clustering and anomaly detection pipelines, and integrated Ollama for concise analytical reporting with Arabic support.
- **Tech Stack:** Python, Streamlit, NiceGUI, Plotly, pandas, Ollama.

## Insurance Customer Data Analysis
- **Categories:** Machine Learning, BI/Dashboarding
- **Project Goal:** Understand insurance customer behavior, estimate customer lifetime value, and improve campaign effectiveness.
- **Implementation Details:** Executed end-to-end EDA, derived business-focused features, prepared datasets for classification/regression/clustering tasks, and linked outputs to practical business KPIs.
- **Tech Stack:** Python, pandas, numpy, matplotlib, seaborn, scikit-learn, Jupyter.

## JANSSEN CRM
- **Categories:** CRM Analytics, BI/Dashboarding, Data Engineering/ETL
- **Project Goal:** Build an analytics-first CRM platform to unify customer data and improve service performance.
- **Implementation Details:** Implemented specialized pages for data operations, customer/call/ticket analytics, SLA and performance tracking, and integrated Google Drive API for storage and synchronization.
- **Tech Stack:** Python, Streamlit, pandas, plotly, SQLAlchemy, Google Drive API.

## Truck Management System (Logistics)
- **Categories:** Optimization/Operations Research, Machine Learning, BI/Dashboarding
- **Project Goal:** Optimize fleet allocation and routing decisions with real-time operational analytics.
- **Implementation Details:** Validated logistics data quality, applied K-means for geographic clustering, used OR-Tools and packing logic for assignment and route planning, and built a unified monitoring dashboard.
- **Tech Stack:** Python, Streamlit, OR-Tools, pandas, scikit-learn, plotly, geopy.

## Economic News & Gold Price Prediction
- **Categories:** NLP/LLM, Time Series Forecasting, Deep Learning, Machine Learning
- **Project Goal:** Predict gold-price direction by combining economic news signals with commodity and energy context.
- **Implementation Details:** Collected and vectorized news text, trained ARIMA/Prophet/LSTM models, implemented PyTorch deep-learning pipelines, clustered market regimes, and generated automated analytical summaries using Ollama.
- **Tech Stack:** Python, NLP pipelines, PyTorch, ARIMA/Prophet/LSTM, Ollama.

## Stock Analysis & Future Price Prediction
- **Categories:** Time Series Forecasting, Deep Learning, BI/Dashboarding
- **Project Goal:** Build an analytical app for stock forecasting using technical indicators and deep learning.
- **Implementation Details:** Pulled market data from Yahoo Finance, generated 35 technical indicators, trained an LSTM forecasting model, and delivered a multi-chart interactive Streamlit interface.
- **Tech Stack:** Python, Streamlit, yfinance, pandas, numpy, matplotlib, LSTM.

## Voice AI Agent (Real-time Assistant)
- **Categories:** Voice AI, NLP/LLM, RAG, Real-time Systems
- **Project Goal:** Deliver a real-time voice assistant that listens, reasons over private knowledge, and responds with natural speech.
- **Implementation Details:** Built a FastAPI WebSocket server for real-time data flow, converted speech-to-text with Wav2Vec2, generated grounded responses via GPT-4o + Qdrant retrieval, and synthesized speech with OpenAI TTS.
- **Tech Stack:** Python, FastAPI (WebSockets), OpenAI API (GPT-4o + TTS), Qdrant, Wav2Vec2, NumPy.
