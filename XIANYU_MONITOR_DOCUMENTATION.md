# Xianyu (Goofish) Intelligent Monitoring Robot - External Documentation

## 1. Project Overview

### 1.1 Main Purpose and Features

The Xianyu (Goofish) Intelligent Monitoring Robot is an advanced tool for monitoring and analyzing second-hand listings on Xianyu (Goofish), a popular Chinese second-hand marketplace. It combines web scraping with AI-powered filtering and analysis to help users find items that match their specific criteria.

Key features include:
- **Web UI for task management**: A comprehensive web-based management interface built with FastAPI
- **AI-driven task creation**: Natural language descriptions to automatically generate monitoring tasks
- **Concurrent multi-task monitoring**: Independent configurations for multiple monitoring tasks
- **Real-time stream processing**: Immediate processing of new listings as they appear
- **Deep AI analysis**: Multimodal AI analysis combining product images/text and seller profiling
- **Instant notifications**: Via ntfy.sh, WeChat Work bots, and Bark
- **Cron-based task scheduling**: Automated execution of monitoring tasks
- **Docker deployment support**: Containerized deployment for easy setup
- **Robust anti-scraping strategies**: Randomized delays and behavior simulation

### 1.2 Key Technologies Used

- **FastAPI**: Web framework for the management interface
- **Playwright**: Web scraping and browser automation
- **AI Integration**: Multimodal LLMs for intelligent filtering and analysis
- **AsyncIO**: Asynchronous programming for concurrent task execution
- **Docker**: Containerization for deployment
- **APScheduler**: Task scheduling

### 1.3 Architecture Overview

The system consists of several core components:
1. **Web Management Interface** (`web_server.py`): FastAPI application providing REST API and serving the web UI
2. **Spider Engine** (`spider_v2.py`): Core spider script that executes monitoring tasks
3. **Scraping & Analysis** (`src/scraper.py`): Main scraping logic and AI integration
4. **AI Processing** (`src/ai_handler.py`): AI analysis and notification functions
5. **Configuration Management** (`src/config.py`): Configuration management and AI client initialization
6. **Task Management** (`src/task.py`): Task data models and file operations
7. **Utility Functions** (`src/utils.py`): Utility functions for retry logic, random sleep, data formatting
8. **Prompt Utilities** (`src/prompt_utils.py`): AI prompt generation for new tasks

## 2. Core Components

### 2.1 Web Management Interface (web_server.py)

The web management interface is built with FastAPI and provides:
- Authentication using HTTP Basic Auth
- Task lifecycle management (create, update, start, stop, delete)
- Real-time log streaming and result browsing
- AI prompt file editing
- System status monitoring
- Scheduler integration for cron-based tasks

Key features:
- RESTful API endpoints for all management operations
- Real-time log streaming with incremental updates
- Result browsing with pagination, filtering, and sorting
- Prompt file management for AI analysis customization
- Notification settings configuration
- System status monitoring and diagnostics

### 2.2 Spider Engine (spider_v2.py)

The spider engine is responsible for executing monitoring tasks:
- Asynchronous task execution using asyncio
- Playwright integration for browser automation
- Multi-task concurrent processing
- Configurable search filters (keywords, price ranges, personal items only)
- Detailed product and seller information extraction

The spider processes tasks defined in `config.json` and performs the following steps:
1. Load task configurations
2. Navigate to search results on Goofish
3. Apply filters (newest first, personal items only, price range)
4. Process search results across multiple pages
5. Extract detailed product information
6. Collect seller profile information
7. Pass data to AI for analysis
8. Send notifications for recommended items
9. Save results to JSONL files

### 2.3 Scraping & AI Analysis (src/scraper.py)

This module handles the core scraping functionality:
- Playwright-based web scraping with anti-detection measures
- User profile scraping (seller/buyer ratings, transaction history)
- Image downloading for AI analysis
- Real-time AI analysis pipeline with retry logic
- Notification sending for recommended items

Key functions:
- `scrape_user_profile()`: Collects comprehensive seller information
- `scrape_xianyu()`: Main scraping function that orchestrates the entire process

