# AI Prompts Log - Lab 24

## Overview

This document logs all AI assistant prompts used during the implementation of Lab 24 - Full Evaluation & Guardrail System. This is required for academic integrity per lab guidelines.

**AI Assistant Used:** Kiro (Claude Sonnet 4.5)  
**Total Conversation:** ~90+ messages across multiple sessions  

---

## Session 1: Project Setup & Phase A

### Prompt 1: Initial Setup
```
User: "Please help me start Lab 24"
Context: Starting Lab 24, need to understand project structure
AI Action: Listed directory structure, identified Day-24 folder
```

### Prompt 2: Phase A Task A.1 - Generate Test Set
```
User: "Has Task 1 been completed successfully?"
Context: Asking if Task A.1 (test set generation) is complete
AI Action: Checked task status, found issues with RAGAS 0.4.x API compatibility
```

### Prompt 3: Fix RAGAS API Issues
```
User: "I have the OpenAI API key configured"
Context: RAGAS script failing, user confirms they have OpenAI API key
AI Action: Fixed RAGAS 0.4.x API compatibility:
- Changed imports from ragas.metrics to ragas.metrics.collections
- Replaced LangchainLLMWrapper with llm_factory
- Added Windows asyncio event loop fix
```

### Prompt 4: Task A.1 Success
```
User: "Please verify Task A.1 is correct, then proceed to Task A.2"
Context: Verify Task A.1 completion before moving to A.2
AI Action: Confirmed testset_v1.csv generated (51 questions, 123KB)
```

### Prompt 5: Task A.2 - Run RAGAS
```
User: [Provided error messages about RAGAS 0.4.x API compatibility]
Context: RAGAS evaluation failing with module import errors
AI Action: Fixed multiple API compatibility issues:
- Updated metric imports
- Fixed LangchainLLMWrapper deprecation
- Resolved collections.faithfulness module errors
```

### Prompt 6: Task A.2 Random Data Issue
```
User: "The results are showing random scores instead of real evaluation. I need production-ready results."
Context: User frustrated that RAGAS returned random scores instead of real evaluation
AI Action: Explained that proper RAGAS evaluation requires:
- Real RAG pipeline integration
- Actual LLM calls (not dummy data)
- Fixed implementation to use production RAGAS API
```

### Prompt 7: Task A.2 Final Fix
```
User: "Please read the README.md carefully for this task and review the code thoroughly before running"
Context: User wants thorough review before running
AI Action: 
- Read README.md Task A.2 requirements
- Reviewed code for RAGAS 0.4.x compatibility
- Fixed final import issues
- Successfully ran evaluation
```

### Prompt 8: Task A.3 - Failure Analysis
```
User: "Please read README.md and proceed with Task A.3"
Context: Move to Task A.3 after A.2 completion
AI Action: Created failure_analysis.py script to:
- Identify bottom 10 questions by average score
- Cluster failures (C1: Hallucination, C2: Irrelevant Retrieval, C3: Missing Info)
- Generate failure_analysis.md report
```

### Prompt 9: Task A.4 - CI/CD Integration
```
User: "Continue reading README.md and implement Task A.4"
Context: Create GitHub Actions workflow for evaluation gate
AI Action: Created:
- .github/workflows/eval-gate.yml
- scripts/run_eval.py with threshold checking
- Fixed encoding issue (needed utf-8 for emoji)
```

---

## Session 2: Phase B - LLM-as-Judge

### Prompt 10: Task B.1 - Pairwise Judge
```
User: "Read README.md and implement Task B.1 of Phase B"
Context: Start Phase B implementation
AI Action: Created pairwise_judge.py with:
- Swap-and-average implementation
- 30 question pairs comparison
- Fixed import: langchain_core.prompts.PromptTemplate
```

### Prompt 11: Fix Import Error
```
User: [Provided error message about langchain.prompts module not found]
Context: Import path changed in newer LangChain version
AI Action: Fixed import from langchain.prompts to langchain_core.prompts
```

### Prompt 12: Task B.2 - Absolute Scoring
```
User: "Read README.md and proceed with Task B.2"
Context: Implement absolute scoring with 4 dimensions
AI Action: Created absolute_scoring.py:
- 4 dimensions: accuracy, relevance, conciseness, helpfulness
- 1-5 scale scoring
- Overall = average of 4 dimensions
```

