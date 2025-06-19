import streamlit as st
import pandas as pd
import json
import time
import plotly.express as px
import plotly.graph_objects as go
from confluent_kafka import Consumer, KafkaException, KafkaError
import socket
import numpy as np
import logging
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Konfigurasi Consumer untuk Docker Compose network
KAFKA_BOOTSTRAP = 'kafka:29092'
TOPIC = 'goodreads-books'

# MinIO Configuration
MINIO_ENDPOINT = 'minio:9000'
MINIO_ACCESS_KEY = 'minioadmin'
MINIO_SECRET_KEY = 'minioadmin'
MINIO_BUCKET = 'streaming-data'

def test_kafka_connectivity():
    """Test if Kafka is reachable"""
    try:
        host, port = KAFKA_BOOTSTRAP.split(':')
        socket.create_connection((host, int(port)), timeout=5)
        return True, "Connection successful"
    except Exception as e:
        return False, f"Connection failed: {str(e)}"

def create_consumer():
    config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': f'streamlit-debug-{int(time.time())}',  # Always new group
        'auto.offset.reset': 'earliest',  # Always read from beginning
        'enable.auto.commit': True,
        'session.timeout.ms': 30000,  # 30 seconds
        'max.poll.interval.ms': 300000  # 5 minutes
    }
    consumer = Consumer(config)
    consumer.subscribe([TOPIC])
    return consumer

def fetch_messages(consumer, max_msgs=100):
    records = []
    count = 0
    
    logger.info(f"🔍 Starting to fetch {max_msgs} messages...")
    
    while count < max_msgs:
        msg = consumer.poll(timeout=5.0)
        if msg is None:
            logger.info(f"⏱️ No message received after timeout. Got {count} messages so far.")
            break
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                logger.error(f"❌ Kafka error: {msg.error()}")
                raise KafkaException(msg.error())
            logger.info("📄 Reached end of partition")
            continue
        
        try:
            obj = json.loads(msg.value().decode('utf-8'))
            records.append(obj)
            logger.info(f"✅ Message {count+1}: {obj.get('Name', 'Unknown')[:30]}...")
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse message: {e}")
            continue
        count += 1
    
    logger.info(f"📊 Fetched {len(records)} total messages")
    return records

def fetch_and_cache_messages(max_msgs=100):
    logger.info(f"🚀 Creating new consumer for {max_msgs} messages")
    consumer = create_consumer()
    try:
        result = fetch_messages(consumer, max_msgs)
        logger.info(f"🎯 fetch_and_cache_messages returning {len(result)} messages")
        return result
    except Exception as e:
        logger.error(f"💥 Error in fetch_and_cache_messages: {e}")
        return []
    finally:
        consumer.close()
        logger.info("🔒 Consumer closed")

def create_rating_chart(df):
    if 'Rating' not in df.columns or df.empty:
        return None

    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    rating_counts = df['Rating'].value_counts().sort_index()

    fig = px.bar(
        x=rating_counts.index,
        y=rating_counts.values,
        labels={'x': 'Rating', 'y': 'Number of Books'},
        title="📊 Rating Distribution",
        color=rating_counts.values,
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Rating",
        yaxis_title="Number of Books",
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font_color='white'
    )

    return fig


def create_year_chart(df):
    if 'PublishYear' not in df.columns or df.empty:
        return None

    df_clean = df.copy()
    df_clean['PublishYear'] = pd.to_numeric(df_clean['PublishYear'], errors='coerce')
    df_clean = df_clean.dropna(subset=['PublishYear'])
    df_clean = df_clean[df_clean['PublishYear'] > 1800]

    year_counts = df_clean['PublishYear'].value_counts().sort_index()

    fig = px.bar(
        x=year_counts.index,
        y=year_counts.values,
        labels={'x': 'Year', 'y': 'Number of Books'},
        title="📚 Books Published Per Year",
        color=year_counts.values,
        color_continuous_scale='Agsunset'
    )

    fig.update_layout(
        height=400,
        xaxis_title="Publication Year",
        yaxis_title="Number of Books",
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font_color='white'
    )

    return fig


def filter_data(df, min_rating=0.0, year_filter=False, year_range=(2000, 2024)):
    if df.empty:
        return df
    
    filtered_df = df.copy()
    
    if 'Rating' in filtered_df.columns:
        filtered_df['Rating'] = pd.to_numeric(filtered_df['Rating'], errors='coerce')
        filtered_df = filtered_df[filtered_df['Rating'] >= min_rating]
    
    if year_filter and 'PublishYear' in filtered_df.columns:
        filtered_df['PublishYear'] = pd.to_numeric(filtered_df['PublishYear'], errors='coerce')
        filtered_df = filtered_df[
            (filtered_df['PublishYear'] >= year_range[0]) & 
            (filtered_df['PublishYear'] <= year_range[1])
        ]
    
    return filtered_df