### 2.4 AI Processing (src/ai_handler.py)

The AI processing module handles:
- Multimodal AI analysis of product images and structured data
- Integration with OpenAI-compatible APIs
- Base64 image encoding for model input
- Response validation and error handling
- Notification services (ntfy, WeChat Work, Bark, Webhook)

Key functions:
- `download_all_images()`: Downloads product images for AI analysis
- `get_ai_analysis()`: Sends product data and images to AI for analysis
- `send_ntfy_notification()`: Sends notifications when items are recommended
- `encode_image_to_base64()`: Encodes images for AI processing

### 2.5 Configuration Management (src/config.py)

Handles all configuration aspects:
- Environment variable loading with dotenv
- AI client initialization
- File path management
- API URL patterns
- HTTP headers configuration

Key configuration elements:
- AI model settings (API key, base URL, model name)
- Notification service URLs
- Browser settings (headless mode, browser type)
- Debug and feature flags

### 2.6 Task Management (src/task.py)

Manages task data models and persistence:
- Task data models using Pydantic
- File-based storage in config.json
- CRUD operations for tasks

### 2.7 Utility Functions (src/utils.py)

Provides common utility functions:
- Retry mechanism with exponential backoff
- Safe nested dictionary access
- Random sleep for anti-detection
- URL conversion utilities
- Data formatting and saving functions

### 2.8 Prompt Utilities (src/prompt_utils.py)

Handles AI prompt generation and management:
- AI-powered criteria generation from natural language descriptions
- Prompt template management
- Configuration file updates

## 3. Key Features

### 3.1 Web UI for Task Management

The web interface provides a comprehensive management dashboard:
- Task creation and configuration
- Real-time log viewing
- Result browsing with filtering and sorting
- Prompt file editing
- System status monitoring
- Notification settings management

### 3.2 AI-Driven Task Creation

Users can create monitoring tasks using natural language descriptions:
- Describe what you're looking for in plain language
- AI automatically generates complex filtering criteria
- Customizable analysis standards for different product types

### 3.3 Concurrent Multi-Task Monitoring

Supports running multiple monitoring tasks simultaneously:
- Each task has independent configuration
- Tasks run concurrently without interference
- Resource management to prevent overload

### 3.4 Real-Time Stream Processing

Processes new listings as they appear:
- Immediate analysis of new items
- Real-time notifications
- Continuous monitoring without batch delays

### 3.5 AI Analysis with Multimodal LLMs

Advanced AI analysis combining:
- Product images analysis
- Structured product data evaluation
- Seller profile assessment
- Comprehensive recommendation scoring

### 3.6 Notification Systems

Multiple notification channels:
- **ntfy.sh**: Push notifications to mobile devices
- **WeChat Work bots**: Enterprise messaging integration
- **Bark**: iOS/macOS push notifications
- **Webhook**: Generic webhook support for custom integrations

### 3.7 Cron-Based Scheduling

Flexible task scheduling using cron expressions:
- Each task can have its own schedule
- Supports complex scheduling patterns
- Automatic task execution

### 3.8 Docker Deployment Support

Containerized deployment for easy setup:
- Dockerfile for building images
- docker-compose configuration
- Environment variable configuration
- Volume mounting for persistent data

### 3.9 Anti-Scraping Strategies

Robust anti-detection measures:
- Randomized delays between actions
- Behavior simulation to mimic human users
- Headless browser detection avoidance
- Session management with state preservation

## 4. Configuration Files

### 4.1 .env File for Environment Variables

The `.env` file contains all configuration settings:
- AI model configuration (API key, base URL, model name)
- Notification service URLs and credentials
- Browser settings (headless mode, browser type)
- Debug and feature flags
- Web interface authentication credentials

