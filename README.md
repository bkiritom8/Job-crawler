# Job Matching Agent 🤖

An intelligent AI-powered job matching system that crawls job postings, analyzes your resume, and ranks opportunities by fit using advanced semantic matching.

## Features

### 🎯 Core Capabilities
- **Resume Parsing**: Extract structured data from PDF and text resumes
- **Multi-Source Job Crawling**: Collect jobs from Indeed, LinkedIn, and other boards
- **Semantic Matching**: Use transformer-based embeddings for deep similarity analysis
- **Skill Normalization**: Handle synonyms and variations (e.g., "ML" ≈ "Machine Learning")
- **Intelligent Scoring**: Comprehensive 0-100 match scores with detailed breakdowns
- **Gap Analysis**: Identify missing skills and areas for improvement

### 📊 Matching Methodology
- **40%** - Skill Overlap
- **25%** - Tool/Technology Alignment
- **20%** - Experience Level Fit
- **15%** - Role Alignment
- **Bonus** - Semantic similarity analysis

### 🎓 Score Ranges
- **90-100**: Excellent Fit (Apply immediately!)
- **75-89**: Strong Fit (Great opportunity)
- **60-74**: Partial Fit (Consider carefully)
- **<60**: Weak Fit (May not be ideal)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- 4GB RAM minimum (for ML models)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/Job-crawler.git
cd Job-crawler
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data** (first run only)
```python
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env with your preferences
```

## Quick Start

### Interactive Mode (Easiest)

```bash
python main.py --interactive
```

Follow the prompts to enter:
- Path to your resume
- Target job roles
- Location preferences
- Remote work preference

### Command Line Mode

**Basic search:**
```bash
python main.py --resume resume.pdf --roles "Machine Learning Engineer,Data Scientist"
```

**Remote jobs only:**
```bash
python main.py --resume resume.pdf --roles "Software Engineer" --remote
```

**Specific location:**
```bash
python main.py --resume resume.pdf --roles "Backend Developer" --location "San Francisco"
```

**Save results to file:**
```bash
python main.py --resume resume.pdf --roles "Data Engineer" --output results.json
```

**Full example with all options:**
```bash
python main.py \
  --resume my_resume.pdf \
  --roles "Senior ML Engineer,AI Researcher" \
  --location "Remote" \
  --remote \
  --max-jobs 50 \
  --min-score 70 \
  --top-n 10 \
  --output matches.json
```

## Programmatic Usage

### Simple Example

```python
from src.job_matching_agent import JobMatchingAgent

# Initialize agent
agent = JobMatchingAgent(config_path="config/config.json")

# Run matching
matches = agent.run(
    resume_path="resume.pdf",
    target_roles=["Machine Learning Engineer", "Data Scientist"],
    location="San Francisco",
    remote=False,
    max_jobs=30,
    min_score=60,
    top_n=10
)

# Display results
agent.display_results(matches)

# Save to file
agent.save_results(matches, "job_matches.json")
```

### Advanced Example

```python
from src.resume_parser import ResumeParser
from src.job_crawler import JobCrawler
from src.skill_normalizer import SkillNormalizer
from src.matching_engine import MatchingEngine
import json

# Load configurations
with open("config/config.json") as f:
    config = json.load(f)

with open("config/skill_taxonomy.json") as f:
    taxonomy = json.load(f)

# Initialize components
resume_parser = ResumeParser(skill_taxonomy=taxonomy)
job_crawler = JobCrawler(config=config)
skill_normalizer = SkillNormalizer(taxonomy=taxonomy)
matching_engine = MatchingEngine(model_name="all-MiniLM-L6-v2")

# Parse resume
resume_data = resume_parser.parse("resume.pdf")

# Crawl jobs
jobs = job_crawler.search(
    query="Senior ML Engineer",
    location="Remote",
    remote=True,
    max_results_per_source=20
)

# Match jobs
job_dicts = [job.to_dict() for job in jobs]
matches = matching_engine.batch_match(
    resume_data=resume_data,
    job_postings=job_dicts,
    skill_normalizer=skill_normalizer
)

# Analyze results
for match in matches[:5]:
    print(f"{match['job']['title']}: {match['final_score']}")
```

## Configuration

### Main Configuration (`config/config.json`)

```json
{
  "job_sources": {
    "linkedin": {"enabled": true, "max_results": 50},
    "indeed": {"enabled": true, "max_results": 50}
  },
  "matching": {
    "weights": {
      "skill_overlap": 0.40,
      "tool_alignment": 0.25,
      "experience_fit": 0.20,
      "role_alignment": 0.15
    },
    "penalties": {
      "missing_core_requirement": 15,
      "seniority_mismatch": 10
    }
  },
  "semantic_model": "all-MiniLM-L6-v2"
}
```

### Skill Taxonomy (`config/skill_taxonomy.json`)

The skill taxonomy maps canonical skill names to their synonyms:

```json
{
  "programming_languages": {
    "Python": ["python", "py", "python3"],
    "JavaScript": ["javascript", "js", "ecmascript"]
  },
  "frameworks_libraries": {
    "TensorFlow": ["tensorflow", "tf"],
    "React": ["react", "reactjs"]
  }
}
```

You can extend this taxonomy with your domain-specific skills.

## Output Format

### Console Output

