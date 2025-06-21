# GitHub Actions Workflow

This directory contains GitHub Actions workflows for the FarmPower project.

## Deployment Workflow

The deployment workflow is defined in `.github/workflows/render-deploy.yml` and handles:

1. **Testing**: Runs tests on every push and pull request to the `main` branch
2. **Deployment**: Automatically deploys to Render when changes are pushed to `main`

### Required Secrets

Add these secrets to your GitHub repository settings:

1. `RENDER_API_KEY`: Your Render API key
   - Generate it from your Render dashboard: [https://dashboard.render.com/account/api-keys](https://dashboard.render.com/account/api-keys)
   - Add it to your repository: `Settings` > `Secrets and variables` > `Actions` > `New repository secret`

2. Environment Variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`

### Manual Deployment

To trigger a manual deployment:

1. Push to the `main` branch
2. Or manually trigger the workflow from the Actions tab

### Monitoring

Monitor deployments and workflow runs in the GitHub Actions tab.