Key environment variables:
- `OPENAI_API_KEY`: API key for the AI service
- `OPENAI_BASE_URL`: Base URL for the AI service
- `OPENAI_MODEL_NAME`: Name of the AI model to use
- `NTFY_TOPIC_URL`: URL for ntfy.sh notifications
- `WX_BOT_URL`: WeChat Work bot URL
- `BARK_URL`: Bark notification URL
- `RUN_HEADLESS`: Whether to run browser in headless mode
- `WEB_USERNAME`/`WEB_PASSWORD`: Web interface credentials

### 4.2 config.json for Task Definitions

The `config.json` file defines all monitoring tasks:
- Task name and enabled status
- Search keywords and filters
- Page limits and personal item preferences
- Price range filters
- Cron scheduling expressions
- AI prompt file references

Example task configuration:
```json
{
  "task_name": "MacBook Air M1",
  "enabled": true,
  "keyword": "macbook air m1",
  "max_pages": 5,
  "personal_only": true,
  "min_price": "3000",
  "max_price": "5000",
  "cron": "3 12 * * *",
  "ai_prompt_base_file": "prompts/base_prompt.txt",
  "ai_prompt_criteria_file": "prompts/macbook_criteria.txt",
  "is_running": false
}
```

### 4.3 xianyu_state.json for Login Session State

The `xianyu_state.json` file stores browser session state for authenticated scraping:
- Cookie information for logged-in sessions
- Browser storage state
- Authentication tokens

This file is generated by the login process and is essential for accessing personalized content on Xianyu.

### 4.4 Prompt Files in prompts/ Directory

The `prompts/` directory contains AI prompt templates:
- `base_prompt.txt`: Base prompt template with output format
- `*_criteria.txt`: Product-specific analysis criteria

The prompt system uses a two-part approach:
1. **Base Prompt**: Defines the structure and output format for AI responses
2. **Criteria Files**: Product-specific analysis criteria that are inserted into the base prompt

## 5. Deployment and Usage

### 5.1 Environment Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/dingyufei615/ai-goofish-monitor
   cd ai-goofish-monitor
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables by copying `.env.example` to `.env` and editing the values:
   ```bash
   cp .env.example .env
   ```

### 5.2 Running the Application

1. Start the web management interface:
   ```bash
   python web_server.py
   ```

2. Access the web interface at `http://127.0.0.1:8000`

3. Configure tasks through the web interface or by editing `config.json` directly

### 5.3 Docker Deployment

1. Build and start services:
   ```bash
   docker-compose up --build -d
   ```

2. View logs:
   ```bash
   docker-compose logs -f
   ```

3. Stop services:
   ```bash
   docker-compose down
   ```

### 5.4 Development Utilities

Generate new AI criteria files from natural language descriptions:
```bash
python prompt_generator.py
```

## 6. Data Flow

1. Tasks defined in `config.json` are loaded by `spider_v2.py`
2. Playwright performs authenticated searches on Goofish
3. New listings are detected and detailed information scraped
4. Product images are downloaded
5. Complete product/seller data sent to AI for analysis
6. AI response determines if item meets criteria
7. Recommended items trigger notifications
8. All results saved to JSONL files
9. Web UI provides management interface for all components

## 7. Security and Authentication

The web interface uses HTTP Basic Auth for protection:
- Configurable username and password via environment variables
- All API endpoints and static resources require authentication
- Health check endpoint (`/health`) is publicly accessible
- Default credentials are `admin`/`admin123` (should be changed in production)

## 8. Error Handling and Recovery

The system includes robust error handling:
- Retry mechanisms for network failures
- Graceful degradation when AI services are unavailable
- Automatic cleanup of temporary files
- Detailed logging for troubleshooting
- Recovery from browser automation errors

## 9. Performance Considerations

To maintain good performance and avoid detection:
- Randomized delays between actions
- Concurrent task processing with resource limits
- Efficient image handling with temporary file cleanup
- Asynchronous processing to maximize throughput
- Proper session management to reduce login requirements

This documentation provides a comprehensive overview of the Xianyu Intelligent Monitoring Robot, covering its architecture, components, features, and usage instructions. The system is designed to be flexible, extensible, and user-friendly while providing powerful monitoring and analysis capabilities for second-hand marketplace listings.