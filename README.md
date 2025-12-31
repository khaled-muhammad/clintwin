# ClinTwin - AI Pharmaceutical Safety System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/FastAPI-0.109-green.svg" alt="FastAPI Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

**ClinTwin** is an AI-powered pharmaceutical safety system designed for resource-limited settings in Egypt. It provides accurate medicine identification and drug interaction checking through three independent modules.

## 🎯 Features

### 1. Pill Akinator (Dynamic MCQ Engine)
- Identifies medicines through **visual memory** - no images needed
- Asks 1-3 intelligent questions about box color, pill shape, text, logos
- Uses **information gain** to select optimal questions
- **Free LLM integration** via Hack Club AI (qwen/qwen3-32b)
- Achieves **>90% confidence** in ~3 questions

### 2. Image Identifier (Visual Recognition)
- **CNN + OCR** for medicine identification from photos
- Supports multiple image types: pill, box, strip, bottle, syrup
- **Bilingual OCR**: English + Arabic text extraction
- Returns full medicine info: name, dosage, warnings, side effects
- **<200ms inference** with lightweight model

### 3. Drug Interaction Checker
- Checks for harmful **drug-drug interactions**
- Supports **drug class interactions** (e.g., all NSAIDs)
- Four severity levels: Contraindicated, Major, Moderate, Minor
- Provides **safe alternatives** when interactions found
- High sensitivity for critical interactions

---

## 📁 Project Structure

```
clintwin/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── models/              # Pydantic models
│   │   │   ├── medicine.py      # Medicine & MCQ models
│   │   │   └── interaction.py   # Interaction models
│   │   ├── services/            # Business logic
│   │   │   ├── pill_akinator.py # MCQ-based identification
│   │   │   ├── image_identifier.py # CNN + OCR
│   │   │   └── interaction_checker.py # Drug interactions
│   │   ├── routes/              # API endpoints
│   │   │   ├── akinator.py
│   │   │   ├── image.py
│   │   │   └── interactions.py
│   │   └── data/                # JSON databases
│   │       ├── medicines.json   # Medicine database
│   │       └── interactions.json # Interaction rules
│   ├── ml_models/               # CNN models (optional)
│   └── requirements.txt
├── frontend/
│   ├── index.html               # Main HTML
│   ├── css/
│   │   └── styles.css           # Stylesheets
│   └── js/
│       ├── app.js               # Main app logic
│       ├── akinator.js          # Pill Akinator module
│       ├── image-identifier.js  # Image module
│       └── interaction-checker.js # Interactions module
├── demo_images/                 # Sample images
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone or navigate to the project:**
```bash
cd clintwin
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

4. **Set up environment variables (optional):**
Create a `.env` file in `backend/` directory:
```env
# LLM Provider: "hackclub" (free!), "mock", "openai", or "anthropic"
LLM_PROVIDER=hackclub

# Hack Club AI (FREE - recommended!)
# Uses https://ai.hackclub.com/proxy/v1/chat/completions
HACKCLUB_MODEL=qwen/qwen3-32b

# Server settings
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### Running the Application

1. **Start the backend server:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python -m app.main
```

2. **Open the frontend:**
- Open `frontend/index.html` in your browser
- Or use a local server:
```bash
cd frontend
python -m http.server 3000
```
Then visit: http://localhost:3000

3. **API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Pill Akinator
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/akinator/start` | Start new session |
| POST | `/api/akinator/answer` | Submit answer |
| GET | `/api/akinator/session/{id}` | Get session status |
| DELETE | `/api/akinator/session/{id}` | End session |

### Image Identifier
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/image/upload` | Upload image for ID |
| POST | `/api/image/identify-base64` | Base64 image ID |
| POST | `/api/image/extract` | Extract text only |
| GET | `/api/image/formats` | Supported formats |

### Drug Interactions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interactions/check` | Check interactions |
| GET | `/api/interactions/medicine/{id}/interactions` | Single drug interactions |
| GET | `/api/interactions/medicines` | List all medicines |
| GET | `/api/interactions/medicines/search?q=` | Search medicines |

---

## 🧠 AI Logic Explained

### Pill Akinator - Information Gain Algorithm

The Akinator uses **information theory** to select questions:

