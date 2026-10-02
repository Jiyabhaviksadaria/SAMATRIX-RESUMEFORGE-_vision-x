import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.data_loader import load_dataset
from ml.data_profiler import profile_dataset
from ml.trainer import train_pipeline
from ml.predictor import Predictor
from backend.services.analysis_service import parse_and_analyze_resume
from ml.similarity import calculate_job_matching
from ml.ranking import rank_candidates


def main():
    sample_dataset = "data/sample/sample_resumes.csv"
    print("\n" + "="*50)
    print(" 🚀 RESUMEFORGE AI — END-TO-END DEMO EXECUTION")
    print("="*50)

    # Step 1: Profile Dataset
    print("\n[Step 1/6] Profiling Sample Dataset...")
    df = load_dataset(sample_dataset)
    profile = profile_dataset(df, target_col="job_role")
    print(f" ✓ Rows: {profile['rows']} | Columns: {profile['columns']}")
    print(f" ✓ Detected Task: {profile['recommended_task'].upper()} (Confidence: {profile['confidence']*100:.0f}%)")

    # Step 2: Train Baseline Model
    print("\n[Step 2/6] Training Baseline ML Models...")
    metadata = train_pipeline(data_path=sample_dataset, target_col="job_role", task_type="classification")
    print(f" ✓ Best Model Selected: {metadata['model']}")
    print(f" ✓ Performance F1-Score: {metadata['metrics'].get('f1', 'N/A')}")

    # Step 3: Run Prediction
    print("\n[Step 3/6] Testing Real-Time Resume Prediction...")
    test_resume = "Experienced Senior Data Scientist with 5 years in Python, Machine Learning, TensorFlow, Scikit-Learn, and SQL."
    predictor = Predictor()
    pred_res = predictor.predict_single(test_resume)
    print(f" ✓ Input Text: '{test_resume[:60]}...'")
    print(f" ✓ Predicted Role: {pred_res['prediction']} (Confidence: {pred_res['confidence']*100:.1f}%)")

    # Step 4: Resume Parsing & Skill Extraction
    print("\n[Step 4/6] Resume Analysis & Taxonomy Skill Extraction...")
    analysis = parse_and_analyze_resume(test_resume, candidate_name="Alice Smith")
    skills = analysis["skills"]["skills"]
    score = analysis["quality_analysis"]["overall_score"]
    print(f" ✓ Extracted Skills ({len(skills)}): {', '.join(skills[:6])}")
    print(f" ✓ Resume Quality Analysis Score: {score}/100")

    # Step 5: Profile-to-Job Matching
    print("\n[Step 5/6] Profile-to-Job Similarity Engine...")
    job_desc = "Seeking a Data Scientist proficient in Python, SQL, Machine Learning, TensorFlow, and AWS."
    matching = calculate_job_matching(test_resume, job_desc)
    print(f" ✓ Profile-to-Job Similarity: {matching['similarity_percentage']}")
    print(f" ✓ Matching Skills: {', '.join(matching['matching_skills'])}")
    print(f" ✓ Missing Skills: {', '.join(matching['missing_skills'])}")

    # Step 6: Candidate Ranking Matrix
    print("\n[Step 6/6] Multi-Candidate Ranking Matrix...")
    candidates = [
        {"candidate_id": "c1", "candidate_name": "Alice Smith", "resume_text": test_resume},
        {"candidate_id": "c2", "candidate_name": "Bob Jones", "resume_text": "Full Stack Engineer skilled in React TypeScript Node.js and AWS."}
    ]
    rankings = rank_candidates(candidates, job_desc)
    for r in rankings:
        print(f"   Rank #{r['rank']} {r['candidate_name']:<15} | Similarity: {r['similarity_percentage']} | Matches: {r['skill_count']} skills")

    print("\n" + "="*50)
    print(" 🎉 DEMO COMPLETED SUCCESSFULLY! SYSTEM READY FOR HACKATHON.")
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
