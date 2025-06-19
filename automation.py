#!/usr/bin/env python3
"""
Automation script for Goodreads Book Recommendation System
This script orchestrates the entire data lakehouse pipeline
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLakehouseAutomation:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.docker_compose_file = self.project_root / "docker-compose.yml"
        
    def run_command(self, command, cwd=None, check=True):
        """Execute a shell command"""
        logger.info(f"Running: {command}")
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                check=check, 
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True
            )
            if result.stdout:
                logger.info(f"Output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            if e.stderr:
                logger.error(f"Error: {e.stderr}")
            raise

    def wait_for_service(self, service_name, port, host="localhost", timeout=120):
        """Wait for a service to be ready"""
        import socket
        
        logger.info(f"Waiting for {service_name} on {host}:{port}")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with socket.create_connection((host, port), timeout=5):
                    logger.info(f"{service_name} is ready!")
                    return True
            except (socket.timeout, ConnectionRefusedError, OSError):
                time.sleep(5)
                
        logger.error(f"Timeout waiting for {service_name}")
        return False

    def setup_infrastructure(self):
        """Start all Docker services"""
        logger.info("🚀 Starting Data Lakehouse infrastructure...")
        
        # Build and start services
        self.run_command("docker-compose down -v")  # Clean start
        self.run_command("docker-compose up --build -d")
        
        # Wait for core services
        services_to_wait = [
            ("Zookeeper", 2181),
            ("Kafka", 9092),
            ("MinIO", 9000),
            ("PostgreSQL", 5432),
        ]
        
        for service_name, port in services_to_wait:
            if not self.wait_for_service(service_name, port):
                raise Exception(f"Failed to start {service_name}")
        
        # Wait a bit more for Hive Metastore and Trino
        logger.info("⏳ Waiting for Hive Metastore and Trino to initialize...")
        time.sleep(30)
        
        logger.info("✅ Infrastructure is ready!")

    def setup_kafka_topics(self):
        """Create necessary Kafka topics"""
        logger.info("📡 Setting up Kafka topics...")
        
        topics = [
            "goodreads-books",
            "book-recommendations",
            "user-interactions"
        ]
        
        for topic in topics:
            try:
                self.run_command(
                    f"docker exec kafka kafka-topics --create --topic {topic} "
                    f"--bootstrap-server localhost:9092 --partitions 3 --replication-factor 1",
                    check=False
                )
                logger.info(f"✅ Topic '{topic}' created/verified")
            except Exception as e:
                logger.warning(f"Topic '{topic}' might already exist: {e}")

    def start_kafka_producer(self):
        """Start streaming data to Kafka"""
        logger.info("🔄 Starting Kafka producer...")
        
        producer_cmd = (
            "python kafka-producer/producer.py "
            "--csv-file data/goodreads.csv "
            "--delay 0.1"
        )
        
        # Run producer in background
        subprocess.Popen(
            producer_cmd,
            shell=True,
            cwd=self.project_root
        )
        
        logger.info("✅ Kafka producer started")

    def train_ml_model(self):
        """Train the recommendation model using Spark"""
        logger.info("🤖 Training ML recommendation model...")
        
        # Submit Spark job
        spark_submit_cmd = (
            "docker exec spark-master spark-submit "
            "--master spark://spark-master:7077 "
            "--deploy-mode client "
            "/opt/spark-apps/recommendation_model.py "
            "--data-path /opt/spark-data/goodreads.csv "
            "--model-path /opt/spark-apps/models"
        )
        
        try:
            self.run_command(spark_submit_cmd)
            logger.info("✅ ML model training completed")
        except Exception as e:
            logger.warning(f"ML model training failed: {e}")
            logger.info("🔄 System will continue with basic recommendations")

    def setup_minio_buckets(self):
        """Create MinIO buckets and upload sample data"""
        logger.info("🗄️  Setting up MinIO storage...")
        
        # Create bucket using MinIO client
        minio_commands = [
            "docker exec minio mc alias set local http://localhost:9000 minioadmin minioadmin",
            "docker exec minio mc mb local/goodreads-lakehouse --ignore-existing",
            "docker exec minio mc mb local/models --ignore-existing",
            "docker exec minio mc mb local/streaming-data --ignore-existing"
        ]
        
        for cmd in minio_commands:
            try:
                self.run_command(cmd, check=False)
            except Exception as e:
                logger.warning(f"MinIO command failed (might be expected): {e}")
        
        logger.info("✅ MinIO buckets configured")

    def verify_system_health(self):
        """Check if all services are working correctly"""
        logger.info("🔍 Verifying system health...")
        
        health_checks = [
            ("API Backend", "curl -f http://localhost:5000/health"),
            ("Streamlit Dashboard", "curl -f http://localhost:8501"),
            ("React Frontend", "curl -f http://localhost:3000"),
            ("Spark Master", "curl -f http://localhost:8080"),
            ("MinIO Console", "curl -f http://localhost:9001"),
            ("Trino", "curl -f http://localhost:8081")
        ]
        
        results = {}
        for service, cmd in health_checks:
            try:
                self.run_command(cmd, check=True)
                results[service] = "✅ Healthy"
            except Exception:
                results[service] = "❌ Unhealthy"
        
        logger.info("📊 System Health Report:")
        for service, status in results.items():
            logger.info(f"  {service}: {status}")
        
        return all("✅" in status for status in results.values())

    def display_access_info(self):
        """Display access information for all services"""
        info = """
