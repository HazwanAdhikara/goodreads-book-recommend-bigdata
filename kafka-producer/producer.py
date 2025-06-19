import pandas as pd
import json
import time
from confluent_kafka import Producer, KafkaError
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoodreadsKafkaProducer:
    def __init__(self, bootstrap_servers: str = 'localhost:9092', topic: str = 'goodreads-books'):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        
    def _create_producer(self) -> Producer:
        """Create Kafka producer with configuration"""
        config = {
            'bootstrap.servers': self.bootstrap_servers,
            'client.id': 'goodreads-producer',
            'acks': 'all',
            'retries': 3,
            'retry.backoff.ms': 300
        }
        return Producer(config)
    
    def _delivery_callback(self, err, msg):
        """Callback for message delivery reports"""
        if err:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')
    
    def send_book_data(self, csv_file_path: str, delay_seconds: float = 0.0001) -> None:
        """
        Read CSV file and send each book as a message to Kafka topic
        """
        try:
            self.producer = self._create_producer()

            # Test connection
            logger.info("🔌 Testing Kafka connection...")
            self.producer.poll(timeout=5)

            # Read CSV
            logger.info(f"📖 Reading CSV file: {csv_file_path}")
            df = pd.read_csv(csv_file_path, low_memory=False)
            total_books = len(df)
            logger.info(f"📚 Found {total_books} books to stream")

            sent_count = 0
            start_time = time.time()
            window_start = time.time()
            window_count = 0
            log_every_n = 10000  # Log after every 1000 messages

            for index, row in df.iterrows():
                try:
                    book_data = {
                        'Id': str(row['Id']),
                        'Name': str(row['Name'])[:500],
                        'Authors': str(row['Authors'])[:200],
                        'Rating': str(row['Rating']),
                        'PublishYear': str(row['PublishYear']),
                        'Publisher': str(row['Publisher'])[:200],
                        'RatingDistTotal': int(row['RatingDistTotal']) if pd.notna(row['RatingDistTotal']) else 0,
                        'PagesNumber': str(row['PagesNumber']),
                        'Description': str(row['Description'])[:1000] if pd.notna(row['Description']) else '',
                        'timestamp': time.time(),
                        'batch_id': f"batch_{int(time.time())}"
                    }

                    self.producer.produce(
                        topic=self.topic,
                        key=book_data['Id'],
                        value=json.dumps(book_data),
                        callback=self._delivery_callback
                    )
                    self.producer.poll(0)

                    sent_count += 1
                    window_count += 1

                    if sent_count % log_every_n == 0:
                        now = time.time()
                        elapsed = now - window_start
                        rate = window_count / elapsed if elapsed > 0 else 0
                        logger.info(f"🔥 Rate: {rate:.2f} books/sec | Sent: {sent_count}/{total_books}")
                        window_start = now
                        window_count = 0

                    # Full speed — no delay
                    # time.sleep(delay_seconds)

                except KeyboardInterrupt:
                    logger.info("⛔ Interrupted by user")
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Error processing book {index}: {str(e)}")
                    continue

            self.producer.flush()
            total_time = time.time() - start_time
            logger.info(f"✅ Completed. Total sent: {sent_count} books in {total_time:.2f} seconds "
                        f"({sent_count / total_time:.2f} books/sec)")

        except KeyboardInterrupt:
            logger.info("Producer interrupted by user")
        except Exception as e:
            logger.error(f"❌ Error sending data to Kafka: {str(e)}")
            raise
        finally:
            if self.producer:
                logger.info("📦 Flushing remaining messages...")
                self.producer.flush()
    
    def send_single_book(self, book_data: dict) -> None:
        """Send a single book record to Kafka"""
        try:
            if not self.producer:
                self.producer = self._create_producer()
            
            book_data['timestamp'] = time.time()

            self.producer.produce(
                topic=self.topic,
                key=book_data.get('Id'),
                value=json.dumps(book_data),
                callback=self._delivery_callback
            )

            self.producer.flush()
            logger.info(f"Sent book: {book_data.get('Name', 'Unknown')}")

        except Exception as e:
            logger.error(f"Error sending single book: {str(e)}")
            raise

def main():
    """Main function to run the Kafka producer"""
    import argparse

    parser = argparse.ArgumentParser(description='Stream Goodreads data to Kafka')
    parser.add_argument('--csv-file', default='../data/goodreads.csv', 
                        help='Path to the CSV file')
    parser.add_argument('--kafka-servers', default='localhost:9092',
                        help='Kafka bootstrap servers')
    parser.add_argument('--topic', default='goodreads-books',
                        help='Kafka topic name')
    parser.add_argument('--delay', type=float, default=0.0001,
                        help='Delay between messages in seconds')

    args = parser.parse_args()

    producer = GoodreadsKafkaProducer(
        bootstrap_servers=args.kafka_servers,
        topic=args.topic
    )

    try:
        producer.send_book_data(args.csv_file, args.delay)
    except KeyboardInterrupt:
        logger.info("Producer stopped by user")
    except Exception as e:
        logger.error(f"Producer failed: {str(e)}")

if __name__ == "__main__":
    main()
