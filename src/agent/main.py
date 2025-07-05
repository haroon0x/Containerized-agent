import logging
import argparse
import os
import json
from typing import Dict, Any
from agent.flow import create_qa_flow
from agent.nodes import GetQuestionNode

logging.basicConfig(level=logging.INFO)

def main() -> None:
    parser = argparse.ArgumentParser(description="Containerized Agent")
    parser.add_argument("--prompt", type=str, default="In one sentence, what's the end of universe?", help="Job prompt")
    parser.add_argument("--job-id", type=str, default="unknown", help="Job ID")
    args = parser.parse_args()

    shared: Dict[str, Any] = {
        "question": args.prompt,
        "answer": None
    }

    try:
        qa_flow = create_qa_flow()
        qa_flow.run(shared)
        
        result = {
            "job_id": args.job_id,
            "prompt": args.prompt,
            "answer": shared.get("answer", "No answer generated"),
            "status": "completed"
        }
        
        # Save result to output directory
        output_dir = "/workspace/output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "result.json"), "w") as f:
            json.dump(result, f, indent=2)
            
        logging.info(f"Job {args.job_id} completed successfully")
        logging.info(f"Question: {shared['question']}")
        logging.info(f"Answer: {shared['answer']}")
        
    except Exception as e:
        error_result = {
            "job_id": args.job_id,
            "prompt": args.prompt,
            "error": str(e),
            "status": "failed"
        }
        
        output_dir = "/workspace/output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "result.json"), "w") as f:
            json.dump(error_result, f, indent=2)
            
        logging.error(f"Job {args.job_id} failed: {e}")
        raise

if __name__ == "__main__":
    main()