```
[1] Senior Machine Learning Engineer
    Company: TechCorp
    Location: San Francisco, CA
    URL: https://...

    Match Score: 92 / 100
    Fit Level: Excellent Fit

    Score Breakdown:
      • Skill Overlap: 88.5
      • Tool Alignment: 95.0
      • Experience Fit: 100.0
      • Role Alignment: 85.0

    ✓ Top Matching Skills:
      • Python
      • TensorFlow
      • Machine Learning
      • AWS
      • Docker

    ✗ Missing/Weak Areas:
      • Rust
      • Go
```

### JSON Output

```json
[
  {
    "job_title": "Senior Machine Learning Engineer",
    "company": "TechCorp",
    "location": "San Francisco, CA",
    "url": "https://...",
    "match_score": 92,
    "recommendation": "Excellent Fit",
    "component_scores": {
      "skill_overlap": 88.5,
      "tool_alignment": 95.0,
      "experience_fit": 100.0,
      "role_alignment": 85.0
    },
    "matching_skills": ["Python", "TensorFlow", "..."],
    "missing_skills": ["Rust", "Go"]
  }
]
```

## Architecture

```
Job-crawler/
├── src/
│   ├── resume_parser.py         # PDF/text resume parsing
│   ├── job_crawler.py           # Multi-source job crawling
│   ├── skill_normalizer.py      # Skill taxonomy & normalization
│   ├── matching_engine.py       # Semantic matching & scoring
│   └── job_matching_agent.py    # Main orchestrator
├── config/
│   ├── config.json              # Main configuration
│   └── skill_taxonomy.json      # Skill synonyms mapping
├── examples/
│   ├── simple_example.py        # Basic usage
│   ├── advanced_example.py      # Advanced usage
│   └── sample_resume.txt        # Sample resume
├── main.py                       # CLI entry point
└── requirements.txt              # Dependencies
```

## How It Works

1. **Resume Parsing**
   - Extracts text from PDF/TXT files
   - Identifies skills, experience, education, certifications
   - Normalizes and categorizes information

2. **Job Crawling**
   - Searches multiple job boards (Indeed, LinkedIn, etc.)
   - Extracts job details, requirements, descriptions
   - Handles rate limiting and errors gracefully

3. **Skill Normalization**
   - Maps synonyms to canonical names (SQL = T-SQL = Structured Query Language)
   - Categorizes skills by type (languages, frameworks, tools)
   - Enables accurate skill matching

4. **Semantic Matching**
   - Compares resume to job descriptions using transformer embeddings
   - Calculates skill overlap, tool alignment, experience fit
   - Applies penalties for missing core requirements
   - Generates 0-100 match score

5. **Ranking & Output**
   - Sorts jobs by match score
   - Filters by minimum threshold
   - Displays top N results with detailed breakdowns

## Customization

### Add New Job Sources

```python
from src.job_crawler import BaseCrawler, JobPosting

class MyJobBoardCrawler(BaseCrawler):
    def search(self, query, location, remote, max_results):
        # Implement crawling logic
        jobs = []
        # ... fetch jobs ...
        return jobs

# Register in job_crawler.py
self.crawlers['myboard'] = MyJobBoardCrawler()
```

### Customize Scoring Weights

Edit `config/config.json`:

```json
{
  "matching": {
    "weights": {
      "skill_overlap": 0.50,      // Increase skill importance
      "tool_alignment": 0.30,
      "experience_fit": 0.10,
      "role_alignment": 0.10
    }
  }
}
```

### Add Domain-Specific Skills

Edit `config/skill_taxonomy.json`:

```json
{
  "domain_skills": {
    "Bioinformatics": ["bioinformatics", "computational biology"],
    "Genomics": ["genomics", "gene sequencing"]
  }
}
```

## Troubleshooting

### Common Issues

**Issue: PDF parsing fails**
```
Solution: Install additional dependencies
pip install pdfplumber PyPDF2
```

**Issue: Slow model loading**
```
Solution: Model downloads ~100MB on first run. Subsequent runs are fast.
```

**Issue: No jobs found**
```
Solution:
- Check internet connection
- Job boards may have rate limiting (wait and retry)
- Try broader search terms
```

**Issue: Low match scores for all jobs**
```
Solution:
- Ensure resume has clear skills section
- Add more technical keywords to resume
- Adjust min_score threshold lower
```

## Limitations

- **Web Scraping**: Job boards may change HTML structure, breaking crawlers
- **Rate Limiting**: Aggressive crawling may trigger rate limits
- **Semantic Model**: Requires ~500MB disk space and decent CPU/RAM
- **Resume Format**: Works best with structured resumes (clear sections)
- **Coverage**: Not all job boards supported (focus on major ones)

## Future Enhancements

- [ ] Support for more job boards (Glassdoor, Monster, etc.)
- [ ] Advanced NLP for better requirement extraction
- [ ] Email notifications for new matching jobs
- [ ] Web dashboard for visualization
- [ ] Integration with job application tracking
- [ ] Cover letter generation based on match analysis

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Sentence Transformers for semantic embeddings
- BeautifulSoup for web scraping
- PyPDF2/pdfplumber for PDF parsing
- scikit-learn for ML utilities

## Support

For issues, questions, or feature requests:
- Open a GitHub issue
- Check existing documentation
- Review example scripts

---

**Built with ❤️ for job seekers everywhere**

Happy job hunting! 🚀
