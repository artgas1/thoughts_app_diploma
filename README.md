# thoughts_app

# ThoughtsApp

This is the documentation for deploying and working with the ThoughtsApp project.

## Deployment

To deploy the ThoughtsApp project, follow these steps:

1. Start the app by running the following command:

    ```bash
    docker-compose up -d --build
    ```

## Development

### Making Migrations

To make migrations in the ThoughtsApp project, follow these steps:

1. Open a terminal or command prompt.
2. Start the project via Docker using the command below:
    ```bash
    docker-compose up -d --build
    ```

3. Set the `DB_HOST` environment variable to `localhost` by running the following command:
    ```bash
    export DB_HOST=localhost
    ```
   This is necessary to run `makemigrations` on your local PostgreSQL.

4. Navigate to the root directory of the project.

5. Run the following command to create a new migration:
    ```bash
    python manage.py makemigrations
    ```

6. It will generate a new migration file in the migrations folder. After the container is up, the changes will be applied to the database by running:
    ```bash
    python manage.py migrate
    ```
