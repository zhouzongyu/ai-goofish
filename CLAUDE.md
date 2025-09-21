# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an intelligent monitoring robot for Xianyu (Goofish), a Chinese second-hand marketplace. It uses Playwright for web scraping and AI (multimodal LLMs) for intelligent filtering and analysis of listings. The project features a comprehensive web-based management interface built with FastAPI.

Key features:
- Web UI for task management, AI prompt editing, real-time logs and result browsing
- AI-driven task creation using natural language descriptions
- Concurrent multi-task monitoring with independent configurations
- Real-time stream processing of new listings
- Deep AI analysis combining product images/text and seller profiling
- Instant notifications via ntfy.sh, WeChat Work bots, and Bark
- Cron-based task scheduling
- Docker deployment support
- Robust anti-scraping strategies with randomized delays

## Repository Structure

- `web_server.py`: Main FastAPI application with web UI and task management
- `spider_v2.py`: Core spider script that executes monitoring tasks
- `src/`: Core modules
  - `scraper.py`: Main scraping logic and AI integration
  - `ai_handler.py`: AI analysis and notification functions
  - `parsers.py`: Data parsing for search results and user profiles
  - `config.py`: Configuration management and AI client initialization
  - `utils.py`: Utility functions (retry, random sleep, data formatting)
  - `prompt_utils.py`: AI prompt generation for new tasks
  - `task.py`: Task data models and file operations
- `prompts/`: AI prompt templates and criteria files
- `static/` and `templates/`: Web UI frontend files
- `config.json`: Task configurations
- `xianyu_state.json`: Login session state for authenticated scraping
- `.env`: Environment variables for API keys, notification settings, etc.

## Common Development Commands

### Setting up the environment
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings
```

### Running the application
```bash
# Start the web management interface
python web_server.py

# Run spider tasks directly (usually managed through web UI)
python spider_v2.py
```

### Docker deployment
```bash
# Build and start services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development utilities
```bash
# Generate new AI criteria files from natural language descriptions
python prompt_generator.py
```

## Core Architecture

### Web Management Interface (web_server.py)
- FastAPI application providing REST API and serving web UI
- Authentication using HTTP Basic Auth
- Task lifecycle management (create, update, start, stop, delete)
- Real-time log streaming and result browsing
- AI prompt file editing
- System status monitoring
- Scheduler integration for cron-based tasks

### Spider Engine (spider_v2.py)
- Asynchronous task execution using asyncio
- Playwright integration for browser automation
- Multi-task concurrent processing
- Configurable search filters (keywords, price ranges, personal items only)
- Detailed product and seller information extraction

### Scraping & Analysis (src/scraper.py)
- Playwright-based web scraping with anti-detection measures
- User profile scraping (seller/buyer ratings, transaction history)
- Image downloading for AI analysis
- Real-time AI analysis pipeline with retry logic
- Notification sending for recommended items

### AI Processing (src/ai_handler.py)
- Multimodal AI analysis of product images and structured data
- Integration with OpenAI-compatible APIs
- Base64 image encoding for model input
- Response validation and error handling
- Notification services (ntfy, WeChat Work, Bark, Webhook)

### Data Flow
1. Tasks defined in `config.json` are loaded by `spider_v2.py`
2. Playwright performs authenticated searches on Goofish
3. New listings are detected and detailed information scraped
4. Product images are downloaded
5. Complete product/seller data sent to AI for analysis
6. AI response determines if item meets criteria
7. Recommended items trigger notifications
8. All results saved to JSONL files
9. Web UI provides management interface for all components

## Key Configuration Files

- `.env`: API keys, notification settings, web auth credentials
- `config.json`: Monitoring task definitions with filters and AI prompts
- `xianyu_state.json`: Browser session state for authenticated scraping
- Prompt files in `prompts/` directory define AI analysis criteria

开发文档
@[XIANYU_MONITOR_DOCUMENTATION.md](XIANYU_MONITOR_DOCUMENTATION.md)

Always respond in Chinese-simplified
