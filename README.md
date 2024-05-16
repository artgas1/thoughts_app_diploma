# Thoughts App

## Description
Thoughts App is a web-based platform designed to capture and share user thoughts. It provides an intuitive interface for users to post, edit, and manage their thoughts over time. This application is built using Python, Docker, and PostgreSQL, featuring a robust API and a responsive front-end.

## Features
- Post thoughts with a title and content
- Edit existing thoughts
- List all thoughts in a timeline
- Dockerized environment for easy setup and deployment

## Technology Stack
- **Back-end**: Python with FastAPI
- **Database**: PostgreSQL
- **Containerization**: Docker and Docker Compose
- **Monitoring**: Prometheus

## Getting Started

### Prerequisites
- Docker
- Docker Compose
- git (optional, for cloning the repository)

### Installation

1. **Clone the Repository (Optional)**
   ```bash
   git clone https://github.com/artgas1/thoughts_app_diploma.git
   cd thoughts_app_diploma
   ```

2. **Set Up the Environment**
   ```bash
   # Install Docker and Docker Compose if not already installed
   ./install_docker.sh

   # Set up the PostgreSQL database volume
   ./clear_postgres_volume.sh
   ```

3. **Run the Application**
   ```bash
   docker-compose up -d
   ```

### Accessing the Application
- The web interface can be accessed at `http://localhost:8000`
- API documentation is available at `http://localhost:8000/docs`

## Development

### Building the Application
- To build the Docker container manually:
  ```bash
  docker-compose build
  ```

### Running Tests
- Execute tests by running:
  ```bash
  docker-compose run --rm web python thoughts_app/manage.py test thoughts_core thoughts_app
  ```

## Configuration
- **Docker configurations**: Adjust `docker-compose.yml` for Docker settings.
- **Prometheus monitoring**: Modify `prometheus.yml` to configure monitoring settings.

## Contributing
Contributions to the Thoughts App are welcome! Please refer to the contributing guidelines for more details.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- Thanks to everyone who has contributed to this project!!!
