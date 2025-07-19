# 📓 IPYNB Converter and Explainer

A powerful Flask web application that transforms your Jupyter notebooks into beautifully formatted PDFs and provides AI-powered code explanations from multiple models simultaneously.

## ✨ Features

### 🎯 **PDF Conversion**
- **High-Fidelity Rendering**: Convert `.ipynb` files to professional PDFs with pixel-perfect styling
- **Live Preview**: See exactly how your notebook will look before downloading
- **One Dark Theme**: Beautiful syntax highlighting with the popular One Dark color scheme
- **Automatic Cleanup**: Server resources are automatically cleaned up after each conversion

### 🤖 **AI-Powered Code Explanation**
- **Multi-Model Analysis**: Get explanations from multiple AI models simultaneously
- **Asynchronous Processing**: Lightning-fast responses using concurrent API calls
- **Interactive Results**: Tabbed interface to compare explanations side-by-side
- **Secure API Management**: Your OpenRouter API key is safely stored in server sessions

## 🚀 Quick Start

### Prerequisites
```bash
pip install flask nbconvert playwright aiohttp
playwright install chromium
```

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/jupyter-notebook-toolkit.git
cd jupyter-notebook-toolkit

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` and start converting your notebooks!

## 🛠️ How It Works

### PDF Generation Pipeline
1. **Upload**: User selects a Jupyter notebook file
2. **Convert**: `nbconvert` transforms the notebook to HTML
3. **Style**: Custom CSS applies the One Dark theme
4. **Render**: Playwright's headless browser generates a high-quality PDF
5. **Serve**: User downloads the formatted PDF

### AI Explanation Engine
1. **Authentication**: Secure API key management via Flask sessions
2. **Model Selection**: Dynamic fetching of available OpenRouter models
3. **Concurrent Processing**: Asynchronous requests to multiple AI models
4. **Result Aggregation**: Explanations organized by code cell and model
5. **Interactive Display**: Tabbed interface for easy comparison

## 🏗️ Project Structure

```
jupyter-notebook-toolkit/
├── app.py                          
├── templates/
│   ├── index.html                  # PDF converter landing page
│   ├── explain_upload_form.html    # AI explanation interface
│   ├── preview.html                # PDF preview page
│   └── explain.html                # Results display with tabs
├── static/
│   └── css/
│       ├── style.css               # Main application styling
│       ├── onedark.css             # Notebook syntax highlighting
|       └── nav_style.css           # Navigation Bar styling
└── requirements.txt
```

## 🔧 Technical Highlights

- **🚀 Async Performance**: Uses `asyncio` and `aiohttp` for concurrent API calls
- **🔒 Security First**: API keys stored in server-side sessions
- **🎨 Beautiful UI**: Clean, responsive design with modal dialogs and loading states
- **🧹 Resource Management**: Automatic cleanup of temporary files
- **🛡️ Robust Error Handling**: Graceful fallback from async to threaded processing

## ⚡ Performance Features

- **Concurrent AI Requests**: Get explanations from multiple models simultaneously
- **Non-blocking UI**: Asynchronous processing keeps the interface responsive
- **Efficient Resource Usage**: Automatic cleanup prevents server bloat
- **Fast PDF Generation**: Headless browser rendering for optimal speed

## 🔐 Security

- Server-side API key storage (never exposed to client)
- Secure filename handling for uploads
- Session-based authentication management
- Automatic file cleanup after processing

## 🎯 Use Cases

- **📚 Documentation**: Convert notebooks to professional PDFs for sharing
- **🎓 Education**: Generate clean handouts from computational tutorials  
- **📊 Reports**: Create presentation-ready documents from data analysis
- **🧠 Learning**: Understand complex code with AI-powered explanations
- **👥 Code Review**: Get multiple perspectives on notebook implementations

## 🛣️ Roadmap

- **Environment Configuration**: Move to environment-based secrets
- **Testing Suite**: Add comprehensive unit and integration tests
-**JavaScript Modules**: Refactor embedded JS into separate files
- **Batch Processing**: Handle multiple notebooks simultaneously
-**Custom Themes**: Additional PDF styling options

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **🐛 Bug Reports**: Open an issue with detailed reproduction steps
2. **💡 Feature Requests**: Suggest new functionality or improvements
3. **🔧 Code Contributions**: Fork, create a branch, and submit a pull request
4. **📖 Documentation**: Help improve our guides and examples


## 🙏 Acknowledgments

- **nbconvert** for powerful notebook conversion capabilities
- **Playwright** for high-quality PDF rendering
- **OpenRouter** for AI model access and API infrastructure
- **Flask** for the elegant web framework foundation

---

⭐ **Star this repo** if you find it useful! ⭐

**Made with ❤️ for the Jupyter community**
