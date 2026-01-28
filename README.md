# CETac - Computational Educational Technology for Acquisition of Content

**AI-Powered Hebrew Learning Platform for Schools**

## Overview

CETac is a production-grade educational platform that generates personalized Hebrew learning activities using Google Cloud's Vertex AI (Gemini). Built with a modular, configuration-driven prompt engineering system, it allows educators to customize every aspect of content generation without touching code.

## Key Features

- 🎯 **CEFR-Aligned Content**: Automatically generates activities for levels A1-B1 (expandable to C1)
- 🧩 **Modular Prompt System**: All linguistic constraints and pedagogical rules in versioned JSON configs
- 🔒 **Multi-Tenant Architecture**: Secure isolation for multiple schools
- ♿ **Accessibility First**: Dyslexia-friendly fonts, WCAG 2.1 AA compliant
- 📊 **Admin Dashboard**: Manage prompts, monitor usage, A/B test teaching strategies
- ☁️ **Serverless**: Firebase Cloud Functions Gen 2 for infinite scalability

## Project Structure

```
cet/
├── backend/                 # Python backend (Firebase Functions)
│   ├── config/             # Settings and prompt configurations
│   │   ├── prompts/        # CEFR-level prompt configs (JSON)
│   │   │   ├── a1/         # A1 Beginner configs
│   │   │   ├── a2/         # A2 Elementary configs
│   │   │   ├── b1/         # B1 Intermediate configs
│   │   │   └── shared/     # Shared resources (vocab lists, rules)
│   │   └── schemas/        # JSON schemas for validation
│   ├── services/           # Core business logic
│   ├── models/             # Pydantic data models
│   ├── middleware/         # Auth, rate limiting, CORS
│   └── api/                # API route handlers
├── frontend/               # React frontend
│   └── src/
│       ├── components/     # UI components
│       └── services/       # API client
├── admin_portal/           # Admin dashboard (React)
├── tests/                  # Comprehensive test suite
│   ├── unit/
│   ├── integration/
│   └── linguistic/         # Hebrew quality validation
└── docs/                   # Documentation

```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account with billing enabled
- Firebase project

### Initial Setup

1. **Clone and navigate**:
   ```bash
   cd /Users/avirammizrahi/Desktop/cet
   ```

2. **Backend setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

3. **Configure GCP**:
   ```bash
   # Set up authentication
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   
   # Grant Vertex AI permissions (see docs/deployment.md)
   ./scripts/setup_permissions.sh
   ```

4. **Frontend setup**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

### Development

**Run backend locally**:
```bash
cd backend
firebase emulators:start
```

**Run tests**:
```bash
pytest tests/ -v --cov
```

## Modular Prompt Engineering

### How It Works

All prompt logic is stored in JSON configuration files under `backend/config/prompts/`. Each CEFR level has its own config defining:

- **Morphological Constraints**: Allowed tenses, verb patterns (binyanim), sentence length
- **System Prompt Template**: Jinja2 template with pedagogical instructions
- **Vocabulary Whitelists**: Approved word lists for the level
- **Few-Shot Examples**: Sample activities for model context
- **Bloom Taxonomy Rules**: Distribution of question cognitive levels

### Example: Modifying A1 Constraints

Edit `backend/config/prompts/a1/default.json`:

```json
{
  "morphological_constraints": {
    "allowed_tenses": ["PRESENT"],  // Only present tense
    "allowed_binyanim": ["PAAL"],   // Only simplest verb pattern
    "max_sentence_length": 10,      // Max 10 words per sentence
    "niqqud_required": true         // Full vowel marks required
  }
}
```

Changes take effect immediately—no code deployment needed!

### Versioning & Rollback

```bash
# Create new version
cp prompts/a1/default.json prompts/versions/a1_default_v1.1.0.json

# Rollback via admin portal or API
curl -X POST https://your-api.com/admin/prompts/a1/rollback \
  -d '{"version": "1.0.0"}'
```

## Deployment

Detailed instructions in [`docs/deployment.md`](docs/deployment.md).

**Quick deploy**:
```bash
# Deploy functions
firebase deploy --only functions

# Deploy frontend
firebase deploy --only hosting
```

## Architecture

- **Frontend**: React + Tailwind CSS
- **Backend**: Python 3.11 + Firebase Functions Gen 2
- **AI Engine**: Google Vertex AI (Gemini 1.5 Flash/Pro)
- **Database**: Cloud Firestore (NoSQL)
- **Auth**: Firebase Authentication
- **Monitoring**: Google Cloud Logging + Sentry

See [`docs/architecture.md`](../../../.gemini/antigravity/brain/239462f5-147e-4c03-9423-8a8ae0c569a4/architecture.md) for diagrams.

## Cost Estimation

For 100 students, 5 activities/week:
- Cloud Functions: ~$5/month
- Vertex AI: ~$25/month
- Firestore: ~$2/month
- **Total**: ~$32/month

Caching can reduce costs by 40-60%.

## Testing

```bash
# Unit tests
pytest tests/unit/

# Integration tests (requires GCP credentials)
pytest tests/integration/

# Hebrew linguistic quality tests
pytest tests/linguistic/

# Load testing
locust -f tests/load/locustfile.py
```

## Security & Compliance

- ✅ COPPA/FERPA compliant (no PII storage)
- ✅ Multi-tenant data isolation
- ✅ Firebase Authentication with custom claims
- ✅ Rate limiting and abuse prevention
- ✅ Firestore security rules

## Contributing

1. Create feature branch
2. Write tests (target >90% coverage)
3. Ensure linguistic validation passes
4. Submit PR

## License

Proprietary - CETac Educational Platform

## Support

- Technical Documentation: `docs/`
- Teacher Guide: `docs/teacher_guide.md`
- API Docs: `docs/api.md`

---

**Built with ❤️ for Hebrew education**
