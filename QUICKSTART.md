# 🚀 Quick Start - 2 Minutes to Your First Job Search

## Option 1: One-Line Install & Run (Recommended)

```bash
# Clone, setup, and run
cd Job-crawler
bash setup.sh
source venv/bin/activate
python run_my_search.py
```

**That's it!** The system will:
- ✅ Search for MLOps, DevOps, Cloud, and ML Engineer roles
- ✅ Focus on remote positions
- ✅ Show you the top 20 matches
- ✅ Analyze your skill gaps
- ✅ Save results to `my_job_matches.json`

## Option 2: Quick Search (If Already Installed)

```bash
cd Job-crawler
source venv/bin/activate  # If not already activated
python run_my_search.py
```

## Option 3: Custom Search

```bash
# Search specific roles
python main.py --resume my_resume.txt --roles "MLOps Engineer,DevOps Engineer" --remote

# On-site only in Boston
python main.py --resume my_resume.txt --roles "ML Engineer" --location "Boston, MA"

# High-match jobs only (90+)
python main.py --resume my_resume.txt --roles "AI Engineer" --min-score 90
```

## What You'll Get

```
[1] MLOps Engineer
    Company: TechCorp
    Location: Remote
    Match Score: 87 / 100
    Fit Level: Strong Fit

    ✓ Top Matching Skills:
      • Python
      • PyTorch
      • AWS
      • CI/CD

    ✗ Missing/Weak Areas:
      • Kubernetes
      • Terraform
```

## Your Results

After running, you'll have:

1. **Console output**: Color-coded, easy to read
2. **my_job_matches.json**: All details for further processing
3. **Skill gap analysis**: What to learn next
4. **Company insights**: Which companies match your profile

## Next Steps

1. ✅ Run the search (2 minutes)
2. 📋 Review top matches (10 minutes)
3. 📝 Apply to 85+ scores immediately
4. 📚 Note missing skills for learning
5. 🔄 Re-run weekly for new postings

## Need Help?

- **Full guide**: `README_BHARGAV.md` (personalized for you)
- **Detailed docs**: `README.md`
- **Step-by-step**: `USAGE_GUIDE.md`

## Pro Tips

💡 **First time?** Just run `python run_my_search.py` and see what happens!

💡 **Every week**: Run the search again to catch new postings

💡 **Update resume**: Add missing skills you actually have, then re-run

💡 **Focus**: Apply to 85+ matches first, they're your best bets

---

**Time investment:** 2 min setup + 5 min review = 7 minutes to find your next job! ⚡