```python
# Information Gain = Entropy(before) - Entropy(after)
# Best question splits candidates closest to 50/50

def calculate_information_gain(candidates, attribute):
    # Count how many have True vs False for this attribute
    true_count = sum(1 for m in candidates if m[attribute])
    false_count = len(candidates) - true_count
    
    # Higher gain = more balanced split = better question
    if true_count == 0 or false_count == 0:
        return 0  # No information gain
    
    # Calculate entropy reduction
    entropy_before = log2(len(candidates))
    entropy_after = weighted_average_entropy(true_count, false_count)
    
    return entropy_before - entropy_after
```

### Image Identifier - CNN + OCR Pipeline

```
Image Input → Preprocessing → CNN Inference → OCR Extraction → Text Matching → Fusion → Results
     ↓              ↓              ↓                ↓               ↓           ↓
  Resize       Normalize      Classify       Extract text      Match to DB   Combine
 224x224       [0,1]         Softmax        EN + AR          Fuzzy match   confidence
```

### Drug Interaction Checker - Multi-level Matching

1. **Direct Match**: Check if specific drug pair has known interaction
2. **Group Match**: Check drug class interactions (NSAIDs, beta-blockers, etc.)
3. **Severity Assessment**: Rank by clinical significance
4. **Alternative Finding**: Suggest safer substitutes

---

## 📊 Sample JSON Outputs

### MCQ Question (Pill Akinator)
```json
{
    "question_id": "q1_abc123",
    "question_text": "What is the main color of the medicine box?",
    "options": ["Red", "Blue", "White", "Green", "Not sure"],
    "field_target": "box_primary_color",
    "confidence_before": 0.0,
    "confidence_after_expected": 0.35
}
```

### Interaction Check Result
```json
{
    "success": true,
    "medicines_checked": ["Brufen 400", "Cataflam 50"],
    "interactions_found": [{
        "severity": "major",
        "drugs_involved": ["NSAIDs", "NSAIDs"],
        "description": "Using multiple NSAIDs increases bleeding risk"
    }],
    "risk_level": "high",
    "summary": "🔴 HIGH RISK: Major interaction found...",
    "safe_alternatives": [{
        "for_medicine": "Brufen 400",
        "alternative": {"name": "Panadol Extra"},
        "reason": "Non-NSAID pain relief"
    }]
}
```

---

## 🔧 Configuration Options

### LLM Provider
Set `LLM_PROVIDER` in `.env`:
- `hackclub` - **Recommended!** Free Hack Club AI (qwen/qwen3-32b)
- `mock` - Use template questions (fully offline, demo mode)
- `openai` - Use GPT-4 for dynamic questions (requires API key)
- `anthropic` - Use Claude for dynamic questions (requires API key)

### Hack Club AI (Default)
ClinTwin uses the **free Hack Club AI API** by default:
- Endpoint: `https://ai.hackclub.com/proxy/v1/chat/completions`
- Model: `qwen/qwen3-32b` (powerful, free!)
- No API key required for basic usage
- OpenAI-compatible format

### Confidence Thresholds
In `config.py`:
```python
AKINATOR_MAX_QUESTIONS = 3      # Max MCQs before guess
AKINATOR_CONFIDENCE_THRESHOLD = 0.90  # Stop when reached
CNN_CONFIDENCE_THRESHOLD = 0.7  # Min confidence for CNN match
```

---

## 🔒 Security Notes

- API keys should be stored in environment variables, never committed
- CORS is configured for development; restrict in production
- Input validation on all endpoints
- File size limits for image uploads (10MB)

---

## 📱 Demo Data

The project includes:
- **16 sample medicines** with full visual attributes
- **15 interaction rules** covering major drug classes
- Supports offline demo mode without external APIs

### Sample Medicines
- Panadol Extra, Brufen 400, Augmentin 1g
- Cataflam 50, Flagyl 500, Antinal
- Concor 5, Lipitor 20, Nexium 40
- And more...

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is for educational purposes. 

**Disclaimer:** This is a demo system. Always consult healthcare professionals for medical decisions.

---

## 📞 Support

For questions or issues:
- Open a GitHub issue
- Contact the development team

---

## 🙏 Acknowledgments

- **Hack Club AI** for providing free LLM API access
- Medicine data adapted from Egyptian pharmaceutical sources
- Interaction rules based on clinical guidelines
- UI design inspired by modern healthcare applications

---

Made with ❤️ for ISEF 2024
# clintwin