@st.cache_resource
def create_minio_client():
    try:
        client = boto3.client(
            's3',
            endpoint_url=f'http://{MINIO_ENDPOINT}',
            aws_access_key_id=MINIO_ACCESS_KEY,
            aws_secret_access_key=MINIO_SECRET_KEY,
            region_name='us-east-1'
        )
        return client
    except Exception as e:
        logger.error(f"Failed to create MinIO client: {e}")
        return None

def save_data_to_minio(df, filename=None):
    if df.empty:
        return False, "No data to save"
    
    try:
        client = create_minio_client()
        if not client:
            return False, "MinIO client not available"

        # Cek dan buat bucket jika belum ada
        buckets = client.list_buckets()
        bucket_names = [b['Name'] for b in buckets['Buckets']]
        if MINIO_BUCKET not in bucket_names:
            client.create_bucket(Bucket=MINIO_BUCKET)

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"books_batch_{timestamp}.csv"

        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        client.put_object(
            Bucket=MINIO_BUCKET,
            Key=filename,
            Body=csv_buffer.getvalue(),
            ContentType='application/octet-stream'
        )

        logger.info(f"✅ Saved {len(df)} records to MinIO: {filename}")
        return True, f"Saved as {filename}"

    except ClientError as e:
        error_msg = f"MinIO error: {e}"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error saving to MinIO: {e}"
        logger.error(error_msg)
        return False, error_msg


def list_minio_files():
    try:
        client = create_minio_client()
        if not client:
            return []
        
        response = client.list_objects_v2(Bucket=MINIO_BUCKET)
        files = []
        
        if 'Contents' in response:
            for obj in response['Contents']:
                files.append({
                    'filename': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified']
                })
        
        return files
    except Exception as e:
        logger.error(f"Error listing MinIO files: {e}")
        return []

