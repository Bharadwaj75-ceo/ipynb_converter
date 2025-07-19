📓 IPYNB Tools
<div align="center">
[Show Image](https://img.shields.io/badge/python-v3.8+-blue.svg)
[Show Image](https://img.shields.io/badge/flask-web%20framework-green.svg)
[Show Image](https://img.shields.io/badge/license-MIT-blue.svg)
A powerful suite of web-based tools for working with Jupyter Notebooks
Features • Installation • Usage • Tech Stack • Contributing
</div>

🌟 Overview
IPYNB Tools is a comprehensive web application that transforms how you work with Jupyter Notebooks. Whether you need to convert notebooks to beautiful PDFs or get AI-powered explanations of your code, this tool has you covered.
✨ Features
📄 PDF Conversion

Transform .ipynb files into stunning, pageless PDF documents
Beautifully styled with the One Dark theme for enhanced readability
Maintains code formatting and output visualization

🤖 AI Code Explanation

Get intelligent explanations of your code cells powered by multiple AI models
Side-by-side view of original code and AI-generated explanations
Support for various LLMs through the OpenRouter API
Tabbed interface for easy comparison between different model explanations

🔐 Secure API Management

Safe, session-based storage of your OpenRouter API key
No client-side exposure of sensitive credentials
Easy key management through the web interface

🎨 Interactive UI

Intuitive file upload with drag-and-drop support
Model selection modal for customizing your AI experience
Real-time loading indicators and progress feedback
Responsive design that works on all devices


🛠 Technology Stack
ComponentTechnologyBackendShow Image PythonFrontendShow Image Show Image Show ImageConversionnbconvert, playwrightAI Integrationrequests, aiohttp (async API calls)StylingCustom "One Dark" theme

🚀 Installation
Prerequisites

Python 3.8+ installed on your system
pip package manager
An OpenRouter API key (for AI explanations)

Quick Setup

Clone the repository
bashgit clone <repository-url>
cd ipynb-tools

Create and activate virtual environment
bashpython -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate

Install dependencies
bashpip install -r requirements.txt

Install Playwright browsers
bashplaywright install


🔑 API Configuration

Sign up for an OpenRouter account
Obtain your API key from the dashboard
Enter your key directly in the web interface when using AI features


📖 Usage
Starting the Application
bashpython app.py
Then navigate to http://127.0.0.1:5000 in your browser.
📄 Converting Notebooks to PDF

Click "Into PDF" in the navigation bar
Upload your .ipynb file using the drag-and-drop area
Click "Convert & Preview" to see the HTML preview
Download your beautifully formatted PDF

🤖 Getting AI Code Explanations

Navigate to "Explain Code"
Enter and save your OpenRouter API key
Select your preferred AI models using "Add / Manage Models"
Upload your .ipynb file
Click "Explain Code" and wait for the magic ✨
Browse through explanations using the tabbed interface


🎯 Key Benefits

Time-saving: Convert and analyze notebooks with just a few clicks
Multi-model insights: Compare explanations from different AI models
Professional output: Generate publication-ready PDFs
Secure: Your API keys and data stay protected
User-friendly: Intuitive interface suitable for all skill levels


🤝 Contributing
We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.
Development Setup

Fork the repository
Create a feature branch (git checkout -b feature/AmazingFeature)
Commit your changes (git commit -m 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Open a Pull Request


📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments

OpenRouter for providing access to multiple AI models
Jupyter Project for the amazing notebook format
Flask community for the robust web framework
All contributors who help make this project better


<div align="center">
Made with ❤️ for the data science community
⭐ Star this repo if you find it helpful! ⭐
</div>Chat controls Sonnet 4
