import streamlit as st
import pandas as pd
import json
from confluent_kafka import Consumer, KafkaException, KafkaError
import socket

# Konfigurasi Consumer untuk Docker Compose network
KAFKA_BOOTSTRAP = 'kafka:29092'
TOPIC = 'goodreads-books'

def test_kafka_connectivity():
    """Test if Kafka is reachable"""
    try:
        host, port = KAFKA_BOOTSTRAP.split(':')
        socket.create_connection((host, int(port)), timeout=5)
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

@st.cache_resource
def create_consumer():
    config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'streamlit-goodreads-consumer',
        'auto.offset.reset': 'earliest',   # mulai dari paling pertama
        'enable.auto.commit': False,
        'session.timeout.ms': 10000,  # Increase timeout
        'request.timeout.ms': 5000    # Reduce request timeout
    }
    consumer = Consumer(config)
    consumer.subscribe([TOPIC])
    return consumer

def fetch_messages(consumer, max_msgs=100):
    """Tarik sampai max_msgs, kembalikan list of dict"""
    records = []
    count = 0
    while count < max_msgs:
        msg = consumer.poll(timeout=1.0)  # Increase timeout slightly
        if msg is None:
            break
        if msg.error():
            # jika error tapi bukan EOF
            if msg.error().code() != KafkaError._PARTITION_EOF:
                raise KafkaException(msg.error())
            continue
        # valid message
        try:
            obj = json.loads(msg.value().decode('utf-8'))
            records.append(obj)
        except Exception:
            continue
        count += 1
    return records

def main():
    st.title("📚 Goodreads Kafka Stream Dashboard")
    
    # Show connection status
    st.subheader("🔗 Connection Status")
    is_connected, status_msg = test_kafka_connectivity()
    if is_connected:
        st.success(f"✅ Kafka: {status_msg}")
    else:
        st.error(f"❌ Kafka: {status_msg}")
        st.warning("Make sure Kafka is running and accessible at kafka:29092")
        return

    consumer = create_consumer()

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Quick Test (1 msg)", help="Fetch just 1 message quickly"):
            with st.spinner("Testing fetch..."):
                try:
                    data = fetch_messages(consumer, max_msgs=1)
                    if data:
                        st.success("✅ Message received!")
                        st.json(data[0])
                    else:
                        st.warning("No message available.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col2:
        if st.button("📊 Fetch Messages (100)", help="Fetch up to 100 messages"):
            with st.spinner("Fetching..."):
                try:
                    data = fetch_messages(consumer, max_msgs=100)
                    if data:
                        df = pd.DataFrame(data)
                        st.success(f"✅ Fetched {len(data)} messages")
                        st.dataframe(df)
                    else:
                        st.info("No new messages found.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    with col3:
        if st.button("💾 Commit Offsets", help="Commit current offset position"):
            try:
                consumer.commit()
                st.success("✅ Offsets committed.")
            except Exception as e:
                st.error(f"Error committing: {str(e)}")

    # Status information
    st.divider()
    st.subheader("ℹ️ Configuration")
    st.info(f"""
    **Consumer Group:** streamlit-goodreads-consumer  
    **Topic:** {TOPIC}  
    **Bootstrap Server:** {KAFKA_BOOTSTRAP}  
    """)
    
    # Debug info
    with st.expander("🐛 Debug Information"):
        st.code(f"""
Consumer Config:
- bootstrap.servers: {KAFKA_BOOTSTRAP}
- group.id: streamlit-goodreads-consumer
- auto.offset.reset: earliest
- enable.auto.commit: False
- session.timeout.ms: 10000
- request.timeout.ms: 5000
        """)

if __name__ == "__main__":
    main()
