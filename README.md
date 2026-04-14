# Django REST Framework API for Books

This project provides a complete API for managing books using Django and Django REST Framework. It includes endpoints to list and create books, and is containerized with Docker and Docker Compose.

## Features

- Django REST Framework API
- Book model with title, author, ISBN, and publication date
- GET `/api/libros/` - List all books
- POST `/api/libros/` - Create a new book
- PostgreSQL database (with SQLite fallback)
- Docker containerization

## Project Structure

```
mi_proyecto/
├── libros/                    # Django app
│   ├── migrations/           # Database migrations
│   ├── models.py            # Book model
│   ├── serializers.py       # DRF serializer
│   ├── views.py             # API views
│   └── urls.py              # App URLs
├── mi_proyecto/             # Project settings
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## Setup and Running

### Option 1: Using Docker Compose (Recommended)

1. Make sure you have Docker and Docker Compose installed.

2. Clone the repository and navigate to the project directory.

3. Build and start the services:
   ```bash
   docker-compose up --build
   ```

4. The API will be available at `http://localhost:8000/api/libros/`

5. To stop the services:
   ```bash
   docker-compose down
   ```

### Option 2: Local Development (without Docker)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```bash
   python manage.py migrate
   ```

4. Run the development server:
   ```bash
   python manage.py runserver
   ```

5. Access the API at `http://localhost:8000/api/libros/`

## API Endpoints

### List Books
- **URL:** `/api/libros/`
- **Method:** `GET`
- **Success Response:**
  ```json
  [
    {
      "id": 1,
      "titulo": "El Quijote",
      "autor": "Miguel de Cervantes",
      "isbn": "9788424113496",
      "fecha_publicacion": "2026-04-14"
    }
  ]
  ```

### Create Book
- **URL:** `/api/libros/`
- **Method:** `POST`
- **Headers:** `Content-Type: application/json`
- **Request Body:**
  ```json
  {
    "titulo": "Cien años de soledad",
    "autor": "Gabriel García Márquez",
    "isbn": "9788437604947"
  }
  ```
- **Note:** `fecha_publicacion` is automatically set to the current date.

## Database Configuration

By default, the project uses SQLite. When running with Docker Compose, it automatically switches to PostgreSQL using environment variables.

To use PostgreSQL locally, set the environment variable:
```bash
export DB_ENGINE=postgresql
```

## Development

### Running Tests
```bash
python manage.py test libros
```

### Creating Migrations
After modifying models:
```bash
python manage.py makemigrations libros
python manage.py migrate
```

### Admin Interface
Access the Django admin at `http://localhost:8000/admin/` (create a superuser first with `python manage.py createsuperuser`).

## License

This project is for educational purposes.