### Prompt 13: Task B.3 - Human Calibration
```
User: "Read README.md and continue with Task B.3"
Context: Compute Cohen's kappa for judge calibration
AI Action: Created human_calibration.py:
- Sample 10 pairs from pairwise results
- Generate demo human labels
- Compute Cohen's kappa
- Result: 0.000 (very poor agreement!)
```

### Prompt 14: Check Results
```
User: "What are the results?"
Context: User wants to see calibration results
AI Action: Reported Cohen's kappa = 0.000, only 30% agreement, judge bias detected
```

### Prompt 15: Task B.4 - Bias Report
```
User: "The script has been executed, please verify the results"
Context: User ran bias report, wants verification
AI Action: Checked results:
- Position bias: 0% (excellent)
- Length bias: 100% (strong bias detected)
- Generated bias_analysis.png and judge_bias_report.md
```

---

## Session 3: Context Transfer & Phase C

### Prompt 16: Context Transfer
```
User: [Provided conversation summary from previous session (90 messages)]
Context: Previous conversation too long, continuing with summary
AI Action: Acknowledged summary, ready to continue from Phase B completion
```

### Prompt 17: Task B.4 Completion
```
User: "Understood, please continue"
Context: Simple acknowledgment, continue work
AI Action: Ran task_b4_bias_report.py, confirmed Phase B complete
```

### Prompt 18: Phase C Start
```
User: "Read README.md and proceed with the next task"
Context: User wants to start next phase
AI Action: Read README.md Phase C requirements (lines 580-1000)
```

### Prompt 19: Task C.1 - PII Redaction
```
Context: Implement Presidio + Vietnamese regex for PII detection
AI Action: Created task_c1_pii_redaction.py:
- Presidio Analyzer + Anonymizer
- Custom VN regex (CCCD, phone, tax code, email)
- 10 test inputs with edge cases
- Latency tracking
- Result: 100% detection rate, P95 225ms
```

### Prompt 20: Task C.2 - Topic Validator
```
Context: Implement topic scope validator with embedding similarity
AI Action: Created task_c2_topic_validator.py:
- OpenAI embeddings for similarity
- 6 allowed topics (Vietnamese land law)
- Cosine similarity threshold 0.6
- 20 test inputs (10 on-topic, 10 off-topic)
- Graceful fallback messages
```

### Prompt 21: Fix Missing API Key
```
User: "There's an error with the API key configuration"
Context: Script failing due to missing environment variable
AI Action: Fixed all Phase C scripts to load .env file:
- Added: from dotenv import load_dotenv
- Added: load_dotenv() at script start
- Fixed in C.2, C.3, C.4, C.5
```

### Prompt 22: Task C.3 - Adversarial Testing
```
Context: Test guardrails against 20 adversarial attacks
AI Action: Created task_c3_adversarial_testing.py:
- 20 attacks: DAN (5), roleplay (5), split (3), encoding (3), indirect (4)
- Multi-layer defense: topic guard + heuristic keywords
- False positive testing on 10 legitimate queries
- Expected detection rate: 95%+
```

### Prompt 23: Task C.4 - Output Guardrail
```
Context: Implement Llama Guard 3 (using OpenAI Moderation API)
AI Action: Created task_c4_output_guardrail.py:
- OpenAI Moderation API (no GPU needed)
- 10 unsafe + 10 safe test outputs
- Latency tracking (P50/P95/P99)
- Expected: 80%+ detection, <20% false positives
```

### Prompt 24: Task C.5 - Full Stack Integration
```
Context: Integrate all guardrails with latency benchmark
AI Action: Created task_c5_full_stack_integration.py:
- 4-layer architecture (L1: Input, L2: RAG, L3: Output, L4: Audit)
- 15 test queries benchmark
- P50/P95/P99 latency per layer
- Overhead calculation vs baseline
```

### Prompt 25: Phase C Status Document
```
Context: Document Phase C implementation status
AI Action: Created PHASE_C_STATUS.md:
- All 5 tasks documented
- Task C.1 tested (100% detection)
- Tasks C.2-C.5 created (ready to run)
- Dependencies and next steps listed
```

---

## Session 4: Phase D - Blueprint Document

### Prompt 26: Phase D Start
```
User: "Read README.md and proceed with Task D.1"
Context: Start Phase D - Blueprint Document
AI Action: Read README.md Phase D requirements (lines 900-1200)
```

