import streamlit as st
import numpy as np
from typing import List, Tuple, Dict
import re
import time
from datetime import datetime

# NLP and semantic expansion imports
try:
    from sentence_transformers import SentenceTransformer
    import nltk
    from nltk.corpus import wordnet
    from nltk.tokenize import word_tokenize
    import ssl
    
    # Handle SSL certificate issue for NLTK
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_unverified_context = _create_unverified_https_context
    
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
except ImportError:
    st.error("Required packages not installed. Run: pip install sentence-transformers nltk")

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="PatentSeek",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary: #0066cc;
        --primary-dark: #004999;
        --secondary: #f0f2f6;
        --accent: #ff6b6b;
        --text-dark: #1a1a1a;
        --text-light: #666666;
        --border: #e0e0e0;
    }
    
    /* Typography */
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: var(--text-dark);
    }
    
    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 600;
    }
    
    /* Main container styling */
    .main-header {
        padding: 2rem 0 1rem 0;
        border-bottom: 3px solid var(--primary);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Input section */
    .input-section {
        background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        margin-bottom: 2rem;
    }
    
    .input-section textarea {
        border: 2px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        font-size: 14px;
        font-family: inherit;
        transition: border-color 0.3s;
    }
    
    .input-section textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    /* Results section */
    .results-container {
        margin-top: 2rem;
    }
    
    .patent-card {
        background: white;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .patent-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border-color: var(--primary);
        transform: translateY(-2px);
    }
    
    .patent-card::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 4px;
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
        transform: scaleY(0);
        transform-origin: top;
        transition: transform 0.3s;
    }
    
    .patent-card:hover::before {
        transform: scaleY(1);
    }
    
    .patent-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 0.5rem;
        cursor: pointer;
        text-decoration: none;
        transition: color 0.3s;
    }
    
    .patent-title:hover {
        color: var(--primary-dark);
        text-decoration: underline;
    }
    
    .patent-number {
        font-size: 12px;
        color: var(--text-light);
        font-weight: 500;
        font-family: 'Courier New', monospace;
        margin-bottom: 0.75rem;
    }
    
    .patent-meta {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
        font-size: 13px;
    }
    
    .patent-meta-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--text-light);
    }
    
    .patent-meta-label {
        font-weight: 600;
        color: var(--text-dark);
    }
    
    .patent-abstract {
        color: var(--text-light);
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    
    .similarity-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .relevance-bar {
        width: 100%;
        height: 6px;
        background: var(--secondary);
        border-radius: 3px;
        overflow: hidden;
        margin-top: 0.5rem;
    }
    
    .relevance-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        border-radius: 3px;
    }
    
    /* Status indicators */
    .status-loading {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        background: #e3f2fd;
        border-radius: 8px;
        color: var(--primary);
        font-weight: 500;
    }
    
    .status-error {
        padding: 1rem;
        background: #ffebee;
        border-radius: 8px;
        color: var(--accent);
        font-weight: 500;
    }
    
    .status-success {
        padding: 1rem;
        background: #e8f5e9;
        border-radius: 8px;
        color: #2e7d32;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .sidebar-section {
        background: var(--secondary);
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section h3 {
        margin-top: 0;
        color: var(--primary);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        margin-bottom: 1rem;
        font-size: 13px;
        color: var(--text-dark);
    }
    
    </style>
""", unsafe_allow_html=True)


# ============================================================================
# SEMANTIC EXPANSION UTILITIES
# ============================================================================

@st.cache_resource
def load_embedding_model():
    """Load sentence transformer model for semantic similarity."""
    return SentenceTransformer('all-MiniLM-L6-v2')


def get_synonyms_and_related(text: str) -> List[str]:
    """
    Extract synonyms and related terms using WordNet.
    """
    tokens = word_tokenize(text.lower())
    expanded_terms = set(tokens)
    
    for token in tokens:
        # Skip short words and common stopwords
        if len(token) <= 2 or token in ['the', 'a', 'an', 'is', 'are', 'for', 'with', 'to', 'of']:
            continue
        
        # Get synonyms
        for synset in wordnet.synsets(token):
            for lemma in synset.lemmas():
                synonyms = lemma.name().replace('_', ' ')
                if synonyms not in expanded_terms:
                    expanded_terms.add(synonyms)
        
        # Get hypernyms (more general terms)
        for synset in wordnet.synsets(token):
            for hypernym in synset.hypernyms():
                for lemma in hypernym.lemmas():
                    hypernym_name = lemma.name().replace('_', ' ')
                    if hypernym_name not in expanded_terms:
                        expanded_terms.add(hypernym_name)
    
    return list(expanded_terms)


def create_semantic_query(description: str, model) -> str:
    """
    Create an expanded semantic query using embeddings.
    Identifies the most important terms based on semantic relevance.
    """
    # Get base expansion
    expanded_terms = get_synonyms_and_related(description)
    
    # Rank terms by semantic similarity to original description
    description_embedding = model.encode(description)
    term_embeddings = model.encode(expanded_terms)
    
    similarities = np.dot(term_embeddings, description_embedding)
    ranked_indices = np.argsort(similarities)[::-1]
    
    # Take top terms
    top_terms = [expanded_terms[i] for i in ranked_indices[:15]]
    
    # Create enhanced query combining original and expanded terms
    query_parts = [description]
    query_parts.extend(top_terms[:8])
    
    return ' '.join(query_parts)


# ============================================================================
# GOOGLE PATENTS SEARCH
# ============================================================================

def search_google_patents(query: str, max_results: int = 15) -> List[Dict]:
    """
    Search Google Patents for patents matching the query.
    """
    patents = []
    base_url = "https://patents.google.com/?q="
    search_url = base_url + quote(query)
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse patent results - note: Google Patents structure may change
        # This is a simplified parser - you may need to adjust selectors
        result_containers = soup.find_all('div', class_='goog-container')
        
        if not result_containers:
            # Fallback: try alternative selectors
            result_containers = soup.find_all('article', class_='tYb')
        
        for container in result_containers[:max_results]:
            try:
                # Extract patent information
                patent_link = container.find('a')
                if not patent_link:
                    continue
                
                title = patent_link.get_text(strip=True)
                patent_url = patent_link.get('href', '')
                
                if not patent_url.startswith('http'):
                    patent_url = 'https://patents.google.com' + patent_url
                
                # Extract patent number from URL or title
                patent_number = extract_patent_number(patent_url, title)
                
                # Extract metadata
                meta_text = container.get_text(strip=True)
                
                patent_data = {
                    'title': title,
                    'number': patent_number,
                    'url': patent_url,
                    'abstract': meta_text[:200] + '...' if len(meta_text) > 200 else meta_text,
                    'applicant': 'N/A',
                    'filing_date': 'N/A',
                    'publication_date': 'N/A',
                }
                
                patents.append(patent_data)
            except Exception as e:
                continue
        
    except requests.RequestException as e:
        st.warning(f"⚠️ Error fetching from Google Patents: {str(e)}")
    
    return patents


def extract_patent_number(url: str, title: str) -> str:
    """Extract patent number from URL or title."""
    # Try to extract from URL
    match = re.search(r'([A-Z]{2}\d{7}|US\d+)', url)
    if match:
        return match.group(1)
    
    # Try to extract from title
    match = re.search(r'([A-Z]{2}\d{7}|US\d+)', title)
    if match:
        return match.group(1)
    
    # Default format
    match = re.search(r'\d{7,}', title)
    if match:
        return match.group(0)
    
    return 'Unknown'


def calculate_relevance_scores(patents: List[Dict], description: str, model) -> List[Dict]:
    """
    Calculate semantic relevance scores between patents and original description.
    """
    description_embedding = model.encode(description)
    
    for patent in patents:
        # Create searchable text from patent data
        patent_text = f"{patent['title']} {patent['abstract']}"
        patent_embedding = model.encode(patent_text)
        
        # Calculate cosine similarity
        similarity = np.dot(patent_embedding, description_embedding) / (
            np.linalg.norm(patent_embedding) * np.linalg.norm(description_embedding) + 1e-10
        )
        
        # Convert to percentage
        patent['relevance_score'] = max(0, min(100, similarity * 100))
    
    # Sort by relevance
    patents = sorted(patents, key=lambda x: x['relevance_score'], reverse=True)
    
    return patents


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_patent_card(patent: Dict, index: int):
    """Render a single patent result card."""
    relevance = patent.get('relevance_score', 0)
    
    html = f"""
    <div class="patent-card">
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
            <div>
                <a href="{patent['url']}" target="_blank" class="patent-title">
                    {patent['title']}
                </a>
                <div class="patent-number">Patent: {patent['number']}</div>
            </div>
            <span class="similarity-badge">{relevance:.0f}% Match</span>
        </div>
        
        <div class="patent-meta">
            <div class="patent-meta-item">
                <span class="patent-meta-label">Applicant:</span>
                <span>{patent.get('applicant', 'N/A')}</span>
            </div>
            <div class="patent-meta-item">
                <span class="patent-meta-label">Filed:</span>
                <span>{patent.get('filing_date', 'N/A')}</span>
            </div>
            <div class="patent-meta-item">
                <span class="patent-meta-label">Published:</span>
                <span>{patent.get('publication_date', 'N/A')}</span>
            </div>
            <div class="patent-meta-item">
                <span class="patent-meta-label">Type:</span>
                <span>Utility Patent</span>
            </div>
        </div>
        
        <div class="patent-abstract">{patent['abstract']}</div>
        
        <div class="relevance-bar">
            <div class="relevance-fill" style="width: {relevance}%;"></div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_query_info(original: str, expanded: str):
    """Render information about the semantic query expansion."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Original Query:**")
        st.code(original, language=None)
    
    with col2:
        st.markdown("**Expanded Query:**")
        st.code(expanded, language=None)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🔍 PatentSeek</h1>
            <p style="color: #666; margin: 0.5rem 0 0 0; font-size: 14px;">
                Intelligent patent search powered by NLP semantic expansion
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'expanded_query' not in st.session_state:
        st.session_state.expanded_query = None
    if 'original_description' not in st.session_state:
        st.session_state.original_description = None
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        st.markdown("""
            <div class="sidebar-section">
                <h3 style="margin-top: 0;">How It Works</h3>
                <p style="font-size: 13px; color: #666;">
                    1. <strong>Enter description</strong> of your invention<br>
                    2. <strong>Semantic expansion</strong> generates related terms<br>
                    3. <strong>Search Google Patents</strong> with expanded query<br>
                    4. <strong>Rank results</strong> by relevance score
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        num_results = st.slider(
            "Number of results",
            min_value=5,
            max_value=30,
            value=15,
            step=5,
            help="How many patents to retrieve"
        )
        
        show_query_info = st.checkbox(
            "Show query expansion",
            value=False,
            help="Display original vs. expanded queries"
        )
        
        st.markdown("""
            <div class="sidebar-section">
                <h3 style="margin-top: 0;">💡 Tips</h3>
                <p style="font-size: 12px; color: #666;">
                    • Use 2-3 sentences for best results<br>
                    • Include key technical terms<br>
                    • Describe the problem & solution<br>
                    • Be specific about novelty
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    # Main input section
    st.markdown("""
        <div class="input-section">
            <h3 style="margin-top: 0;">📝 Describe Your Invention</h3>
            <p style="color: #666; font-size: 13px;">
                Provide a clear, detailed description of your invention. The more specific you are, 
                the better the patent search results will be.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    description = st.text_area(
        "Invention Description",
        height=150,
        placeholder="Example: A machine learning system that automatically detects anomalies in time-series data using a novel neural network architecture based on attention mechanisms and wavelet transforms...",
        label_visibility="collapsed"
    )
    
    # Search button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        search_button = st.button("🔍 Search Patents", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear Results", use_container_width=True)
    
    if clear_button:
        st.session_state.search_results = None
        st.session_state.expanded_query = None
        st.rerun()
    
    # Execute search
    if search_button and description:
        # Load model
        model = load_embedding_model()
        
        # Create progress tracking
        with st.spinner("🔄 Expanding query with semantic analysis..."):
            expanded_query = create_semantic_query(description, model)
            st.session_state.expanded_query = expanded_query
            st.session_state.original_description = description
        
        with st.spinner("🔍 Searching Google Patents..."):
            patents = search_google_patents(expanded_query, max_results=num_results)
        
        if patents:
            with st.spinner("⚖️ Calculating relevance scores..."):
                patents = calculate_relevance_scores(patents, description, model)
            
            st.session_state.search_results = patents
        else:
            st.warning("No patents found. Try with different keywords.")
    
    # Display results
    if st.session_state.search_results:
        st.markdown("---")
        
        # Query info section
        if show_query_info and st.session_state.expanded_query:
            with st.expander("📊 Query Analysis", expanded=False):
                render_query_info(
                    st.session_state.original_description,
                    st.session_state.expanded_query
                )
        
        # Results header
        num_patents = len(st.session_state.search_results)
        st.markdown(f"""
            <div class="status-success">
                ✓ Found {num_patents} relevant patents
            </div>
        """, unsafe_allow_html=True)
        
        # Patent cards
        st.markdown("### 📋 Patent Search Results")
        
        for idx, patent in enumerate(st.session_state.search_results, 1):
            render_patent_card(patent, idx)
        
        # Export options
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export as CSV"):
                import pandas as pd
                df = pd.DataFrame([
                    {
                        'Rank': i,
                        'Title': p['title'],
                        'Patent Number': p['number'],
                        'Relevance Score': f"{p.get('relevance_score', 0):.1f}%",
                        'URL': p['url'],
                        'Applicant': p.get('applicant', 'N/A'),
                        'Filed': p.get('filing_date', 'N/A'),
                    }
                    for i, p in enumerate(st.session_state.search_results, 1)
                ])
                
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"patent_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            if st.button("📄 Export as JSON"):
                import json
                json_data = json.dumps(st.session_state.search_results, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"patent_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    elif description:
        st.info("👆 Click 'Search Patents' to find relevant patents for your invention.")
    
    else:
        # Empty state
        st.markdown("""
            <div class="info-box">
                <strong>Get Started:</strong> Describe your invention in detail and click "Search Patents" 
                to find the top relevant patents. PatentSeek uses advanced NLP to semantically expand 
                your query and identify the most relevant patents from Google Patents.
            </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()