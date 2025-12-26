# Job Matching Agent - Usage Guide

This guide will walk you through using the Job Matching Agent step-by-step.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Preparing Your Resume](#preparing-your-resume)
3. [Running Your First Search](#running-your-first-search)
4. [Understanding the Results](#understanding-the-results)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)

## Getting Started

### Installation

1. **Install Python** (if not already installed)
   - Download from https://www.python.org/downloads/
   - Version 3.8 or higher required

2. **Install the Job Matching Agent**
   ```bash
   # Clone or download the repository
   cd Job-crawler

   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **First-time setup**
   ```python
   # Download required NLP data
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   ```

## Preparing Your Resume

### Resume Format

The agent works best with resumes that have:

1. **Clear sections** for:
   - Skills
   - Experience
   - Education
   - Certifications (if applicable)

2. **Explicit skill listings**:
   ```
   SKILLS
   Programming: Python, Java, JavaScript
   Frameworks: TensorFlow, React, Django
   Tools: Docker, Git, AWS
   ```

3. **Quantified experience**:
   ```
   Senior Data Scientist | 2020 - Present (4 years)
   ```

### Supported Formats

- **PDF** (preferred): Better formatting preservation
- **TXT**: Plain text, good for simple resumes

### Example Resume Structure

```
YOUR NAME
Title | Contact Info

SUMMARY
Brief professional summary (2-3 sentences)

SKILLS
Language: Python, Java
Frameworks: TensorFlow, React
Cloud: AWS, Azure

EXPERIENCE
Job Title | Company | 2020 - Present
• Achievement 1
• Achievement 2

EDUCATION
Degree | University | Year
```

## Running Your First Search

### Method 1: Interactive Mode (Recommended for Beginners)

```bash
python main.py --interactive
```

You'll be prompted for:
1. **Resume path**: `/path/to/your/resume.pdf`
2. **Target roles**: `Machine Learning Engineer, Data Scientist`
3. **Location**: `San Francisco` (or press Enter for any)
4. **Remote preference**: `y` or `n`

### Method 2: Command Line

**Basic search:**
```bash
python main.py \
  --resume resume.pdf \
  --roles "Machine Learning Engineer"
```

**With filters:**
```bash
python main.py \
  --resume resume.pdf \
  --roles "Software Engineer,Backend Developer" \
  --location "Remote" \
  --remote \
  --min-score 70 \
  --top-n 10
```

## Understanding the Results

### Output Breakdown

```
[1] Senior Machine Learning Engineer          ← Job #1
    Company: TechCorp                         ← Company name
    Location: San Francisco, CA               ← Job location
    URL: https://...                          ← Application link

    Match Score: 92 / 100                     ← Overall fit score
    Fit Level: Excellent Fit                  ← Category

    Score Breakdown:                          ← Component scores
      • Skill Overlap: 88.5
      • Tool Alignment: 95.0
      • Experience Fit: 100.0
      • Role Alignment: 85.0

    ✓ Top Matching Skills:                    ← Your strengths
      • Python
      • TensorFlow
      • Machine Learning

    ✗ Missing/Weak Areas:                     ← Skills to develop
      • Rust
      • Go
```

### Score Interpretation

| Score Range | Meaning | Action |
|------------|---------|--------|
| 90-100 | Excellent Fit | Apply immediately! |
| 75-89 | Strong Fit | Great opportunity, apply |
| 60-74 | Partial Fit | Review carefully, may require skill development |
| <60 | Weak Fit | Consider passing unless very interested |

### Component Scores Explained

1. **Skill Overlap (40% weight)**
   - Measures how many required skills you have
   - Based on skill taxonomy matching

2. **Tool Alignment (25% weight)**
   - Checks if you've used the specific tools mentioned
   - Includes frameworks, libraries, platforms

3. **Experience Fit (20% weight)**
   - Compares your years of experience to requirements
   - Penalizes significant over/under qualification

4. **Role Alignment (15% weight)**
   - Matches your previous job titles to target role
   - Uses semantic similarity

## Advanced Usage

### Customizing Search Parameters

```bash
python main.py \
  --resume resume.pdf \
  --roles "Data Engineer,Analytics Engineer" \
  --location "New York" \
  --max-jobs 100 \              # Collect more jobs
  --min-score 80 \              # Only show high matches
  --top-n 5 \                   # Limit to top 5
  --output results.json         # Save to file
```

### Using Multiple Target Roles

The agent will search for all specified roles:

```bash
python main.py \
  --resume resume.pdf \
  --roles "Machine Learning Engineer,AI Engineer,Research Scientist,Data Scientist"
```

### Saving Results

**JSON format** (for further processing):
```bash
python main.py --resume resume.pdf --roles "..." --output matches.json --format json
```

**Console format** (for reading):
```bash
python main.py --resume resume.pdf --roles "..." --format console
```

### Programmatic Usage

For integration into other tools:

```python
from src.job_matching_agent import JobMatchingAgent

agent = JobMatchingAgent()

matches = agent.run(
    resume_path="resume.pdf",
    target_roles=["ML Engineer"],
    location="Remote",
    remote=True,
    max_jobs=50,
    min_score=70,
    top_n=10
)

# Process results
for match in matches:
    if match['final_score'] >= 90:
        print(f"Excellent match: {match['job']['title']}")
        # Could automatically send to application tracker
```

## Best Practices

### 1. Resume Optimization

**DO:**
- Use standard section headers (SKILLS, EXPERIENCE, EDUCATION)
- List technologies explicitly
- Include years of experience
- Use industry-standard skill names

**DON'T:**
- Use images or fancy formatting in PDF
- Abbreviate skills without context
- Hide skills in dense paragraphs
- Use non-standard terms

### 2. Search Strategy

**Start Broad:**
```bash
# First pass - get overview
python main.py --resume resume.pdf --roles "Software Engineer" --min-score 60
```

**Then Narrow:**
```bash
# Second pass - focus on best matches
python main.py --resume resume.pdf --roles "Senior Backend Engineer" --min-score 80
```

### 3. Interpreting Missing Skills

Use the "Missing/Weak Areas" to guide learning:

```python
# Run search
matches = agent.run(...)

# Collect all missing skills from top 10 jobs
all_missing = []
for match in matches[:10]:
    all_missing.extend(match['missing_skills'])

# Find most common gaps
from collections import Counter
skill_gaps = Counter(all_missing).most_common(5)
print("Top skills to learn:", skill_gaps)
```

### 4. Regular Searches

Run searches periodically to:
- Track new postings
- Monitor market trends
- Validate skill development

**Automate** (Linux/Mac):
```bash
# Add to crontab for weekly searches
0 9 * * 1 cd /path/to/Job-crawler && python main.py --resume resume.pdf --roles "..." --output weekly_matches.json
```

### 5. Customizing for Your Domain

**Edit skill taxonomy** for your field:

```json
// config/skill_taxonomy.json
{
  "bioinformatics": {
    "BLAST": ["blast", "basic local alignment"],
    "CRISPR": ["crispr", "gene editing"]
  }
}
```

**Adjust scoring weights** for your priorities:

```json
// config/config.json
{
  "matching": {
    "weights": {
      "skill_overlap": 0.60,     // Prioritize skills
      "experience_fit": 0.30,    // Emphasize experience
      "tool_alignment": 0.05,
      "role_alignment": 0.05
    }
  }
}
```

## Troubleshooting

### "No jobs found"

**Causes:**
- Network issues
- Rate limiting by job boards
- Too specific search terms

**Solutions:**
```bash
# Try broader terms
--roles "Engineer" instead of "Senior Staff ML Engineer Level 5"

# Expand location
--location "" instead of specific city

# Check internet connection
ping google.com
```

### "Low scores for all jobs"

**Causes:**
- Resume not optimized
- Searching wrong roles
- Missing key skills

**Solutions:**
1. Review top job descriptions manually
2. Add missing skills to resume (if you have them)
3. Try different role keywords
4. Lower min-score threshold temporarily

### "PDF parsing failed"

**Solutions:**
```bash
# Try converting to text
# Use online PDF to TXT converter
# Or on Linux/Mac:
pdftotext resume.pdf resume.txt
python main.py --resume resume.txt ...
```

## FAQ

**Q: How many jobs should I search?**
A: Start with 30-50 per role. More jobs = longer processing but better coverage.

**Q: Should I apply to all "Excellent Fit" jobs?**
A: Yes! These are your best matches. But also review company culture fit.

**Q: Can I search only specific companies?**
A: Not directly, but you can filter results afterward or extend the crawler.

**Q: How often should I update my resume?**
A: Run a search, review missing skills from top matches, update resume monthly.

**Q: Is my data shared?**
A: No. All processing is local. No data leaves your machine.

## Next Steps

1. **Run your first search** using interactive mode
2. **Analyze the top 5 matches** in detail
3. **Identify skill gaps** and create learning plan
4. **Update resume** with relevant keywords
5. **Re-run search** to see improved matches
6. **Apply to top matches!**

---

For more help, see:
- `README.md` - Full documentation
- `examples/` - Code examples
- GitHub Issues - Report problems

Good luck with your job search! 🎯