def main():
    st.set_page_config(
        page_title="Goodreads Book Recommendation System",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #cccccc;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .book-card {
        border: 1px solid #444;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: #1e1e1e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #2d2d2d;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #ccc;
    }
    .stTabs [aria-selected="true"] {
        background-color: #444;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">📚 Goodreads Book Recommendation System</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time book data streaming and analytics dashboard</p>', unsafe_allow_html=True)
    
    # Quick connection check (hidden from main view)
    is_connected, status_msg = test_kafka_connectivity()
    if not is_connected:
        st.error(f"⚠️ Connection Issue: {status_msg}")
        st.info("💡 Make sure Kafka is running: `docker-compose up kafka`")
        st.stop()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Auto-refresh toggle
        auto_refresh = st.toggle("🔄 Auto Refresh", value=False, help="Automatically refresh data every 5 seconds")
        
        # Number of books to fetch
        num_books = st.slider("📊 Books to Display", 10, 200, 50, help="Number of recent books to load from Kafka")
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.rerun()
        st.divider()
        
        # MinIO Storage Controls
        st.subheader("🗄️ Data Storage")
        
        # Manual save button
        if st.button("💾 Save Current Data to MinIO", use_container_width=True):
            # This will trigger a save on next data fetch
            st.session_state.force_save = True
        
        # Show MinIO files
        with st.expander("📁 View MinIO Files"):
            minio_files = list_minio_files()
            if minio_files:
                for file_info in minio_files[:5]:  # Show last 5 files
                    st.text(f"📄 {file_info['filename']}")
                    st.caption(f"Size: {file_info['size']} bytes | Modified: {file_info['modified']}")
            else:
                st.info("No files in MinIO yet")
        
        st.divider()
        
        # Filters
        st.subheader("🔍 Filters")
        min_rating = st.slider("⭐ Minimum Rating", 0.0, 5.0, 0.0, 0.1)
        
        # Year filter
        year_filter = st.checkbox("📅 Filter by Publication Year")
        if year_filter:
            year_range = st.slider("Select Year Range", 1900, 2024, (2000, 2024))
        else:
            year_range = (2000, 2024)
        
        st.divider()
        
        # Connection status (compact)
        st.success("✅ Kafka Connected")
        st.caption(f"📡 Topic: {TOPIC}")
        st.caption(f"🔗 Bootstrap: {KAFKA_BOOTSTRAP}")
    
    # Main content area
    # Fetch and display data
    with st.spinner("📚 Loading latest books..."):
        try:
            data = fetch_and_cache_messages(max_msgs=num_books)
            logger.info(f"🎭 Main function got {len(data) if data else 0} records")
            
            if data:
                logger.info(f"✅ Data exists, creating DataFrame with {len(data)} records")
                df = pd.DataFrame(data)
                
                # Auto-save to MinIO (batch processing)
                should_save = (len(df) > 10) or st.session_state.get('force_save', False)
                
                if should_save:
                    with st.spinner("💾 Saving data to MinIO..."):
                        save_success, save_msg = save_data_to_minio(df)
                        if save_success:
                            st.success(f"✅ Data saved to MinIO: {save_msg}")
                        else:
                            st.error(f"❌ MinIO save failed: {save_msg}")
                    
                    # Reset force save flag
                    if 'force_save' in st.session_state:
                        del st.session_state.force_save
                else:
                    st.info(f"📊 Got {len(df)} records. Auto-save threshold: 10+ records")
                
                # Apply filters
                filtered_df = filter_data(df, min_rating, year_filter, year_range)
                
                if filtered_df.empty:
                    st.warning("🔍 No books match your current filters. Try adjusting the filter criteria.")
                    st.stop()
                
                # Metrics row
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📚 Total Books", len(filtered_df), delta=f"{len(filtered_df) - len(df)} filtered" if len(filtered_df) != len(df) else None)
                
                with col2:
                    if 'Rating' in filtered_df.columns:
                        avg_rating = pd.to_numeric(filtered_df['Rating'], errors='coerce').mean()
                        st.metric("⭐ Avg Rating", f"{avg_rating:.2f}" if not pd.isna(avg_rating) else "N/A")
                    else:
                        st.metric("⭐ Avg Rating", "N/A")
                
                with col3:
                    unique_authors = len(filtered_df['Authors'].unique()) if 'Authors' in filtered_df.columns else 0
                    st.metric("👥 Unique Authors", unique_authors)
                
                with col4:
                    if 'PublishYear' in filtered_df.columns:
                        latest_year = pd.to_numeric(filtered_df['PublishYear'], errors='coerce').max()
                        st.metric("📅 Latest Year", int(latest_year) if not pd.isna(latest_year) else "N/A")
                    else:
                        st.metric("📅 Latest Year", "N/A")
                
                st.divider()
                
                # Display options
                tab1, tab2, tab3, tab4 = st.tabs(["📖 Book Gallery", "📊 Data Table", "📈 Analytics", "🔍 Book Details"])
                
                with tab1:
                    st.subheader("📖 Featured Books")
                    
                    # Display books as enhanced cards
                    cols = st.columns(3)
                    display_books = filtered_df.head(15)  # Show first 15 books as cards
                    
                    for idx, (_, book) in enumerate(display_books.iterrows()):
                        with cols[idx % 3]:
                            with st.container():
                                st.markdown(f"""
                                <div class="book-card">
                                    <h4 style="margin-top:0;">{book.get('Name', 'Unknown Title')[:60]}</h4>
                                    <p><strong>Author:</strong> {book.get('Authors', 'Unknown')[:40]}</p>
                                    <p><strong>Rating:</strong> ⭐ {book.get('Rating', 'N/A')} | <strong>Year:</strong> 📅 {book.get('PublishYear', 'N/A')}</p>
                                    <p><strong>Publisher:</strong> {book.get('Publisher', 'Unknown')[:30]}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                if book.get('Description'):
                                    with st.expander("📝 Description"):
                                        st.write(book['Description'][:200] + "..." if len(str(book['Description'])) > 200 else book['Description'])
                
                with tab2:
                    st.subheader("📊 Complete Book Data")

                    display_columns = ['Name', 'Authors', 'Rating', 'PublishYear', 'Publisher', 'PagesNumber', 'Description']
                    available_columns = [col for col in display_columns if col in filtered_df.columns]

                    if available_columns:
                        display_df = filtered_df[available_columns].copy()

                        if 'Rating' in display_df.columns:
                            display_df['Rating'] = pd.to_numeric(display_df['Rating'], errors='coerce').round(2)

                        # Rename PagesNumber to Pages for better display
                        if 'PagesNumber' in display_df.columns:
                            display_df = display_df.rename(columns={'PagesNumber': 'Pages'})

                        st.dataframe(display_df, use_container_width=True, height=400)

                        # Form untuk batch size download
                        with st.form(key='download_form'):
                            st.subheader("📥 Download Data")
                            batch_size = st.slider("Number of records to download", 10, len(display_df), 50)
                            submitted = st.form_submit_button("Download CSV")

                            if submitted:
                                download_df = display_df.head(batch_size)
                                csv = download_df.to_csv(index=False)
                                st.download_button(
                                    label="📥 Click here to download",
                                    data=csv,
                                    file_name="goodreads_download.csv",
                                    mime="text/csv"
                                )
                    else:
                        st.info("No data columns available for display.")

                
                with tab3:
                    st.subheader("📈 Book Analytics")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Interactive rating chart
                        rating_chart = create_rating_chart(filtered_df)
                        if rating_chart:
                            st.plotly_chart(rating_chart, use_container_width=True)
                        else:
                            st.info("Rating data not available for visualization.")
                    
                    with col2:
                        # Interactive year chart
                        year_chart = create_year_chart(filtered_df)
                        if year_chart:
                            st.plotly_chart(year_chart, use_container_width=True)
                        else:
                            st.info("Publication year data not available for visualization.")
                    
                    # Additional analytics
                    if 'Authors' in filtered_df.columns:
                        st.subheader("👥 Top Authors")
                        author_counts = filtered_df['Authors'].value_counts().head(10)
                        if not author_counts.empty:
                            fig_authors = px.bar(
                                x=author_counts.values,
                                y=author_counts.index,
                                orientation='h',
                                labels={'x': 'Number of Books', 'y': 'Authors'},
                                title="Top 10 Authors by Book Count"
                            )
                            fig_authors.update_layout(height=400)
                            st.plotly_chart(fig_authors, use_container_width=True)
                
                with tab4:
                    st.subheader("🔍 Detailed Book Information")
                    
                    # Book selector
                    if not filtered_df.empty:
                        book_titles = filtered_df['Name'].tolist() if 'Name' in filtered_df.columns else []
                        
                        if book_titles:
                            selected_book = st.selectbox("Choose a book to view details:", book_titles)
                            
                            if selected_book:
                                book_data = filtered_df[filtered_df['Name'] == selected_book].iloc[0]
                                
                                # Display detailed information
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.markdown(f"### {book_data.get('Name', 'Unknown Title')}")
                                    st.markdown(f"**Author:** {book_data.get('Authors', 'Unknown')}")
                                    st.markdown(f"**Rating:** ⭐ {book_data.get('Rating', 'N/A')}")
                                    st.markdown(f"**Publication Year:** {book_data.get('PublishYear', 'N/A')}")
                                    st.markdown(f"**Publisher:** {book_data.get('Publisher', 'Unknown')}")
                                    
                                    if book_data.get('Description'):
                                        st.markdown("**Description:**")
                                        st.write(book_data['Description'])
                                
                                with col2:
                                    # Book statistics
                                    st.metric("Book Rating", book_data.get('Rating', 'N/A'))
                                    st.metric("Publication Year", book_data.get('PublishYear', 'N/A'))
                                    
                                    # Additional info if available
                                    if book_data.get('PagesNumber'):
                                        st.metric("Pages", book_data.get('PagesNumber', 'N/A'))
                        else:
                            st.info("No books available for detailed view.")
            
            else:
                logger.warning("❌ No data returned from fetch_and_cache_messages")
                st.warning("📭 No new books available from Kafka stream!")
                
                # Enhanced troubleshooting information
                st.markdown("""
                **Troubleshooting Steps:**
                1. **Check Producer**: Ensure `python3 producer.py` is running in the `kafka-producer` directory
                2. **Check Kafka Topic**: The producer should be sending to topic `goodreads-books`
                3. **Reset Consumer**: Click "Reset & Refresh" button above to get latest data
                4. **Check Docker**: Ensure Kafka container is running: `docker ps | grep kafka`
                
                **Quick Commands:**
                ```bash
                # Check Kafka topics
                docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
                
                # Check messages in topic
                docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic goodreads-books --max-messages 5
                ```
                """)
                
                # Show current consumer group for debugging
                consumer_group = st.session_state.get('consumer_group_id', 'streamlit-goodreads-consumer')
                st.info(f"🔍 Current consumer group: `{consumer_group}`")
                
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.markdown("""
            **Troubleshooting:**
            - Ensure Kafka is running: `docker-compose up kafka`
            - Check if the topic exists: `goodreads-books`
            - Verify the producer is sending data
            """)
    
    # Auto-refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
