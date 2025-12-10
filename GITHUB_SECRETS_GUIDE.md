# GitHub Secrets Setup Guide

This guide shows you how to configure GitHub repository secrets for the DioramaCast application.

## Why GitHub Secrets?

GitHub Secrets allow you to securely store API keys and other sensitive information. The GitHub Actions workflow will automatically use these secrets as environment variables during automated testing.

## Step-by-Step Setup

### 1. Navigate to Repository Settings

1. Go to your GitHub repository: `https://github.com/Erik0810/DioramaCast`
2. Click on **Settings** (top navigation bar)

### 2. Access Secrets and Variables

1. In the left sidebar, scroll down to **Security** section
2. Click on **Secrets and variables**
3. Select **Actions** from the dropdown

### 3. Add Repository Secrets

Click the **New repository secret** button and add the following secrets:

#### Secret 1: OPENWEATHER_API_KEY
- **Name**: `OPENWEATHER_API_KEY`
- **Value**: Your OpenWeatherMap API key
- Get a free key at: https://openweathermap.org/api

#### Secret 2: NANABANA_API_KEY
- **Name**: `NANABANA_API_KEY`
- **Value**: Your Nano Banana Pro API key

### 4. Verify Secrets are Added

After adding both secrets, you should see them listed:
- ✅ OPENWEATHER_API_KEY
- ✅ NANABANA_API_KEY

## How the Workflow Uses Secrets

The GitHub Actions workflow (`.github/workflows/test.yml`) automatically fetches secrets:

```yaml
env:
  OPENWEATHER_API_KEY: ${{ secrets.OPENWEATHER_API_KEY }}
  NANABANA_API_KEY: ${{ secrets.NANABANA_API_KEY }}
  FLASK_DEBUG: False
```

These environment variables are available to:
- The Flask application during tests
- All test cases
- API endpoint testing

## Manual Workflow Trigger

You can manually run the test workflow:

1. Go to the **Actions** tab in your repository
2. Select **Test DioramaCast Application** workflow
3. Click **Run workflow** button
4. Choose the branch (default: main)
5. Click the green **Run workflow** button

The workflow will:
- ✅ Install Python dependencies
- ✅ Run 8 comprehensive tests
- ✅ Test API endpoints with your secrets
- ✅ Verify environment variables are configured
- ✅ Display results and logs

## Automatic Triggers

The workflow automatically runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Manual trigger via Actions tab

## Security Notes

✅ **Secrets are encrypted** - GitHub encrypts secrets before storing them
✅ **Secrets are masked** - Secret values are hidden in workflow logs
✅ **Scoped access** - Secrets are only available to workflows in the repository
✅ **No export** - Secrets cannot be exported or viewed after creation

## Testing Locally

For local development, continue using the `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

The application reads from `os.environ.get()` which works for both:
- Local `.env` files (via python-dotenv)
- GitHub Secrets (via workflow environment variables)

## Troubleshooting

**Test Fails with "API key not configured"**
- Check that secret names match exactly: `OPENWEATHER_API_KEY` and `NANABANA_API_KEY`
- Verify secrets are added to the repository (not organization or user secrets)
- Check workflow logs to see if environment variables are detected

**Workflow doesn't trigger**
- Ensure you're pushing to `main` or `develop` branch
- Check that workflow file exists at `.github/workflows/test.yml`
- Manually trigger via Actions tab to test

**Can't find Actions tab**
- Actions must be enabled for your repository
- Go to Settings → Actions → General and enable Actions

## Support

For issues or questions, please open an issue in the repository.
