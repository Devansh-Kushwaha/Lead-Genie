
# 🧠 Lead Intelligence Tool

An AI-powered B2B lead generation tool that searches companies by industry and location, gathers verified contact data, news insights, and performs OpenAI-driven analysis to generate pain points, values, service suggestions, and lead scoring.

---

## 📸 Demo & Screenshots

### Demo: 
https://drive.google.com/file/d/1K80V6P05iOsECyHrO-yIvuEEgccZPL_l/view?usp=drive_link

### 🔍 Company Search
<img src="screenshots/Screenshot 2025-07-07 150817.png" width="100%" alt="Company search results"/>

### 🧠 Company Search Result Table
<img src="screenshots/Screenshot 2025-07-07 150924.png" width="100%" alt="Company Search Result Table"/>

### 📰 Company Details
<img src="screenshots/Screenshot 2025-07-07 150949.png" width="100%" alt="Company Details"/>

### 📰 News Pane
<img src="screenshots/Screenshot 2025-07-07 151004.png" width="100%" alt="News Pane"/>

---

## 🗂️ Project Structure

```
SAAS-LEAD-INTEL/
├── api/                  # Django app containing API views and logic
├── frontend/             # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
├── SaaSquatch/           # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── manage.py
└── .env                  # Environment variables for backend
```

---

## 🚀 Features

- 🔍 Company search by industry + location
- 🧠 AI analysis using OpenAI/Groq to extract:
  - Pain Points
  - Core Values
  - Suggested Services
- 📈 Lead scoring with reason
- 📰 News aggregation (GNews)
- 📧 Contact discovery (Hunter.io)
- 🌍 Company enrichment (People Data Labs)

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/saas-lead-intel.git
cd saas-lead-intel
```

---

### 2. Backend Setup (Django)

```bash
# Navigate to root (same directory as manage.py)
cd saas-lead-intel

# Create virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### ⚠️ Configure `.env`

Create a `.env` file in the root directory (same as `manage.py`) with the following:

```
OPENAI_API_KEY=your_openai_key
HUNTER_API_KEY=your_hunter_key
PDL_API_KEY=your_pdl_key
GNEWS_API_KEY=your_gnews_key
```

---

#### Run the backend

```bash
python manage.py migrate
python manage.py runserver
```

Backend running at: `http://127.0.0.1:8000/`

---

### 3. Frontend Setup (React)

```bash
cd frontend
npm install
npm start
```

Frontend running at: `http://localhost:3000/`

---

## 🧪 Sample API Endpoint

```http
GET /api/scrape-companies/?industry=finance&location=united+states
```

Returns enriched company objects with contacts, scores, news, and AI insights.

---

## 📦 Technologies Used

- **Frontend**: React, Axios
- **Backend**: Django REST Framework
- **Database**: MySQL / PostgreSQL
- **APIs**: OpenAI, People Data Labs, Hunter.io, GNews

---

## 🤝 Contributions

Feel free to open issues or pull requests!
