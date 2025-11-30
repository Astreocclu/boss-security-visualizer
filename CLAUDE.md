# Boss Security Visualizer

## Branch Workflow

This project uses two separate working directories for development:

| Directory | Branch | Purpose |
|-----------|--------|---------|
| `boss-security-visualizer` | `master` | Stable, production-ready code |
| `boss-security-visualizer-dev` | `development` | Experimental, risky changes |

Both directories point to the same GitHub repo: `Astreocclu/boss-security-visualizer`

### Workflow
- Work on stable features in `boss-security-visualizer` → pushes to `master`
- Experiment with risky features in `boss-security-visualizer-dev` → pushes to `development`
- When a feature is tested and ready, merge `development` into `master` via PR

### Merging Development to Master
```bash
# From the main repo directory
git fetch origin
git merge origin/development
# Or create a PR on GitHub
```
