# 🚀 LingX EaseBI - Intelligent Data Analysis Platform

<p align="center">
  <img src="frontend/public/logo.png" alt="LingX EaseBI Logo" width="200"/>
</p>

> 🤖 **LingX EaseBI** is an intelligent BI platform powered by Large Language Models (LLM), providing organizations with an all-in-one solution from database management to knowledge base construction. Through AI empowerment, data analysis becomes simpler, more efficient, and smarter.

---

## ✨ Core Features & Advantages

### 🎯 Intelligent Database Management
- Visual operation interface, simplified management process
- AI-driven database structure optimization
- Automated data quality monitoring

### 🧹 Efficient Data Cleaning
- Intelligent data cleaning process
- Automatic detection and repair of abnormal data
- Data consistency checking and assurance

### 📚 Intelligent Knowledge Base
- Automatic vector knowledge base construction based on database structure
- Support for generating sample datasets
- Knowledge graph visualization capabilities

### 🔮 Dataset Management
- Support for multi-format data import and export
- Intelligent annotation and data augmentation features
- Support for incremental updates and version control

### 🛠️ Model Training & Deployment
- One-click model fine-tuning and training
- Flexible adaptation to various business scenarios
- Real-time model performance monitoring

### 🖥️ User-Friendly Interface
- Natural language query support, lowering barriers
- Rich visualization components, enhancing user experience
- Support for embedded data conversation interface

---

## 🚀 Quick Start

Here are the installation steps for frontend and backend.

### Frontend Installation

1. Clone repository
   ```bash
   git clone https://github.com/lingx-ai/lingx-ease-bi.git
   cd lingx-ease-bi/frontend
   ```

2. Install dependencies
   ```bash
   # Using pnpm
   pnpm install

   # Or using yarn
   yarn install

   # Or using npm
   npm install
   ```

3. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env file according to actual needs
   ```

4. Start development server
   ```bash
   pnpm dev  # or yarn dev / npm run dev
   ```

### Backend Installation

1. Navigate to backend directory
   ```bash
   cd backend
   ```

2. Create and activate virtual environment (recommended using `venv` or `conda`)
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   ```

3. Install backend dependencies
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp .env.example .env
   # Modify configurations in .env as needed (e.g., PostgreSQL connection, API keys)
   ```

5. Initialize database
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create superuser for admin access
   ```bash
   python manage.py createsuperuser
   ```

7. Start backend service
   ```bash
   uvicorn backend.asgi:application --workers 4 --reload --host 0.0.0.0 --port 8000 --env-file .env
   ```

---

## 📋 Requirements

Ensure the following environments are ready:

- **Frontend:**
  - Node.js >= 18.0.0
- **Backend:**
  - Python >= 3.10
  - PostgreSQL >= 12
  - Redis >= 6.0

---

## 🛠️ Contribution Guide

Community contributions are welcome! You can participate through:
- Submit [Pull Requests](https://github.com/lingx-ai/lingx-ease-bi/pulls) for new features or improvements
- Report issues: [Issue](https://github.com/lingx-ai/lingx-ease-bi/issues)

Please read our [Contribution Guide](CONTRIBUTING.md) before submitting code.

---

## 📄 License

This project is under the [MIT License](LICENSE).

---

## 🔍 FAQ

### Q1: Encountering errors during model training?
- Ensure training data format meets requirements
- Verify system GPU resources are sufficient
- Check detailed error logs to locate issues

---

## 📞 Contact Us

- 📍 Project Homepage: [GitHub](https://github.com/lingx-ai/lingx-ease-bi)
- 🛠 Issue Feedback: [Issue](https://github.com/lingx-ai/lingx-ease-bi/issues)

---

Made with ❤️ by LingX Team

---