# Goodreads Book Recommendation System - Data Lakehouse Architecture

A comprehensive book recommendation system built with modern data lakehouse architecture, featuring real-time streaming, machine learning, and a beautiful React frontend.

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────┐    ┌─────────────────┐
│  React Frontend │     │ API Backend  │    │ Spark ML Engine │
│  (TypeScript)   │◄──► │   (Flask)    │◄──►│  (Rec. Model)   │
└─────────────────┘     └──────────────┘    └─────────────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ Streamlit Dash  │    │    MinIO     │    │      Trino      │
│  (Real-time)    │    │ (S3 Storage) │    │ (Query Engine)  │
└─────────────────┘    └──────────────┘    └─────────────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐    ┌──────────────┐     ┌─────────────────┐
│  Apache Kafka   │    │Hive Metastore│     │   PostgreSQL    │
│  (Streaming)    │    │  (Metadata)  │     │   (Metadata)    │
└─────────────────┘    └──────────────┘     └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.8+
- 8GB+ RAM recommended

### 1. Clone & Setup

```bash
git clone <your-repo>
cd goodreads-book-recommend-bigdata
```

### 2. Run Automated Setup

```bash
# Full automated setup
python automation.py --action setup

# Or step by step
python automation.py --action infrastructure
python automation.py --action kafka
python automation.py --action model
```

### 3. Access the System

- **React Frontend**: http://localhost:3000
- **API Backend**: http://localhost:5000
- **Streamlit Dashboard**: http://localhost:8501
- **Spark UI**: http://localhost:8080
- **MinIO Console**: http://localhost:9001
- **Trino**: http://localhost:8081

## 📊 Features

### Core Functionality

- **Content-Based Recommendations**: TF-IDF + Cosine Similarity on book descriptions
- **Collaborative Filtering**: ALS (Alternating Least Squares) algorithm
- **Hybrid Recommendations**: Combining multiple approaches
- **Real-time Streaming**: Kafka-based data pipeline
- **Interactive Dashboard**: Real-time visualization with Streamlit

### Frontend Features (React + TypeScript + Tailwind)

- **Modern UI**: Beautiful, responsive design with Tailwind CSS
- **Book Search**: Fast search across titles, authors, descriptions
- **Smart Recommendations**: AI-powered book suggestions
- **Filter & Sort**: Advanced filtering by rating, year, genre
- **Book Details**: Comprehensive book information pages

### Data Pipeline

- **Kafka Streaming**: Real-time book data ingestion
- **MinIO Storage**: S3-compatible object storage
- **Hive Metastore**: Schema management
- **Trino Queries**: Fast SQL analytics
- **Spark Processing**: Distributed ML training

## 🛠️ Technology Stack

| Component     | Technology                        | Purpose                   |
| ------------- | --------------------------------- | ------------------------- |
| Frontend      | React + TypeScript + Tailwind CSS | Modern, type-safe UI      |
| Backend API   | Flask + Python                    | RESTful API service       |
| ML Engine     | Apache Spark + MLlib              | Recommendation algorithms |
| Streaming     | Apache Kafka                      | Real-time data pipeline   |
| Storage       | MinIO (S3-compatible)             | Object storage            |
| Query Engine  | Trino                             | Distributed SQL queries   |
| Metadata      | Apache Hive + PostgreSQL          | Schema management         |
| Visualization | Streamlit                         | Real-time dashboards      |
| Orchestration | Docker Compose                    | Container management      |

## 📁 Project Structure

```
goodreads-book-recommend-bigdata/
├── 📄 docker-compose.yml           # Service orchestration
├── 🐍 automation.py                # Setup automation
├── 📊 cleaningdataset.ipynb        # Data preprocessing
│
├── 📡 kafka-producer/              # Streaming components
│   ├── producer.py                 # Kafka data producer
│   └── requirements.txt
│
├── 🎨 react-frontend/              # React TypeScript app
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── types/                 # TypeScript definitions
│   │   ├── services/              # API clients
│   │   └── utils/                 # Helper functions
│   ├── tailwind.config.js         # Tailwind configuration
│   ├── tsconfig.json              # TypeScript config
│   └── package.json
│
├── 🚀 api-backend/                 # Flask API service
│   ├── app.py                     # Main API application
│   ├── requirements.txt
│   └── Dockerfile
│
├── ⚡ spark-apps/                  # Spark applications
│   └── recommendation_model.py    # ML recommendation model
│
├── 📊 streamlit-app/               # Real-time dashboard
│   ├── app.py                     # Streamlit application
│   ├── requirements.txt
│   └── Dockerfile
│
├── 🗄️ trino-config/                # Trino configuration
│   ├── node.properties
│   ├── config.properties
│   └── catalog/
│       └── hive.properties
│
└── 📁 data/                        # Dataset storage
    ├── goodreads.csv              # Cleaned dataset
    └── raw.csv                    # Original dataset
```

## 🔧 API Endpoints

### Books API

- `GET /health` - System health check
- `GET /books/search?q=query` - Search books
- `GET /books/{id}` - Get book details
- `GET /books/popular` - Get popular books
- `GET /books/{id}/recommendations` - Get recommendations
- `POST /recommendations/filter` - Filtered recommendations

### Example API Usage

```bash
# Search books
curl "http://localhost:5000/books/search?q=python&limit=10"

# Get recommendations
curl "http://localhost:5000/books/123/recommendations?method=content&limit=5"

# Health check
curl "http://localhost:5000/health"
```

## 🤖 Machine Learning Models

### Content-Based Filtering

- **TF-IDF Vectorization**: Converts book descriptions to numerical vectors
- **Cosine Similarity**: Measures similarity between books
- **Features**: Authors, Publisher, Description, Rating, Pages

### Collaborative Filtering

- **ALS Algorithm**: Matrix factorization for user-item interactions
- **Synthetic Users**: Generated based on book popularity and ratings
- **Features**: User preferences, Book ratings, Interaction patterns

### Hybrid Approach

- Combines content and collaborative methods
- Weighted scoring system
- Fallback mechanisms for cold start problems

## 📈 Real-time Dashboard

The Streamlit dashboard provides:

- **Live Data Streaming**: Real-time book data from Kafka
- **Interactive Visualizations**: Rating distributions, popular publishers
- **Batch Management**: Save streaming data to MinIO
- **System Monitoring**: Health metrics and performance stats

For questions and support, please open an issue or contact the development team.

**Happy Reading! 📚✨**
