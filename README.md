# EmotiBot - AI-Powered Emotional Conversation Companion

EmotiBot is an intelligent conversational AI that can understand emotions, process speech, and provide empathetic responses through text and voice interactions.

## Features

- **Emotion Detection**: Analyzes text input to detect emotional states
- **Speech Processing**: Convert speech to text and text to speech
- **RAG System**: Retrieval-Augmented Generation for contextual responses
- **Document Processing**: Handle PDF and DOCX documents
- **Real-time Chat**: Interactive conversation interface
- **Voice Interaction**: Speech input and output capabilities

## Deployment

### Deploy on Streamlit Cloud

1. **Fork or use this repository** on GitHub
2. **Go to [Streamlit Cloud](https://share.streamlit.io/)**
3. **Sign in** with your GitHub account
4. **Click "New app"**
5. **Select your repository**: `vanshikaxcx/emotibot`
6. **Set main file path**: `streamlit_app.py`
7. **Add secrets** in the Streamlit Cloud dashboard:
   ```
   GOOGLE_API_KEY = "your_google_api_key"
   OPENAI_API_KEY = "your_openai_api_key"
   SUPABASE_URL = "your_supabase_url"
   SUPABASE_KEY = "your_supabase_key"
   ```
8. **Click "Deploy"**

Your app will be available at: `https://your-app-name.streamlit.app`

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/vanshikaxcx/emotibot.git
cd emotibot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
streamlit run streamlit_app.py
```

## Configuration

Add your API keys to the `.env` file:
- `GOOGLE_API_KEY`: For Google Generative AI
- `OPENAI_API_KEY`: For OpenAI services
- `SUPABASE_URL`: For Supabase database
- `SUPABASE_KEY`: For Supabase authentication

## Usage

1. Launch the Streamlit app
2. Choose interaction mode (text or voice)
3. Start conversing with EmotiBot
4. View emotion analysis and responses

## Technologies Used

- **Streamlit**: Web interface
- **Google Generative AI**: LLM for responses
- **OpenAI Whisper**: Speech recognition
- **LangChain**: LLM framework
- **Supabase**: Database and storage
- **TextBlob**: Sentiment analysis

## License

This project is licensed under the MIT License.
