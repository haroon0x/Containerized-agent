# Quick Instructions

## Build & Run
- Build: `docker-compose build --no-cache`
- Run: `export GEMINI_API_KEY=your_key && docker-compose up`
- Stop: `docker-compose down`

## Environment Variables
- `GEMINI_API_KEY` (required): LLM API key
- `JOB_PROMPT`: Task for the agent (default: echo hello)
- `JOB_ID`: Job identifier (optional)

## Output
- Results: `/workspace/output/result.json` (inside container)
- To mount output: uncomment in `docker-compose.yml` and run `sudo chown -R 1000:1000 ./output` on host

## Testing & Debugging
- Check logs: `docker-compose logs -f`
- Inspect output: `cat ./output/result.json` (if mounted)
- Run a custom task: `export JOB_PROMPT='your task' && docker-compose up`
- Clean up: `docker-compose down -v` (removes containers & volumes)
- Rebuild after code changes: `docker-compose build --no-cache`

## Troubleshooting
- Permission errors: Fix host output dir ownership
- LLM errors: Check `GEMINI_API_KEY` is set

## Dev Tips
- Edit code in `src/`
- Alpine Linux base for speed