🎉 Goodreads Book Recommendation System is ready!

📱 Access URLs:
  • React Frontend:     http://localhost:3000
  • API Backend:        http://localhost:5000
  • Streamlit Dashboard: http://localhost:8501
  • Spark Master UI:    http://localhost:8080
  • MinIO Console:      http://localhost:9001 (admin/admin123)
  • Trino UI:           http://localhost:8081

🔧 Development Tools:
  • Kafka Topics:      localhost:9092
  • PostgreSQL:        localhost:5432 (hive/hive)
  • Hive Metastore:    localhost:9083

📚 Getting Started:
  1. Visit the React Frontend at http://localhost:3000
  2. Search for books or browse popular books
  3. Get AI-powered recommendations
  4. Monitor real-time streaming at http://localhost:8501
  5. Query data with Trino at http://localhost:8081

🛠️  Management Commands:
  • View logs:          docker-compose logs -f [service-name]
  • Stop system:        docker-compose down
  • Restart service:    docker-compose restart [service-name]
  • Clean restart:      docker-compose down -v && docker-compose up -d
        """
        
        print(info)

    def run_full_pipeline(self):
        """Execute the complete setup pipeline"""
        try:
            logger.info("🚀 Starting Goodreads Data Lakehouse setup...")
            
            # Step 1: Infrastructure
            self.setup_infrastructure()
            
            # Step 2: MinIO setup
            self.setup_minio_buckets()
            
            # Step 3: Kafka topics
            self.setup_kafka_topics()
            
            # Step 4: Start data streaming
            self.start_kafka_producer()
            
            # Step 5: Train ML model
            self.train_ml_model()
            
            # Step 6: Health check
            if self.verify_system_health():
                logger.info("✅ All systems operational!")
            else:
                logger.warning("⚠️  Some services may need attention")
            
            # Step 7: Display access info
            self.display_access_info()
            
            logger.info("🎉 Setup completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            logger.info("🔧 Try running: docker-compose logs to debug issues")
            raise

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Goodreads Data Lakehouse Automation')
    parser.add_argument('--action', choices=[
        'setup', 'infrastructure', 'kafka', 'model', 'health', 'info'
    ], default='setup', help='Action to perform')
    parser.add_argument('--project-root', help='Project root directory')
    
    args = parser.parse_args()
    
    automation = DataLakehouseAutomation(args.project_root)
    
    try:
        if args.action == 'setup':
            automation.run_full_pipeline()
        elif args.action == 'infrastructure':
            automation.setup_infrastructure()
        elif args.action == 'kafka':
            automation.setup_kafka_topics()
            automation.start_kafka_producer()
        elif args.action == 'model':
            automation.train_ml_model()
        elif args.action == 'health':
            automation.verify_system_health()
        elif args.action == 'info':
            automation.display_access_info()
            
    except KeyboardInterrupt:
        logger.info("⏹️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