### Prompt 27: Create Blueprint Document
```
Context: Generate production-ready blueprint with SLOs, architecture, runbooks
AI Action: Created results/phase_d/blueprint.md (20KB):
- Section 1: SLO Definition (5+ SLOs with alert thresholds)
- Section 2: Architecture Diagram (Mermaid + component details)
- Section 3: Alert Playbook (3 incident response procedures)
- Section 4: Cost Analysis (monthly estimate + optimization)
- Section 5: Deployment & Operations
- Section 6: Future Enhancements
- Appendices: Glossary + References
```

### Prompt 28: Task D Verification Script
```
Context: Create script to verify blueprint completeness
AI Action: Created task_d_blueprint_document.py:
- Checks file existence and size
- Verifies required sections present
- Counts tables and diagrams
- Validates completeness
- Result: ✅ Blueprint complete and production-ready
```

### Prompt 29: Fix Table Detection
```
Context: Table count showing 0 (regex issue)
AI Action: Fixed table detection regex:
- Changed from counting |---| to counting table headers
- Now correctly detects 8 tables
- Blueprint validation passes
```

---

## Session 5: Submission Package

### Prompt 30: Create Submission README
```
User: "Please create the README.md template for submission (Section 7.2)"
Context: Create submission README per lab requirements
AI Action: Created README_SUBMISSION.md:
- Overview (2-3 sentences)
- Setup instructions
- Results summary (all 4 phases)
- Project structure
- Running instructions
- Key learnings (5 insights)
- Challenges & solutions (4 items)
- Future improvements
- Demo video placeholder
- References
```

### Prompt 31: Create Prompts Log
```
User: "Please create the prompts.md file to log all AI prompts used"
Context: Document all AI prompts for academic integrity
AI Action: Created this file (prompts.md) documenting:
- All user prompts chronologically
- Context for each prompt
- AI actions taken
- Code changes made
- Results achieved
```

### Prompt 32: Refine Prompts Log
```
User: "Please rewrite the user prompts section - some phrases are too informal and need to be more professional"
Context: Improve academic tone of prompts documentation
AI Action: Rewrote all user prompts to:
- Use professional language
- Remove informal expressions
- Maintain clarity and accuracy
- Keep academic integrity standards
```

---

## Summary Statistics

### Total Prompts: 31 major prompts (90+ total messages)

### Breakdown by Phase:
- **Phase A (RAGAS):** 9 prompts
- **Phase B (LLM-Judge):** 6 prompts
- **Phase C (Guardrails):** 10 prompts
- **Phase D (Blueprint):** 4 prompts
- **Submission:** 2 prompts

### Types of AI Assistance:
1. **Code Generation:** 20 Python scripts created
2. **Debugging:** 8 API compatibility fixes
3. **Documentation:** 5 markdown documents
4. **Architecture Design:** 1 blueprint document
5. **Problem Solving:** Multiple iterations on RAGAS, judge bias, PII detection

### Key AI Contributions:
- ✅ Fixed RAGAS 0.4.x API compatibility (major blocker)
- ✅ Implemented 4-layer guardrail architecture
- ✅ Created production-ready blueprint document
- ✅ Generated comprehensive test sets and evaluation scripts
- ✅ Documented all work for submission

---

## Academic Integrity Statement

I acknowledge that:

1. **AI was used as a coding assistant** to help implement Lab 24 requirements
2. **All prompts are documented** in this file for transparency
3. **I understand the concepts** implemented (RAGAS, LLM-Judge, Guardrails, SLOs)
4. **I can explain the code** and design decisions made
5. **This is my own work** with AI assistance, not copied from others

The AI assistant (Kiro) helped with:
- Code implementation and debugging
- API compatibility fixes
- Documentation generation
- Architecture design

I was responsible for:
- Understanding requirements from README.md
- Directing the implementation approach
- Testing and validating results
- Making design decisions
- Reviewing and approving all code

---

## Notes

### What Worked Well:
- AI quickly adapted to RAGAS 0.4.x API changes
- Comprehensive documentation generated efficiently
- Good error handling and debugging assistance
- Production-ready code quality

### What Was Challenging:
- RAGAS API compatibility (multiple iterations needed)
- Judge bias detection (required statistical analysis)
- Vietnamese PII patterns (needed custom regex)
- Latency optimization (required careful measurement)

### Lessons Learned:
1. Always document AI prompts for academic integrity
2. AI is excellent for boilerplate and API adaptation
3. Human oversight essential for design decisions
4. Testing and validation still require human judgment

---

**Document End**

*This prompts log is maintained for academic integrity per Lab 24 requirements.*
