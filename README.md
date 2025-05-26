# Task Management API

A RESTful API for managing tasks, built with Flask.

## Features

- User registration and authentication using JWT
- CRUD operations for tasks
- Filtering, sorting, and pagination of tasks
- Search functionality
- Bulk operations for tasks
- Task statistics
- Comprehensive test coverage
- API documentation with Swagger

## Requirements

- Python 3.8+
- PostgreSQL

## Installation

1. Clone the repository:
git clone https://github.com/yourusername/task-management-api.git
cd task-management-api

2. Create a virtual environment and install dependencies:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Set up environment variables:
cp .env.example .env
Edit the `.env` file to configure your database connection and other settings.

4. Create the database:
createdb task_management

5. Run database migrations:
flask db upgrade

## Running the Application
flask run

The API will be available at http://localhost:5000

## API Documentation

Swagger UI will be available at http://localhost:5000/api/docs when the project is completed.

## Running Tests
pytest

## License

MIT