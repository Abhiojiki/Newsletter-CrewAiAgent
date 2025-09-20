import streamlit as st
import sys
import os
from crewai import Crew, Process
from news_agents import NewsAgents, StreamToExpander
from news_tasks import NewsTasks
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set page configuration
st.set_page_config(page_title="AI News Letter", page_icon="📰", layout="wide")

def safe_read_file(file_path):
    """Safely read file with proper encoding"""
    if not os.path.exists(file_path):
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception:
            return None
    except Exception:
        return None

def get_report(output_file):
    """Display report content as rendered markdown"""
    content = safe_read_file(output_file)
    if content:
        st.markdown(content)
    else:
        st.warning(f"Report file '{output_file}' not found or couldn't be read.")

def clean_text_for_pdf(text):
    """Clean text for PDF generation"""
    if not text:
        return ""
    
    # Remove markdown formatting that doesn't work well in PDF
    text = re.sub(r'#{1,6}\s+', '', text)  # Remove markdown headers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold formatting
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic formatting
    text = re.sub(r'`(.*?)`', r'\1', text)  # Remove code formatting
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove markdown links, keep text
    
    return text.strip()

def create_combined_pdf(topic_name, news_content, writer_content):
    """Create a combined PDF from both reports"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12
    )
    
    # Story list to hold the content
    story = []
    
    # Add title
    title = f"Newsletter Report: {topic_name}"
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))
    
    # Add News Report section
    if news_content:
        story.append(Paragraph("News Aggregation Report", header_style))
        cleaned_news = clean_text_for_pdf(news_content)
        # Split content into paragraphs
        paragraphs = cleaned_news.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
        story.append(Spacer(1, 20))
    
    # Add Writer Report section
    if writer_content:
        story.append(Paragraph("Newsletter Writing Report", header_style))
        cleaned_writer = clean_text_for_pdf(writer_content)
        # Split content into paragraphs
        paragraphs = cleaned_writer.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), normal_style))
    
    # Build PDF
    try:
        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

class TheCrew:
    """Main crew orchestrator class"""
    
    def __init__(self, topic, model_name):
        self.topic = topic
        self.model_name = model_name

    def run(self):
        """Execute the crew and return results"""
        agents = NewsAgents(self.model_name)
        tasks = NewsTasks()

        news_agent = agents.news_agent()
        writer_agent = agents.writer_agent()

        news_task = tasks.news_task(self.topic, news_agent)
        writer_task = tasks.writer_task(self.topic, writer_agent, news_task)

        crew = Crew(
            agents=[news_agent, writer_agent],
            tasks=[news_task, writer_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff(inputs={"topic": self.topic})
        return result

# Initialize session state to persist data after download
if 'newsletter_generated' not in st.session_state:
    st.session_state.newsletter_generated = False
if 'newsletter_content' not in st.session_state:
    st.session_state.newsletter_content = ""
if 'topic_name' not in st.session_state:
    st.session_state.topic_name = ""
if 'crew_result' not in st.session_state:
    st.session_state.crew_result = None

# ===== STREAMLIT UI =====

# Header
st.header("📅 Weekly :orange-background[News Letter] :orange[AI]gent 🤖", divider="orange")

# Sidebar with configuration
with st.sidebar:
    with st.expander('🤖 App Info', expanded=False):      
        st.write("🤖 AI-Generated Weekly News Letter App: Use AI to get your weekly newsletter about a specific topic.")
        st.caption("💻 Built with: Streamlit, CrewAI, DuckDuckGo, LLM, API for inference.")
        
    # API Key configuration
    st.subheader("🔐 Google API Key", divider="violet")
    GOOGLE_API = st.text_input("Enter your Google API Key", type="password", 
                              help="Get your API key from Google AI Studio")
    api_key_available = bool(GOOGLE_API)
    if not GOOGLE_API:
        st.info("Enter your Google API Key to continue")
        st.stop()
    else:
        # Set the API key as an environment variable for the agents
        os.environ['GOOGLE_API'] = GOOGLE_API
        
        # Test button to display API key (for testing purposes)
        if st.button("🔍 Test API Key", help="Click to display the current API key for testing"):
            # Mask the API key for security (show first 10 and last 10 characters)
            if len(GOOGLE_API) > 20:
                masked_key = GOOGLE_API[:10] + "..." + GOOGLE_API[-10:]
            else:
                masked_key = GOOGLE_API[:5] + "..." if len(GOOGLE_API) > 5 else GOOGLE_API
            
            st.success(f"✅ API Key Set: `{masked_key}`")
            st.info(f"Full API Key: `{GOOGLE_API}`")
            
            # Additional testing info
            st.write("**Environment Variable Check:**")
            env_key = os.environ.get('GOOGLE_API', 'Not set')
            if env_key == GOOGLE_API:
                st.success("✅ Environment variable matches input")
            else:
                st.error("❌ Environment variable mismatch")
                
            st.write(f"**API Key Length:** {len(GOOGLE_API)} characters")
    
    # Model selection
    st.subheader("🤖 LLM Model", divider="violet")
    model_name = st.selectbox(
        "Select Model", 
        ("gemini/gemini-2.0-flash", "gemini/gemini-2.0-flash-lite", 
         "gemini/gemini-2.5-flash-lite", "gemini/gemini-2.5-pro"),
        help="Choose the AI model for content generation"
    )
    st.divider()

# Main input section
topic = st.text_input(
    "📰 Enter Your Topic for the Newsletter:", 
    placeholder="AI, Green Energy, Space Exploration...",
    help="Enter a topic you want to create a newsletter about"
)

# Generate button
if not api_key_available:
    st.stop()

generate_clicked = st.button(
    "💫 Generate Newsletter", 
    use_container_width=True, 
    disabled=not topic,
    help="Click to start generating your AI newsletter"
)

# Main execution logic
if generate_clicked and topic:
    
    # Show progress
    with st.spinner("🤖 AI Agents working on your newsletter..."):
        
        # Agent process container
        with st.status("🤖 **Agents at work...**", state="running", expanded=True) as status:
            
            # Container for agent output
            agent_output = st.container(height=400, border=True)
            
            with agent_output:
                # Capture agent output
                original_stdout = sys.stdout
                sys.stdout = StreamToExpander(st)
                
                try:
                    # Execute the crew
                    the_crew = TheCrew(topic, model_name)
                    result = the_crew.run()
                    
                    # Store in session state
                    st.session_state.crew_result = result
                    st.session_state.topic_name = topic
                    st.session_state.newsletter_generated = True
                    
                finally:
                    # Restore stdout
                    sys.stdout = original_stdout
            
            # Update status
            status.update(
                label=f"✨ Newsletter about '{topic}' generated successfully!",
                state="complete", 
                expanded=False
            )

# Display results if newsletter has been generated
if st.session_state.newsletter_generated:
    result = st.session_state.crew_result
    topic = st.session_state.topic_name
    
    # Display the generated newsletter
    st.subheader(f"📰 {topic} Newsletter 🖋️", anchor=False, divider="grey")
    
    # Newsletter content container
    newsletter_container = st.container(border=True)
    
    with newsletter_container:
        try:
            # Extract and display the newsletter content
            if hasattr(result, 'raw'):
                newsletter_content = result.raw
            elif hasattr(result, 'tasks_output') and result.tasks_output:
                final_task = result.tasks_output[-1]
                if hasattr(final_task, 'raw'):
                    newsletter_content = final_task.raw
                else:
                    newsletter_content = str(final_task)
            else:
                newsletter_content = str(result)
            
            # Store content in session state
            st.session_state.newsletter_content = newsletter_content
            
            # Display the newsletter
            st.markdown(newsletter_content)
            
        except Exception as e:
            st.error(f"Error displaying newsletter: {str(e)}")
            st.code(str(result), language="text")
    
    # Add spacing
    st.divider()
    
    # Final Report Section - Combined view
    st.subheader("📋 Final Complete Report", divider="grey")
    
    final_report_container = st.container(border=True)
    
    with final_report_container:
        st.markdown("### 📄 News Aggregation Report")
        news_content = safe_read_file('report_task_news.md')
        if news_content:
            st.markdown(news_content)
        else:
            st.warning("News report not available")
        
        st.divider()  # Visual separator between reports
        
        st.markdown("### ✍️ Newsletter Writing Report") 
        writer_content = safe_read_file('report_task_writer.md')
        if writer_content:
            st.markdown(writer_content)
        else:
            st.warning("Writer report not available")
    
    # Single PDF Download Section
    st.subheader("📥 Download Complete Report", divider="grey")
    
    # Center the download button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Get both report contents
        news_content = safe_read_file('report_task_news.md')
        writer_content = safe_read_file('report_task_writer.md')
        
        if news_content or writer_content:
            # Create PDF buffer
            pdf_buffer = create_combined_pdf(
                st.session_state.topic_name, 
                news_content, 
                writer_content
            )
            
            if pdf_buffer:
                st.download_button(
                    label="📥 Download Complete Report (PDF)",
                    data=pdf_buffer.getvalue(),
                    file_name=f"complete_report_{st.session_state.topic_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_complete_pdf"
                )
        else:
            st.error("No reports available for download")
    
    # Usage Metrics (if available)
    if hasattr(result, 'token_usage') and result.token_usage:
        with st.expander('📊 Usage Metrics', expanded=False):
            st.json(result.token_usage)

# Show empty state when no topic is entered and nothing generated
elif not topic and not st.session_state.newsletter_generated:
    st.info("👆 Enter a topic above and click 'Generate Newsletter' to create your AI-powered newsletter!")
