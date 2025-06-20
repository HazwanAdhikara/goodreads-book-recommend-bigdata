
# Model Loading Helper for API
import pickle
from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALSModel
from pyspark.ml.feature import BucketedRandomProjectionLSHModel, CountVectorizerModel
import pandas as pd

def load_models(models_dir):
    """Load all trained models for the API"""
    
    # Initialize Spark
    spark = SparkSession.builder.appName("GoodreadsAPI").getOrCreate()
    
    # Load Spark models
    als_model = ALSModel.load(f"{models_dir}/als_model")
    lsh_model = BucketedRandomProjectionLSHModel.load(f"{models_dir}/lsh_model")
    cv_model = CountVectorizerModel.load(f"{models_dir}/cv_model")
    
    # Load data
    books_df = spark.read.parquet(f"{models_dir}/books_features.parquet")
    books_pdf = pd.read_parquet(f"{models_dir}/books_pandas.parquet")
    
    # Load metadata
    with open(f"{models_dir}/model_metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    
    return {
        "spark": spark,
        "als_model": als_model,
        "lsh_model": lsh_model,
        "cv_model": cv_model,
        "books_df": books_df,
        "books_pdf": books_pdf,
        "metadata": metadata
    }
