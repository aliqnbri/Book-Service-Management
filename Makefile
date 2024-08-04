build:
    docker-compose build

up:
    docker-compose up -d

down:
    docker-compose down

logs:
    docker-compose logs -f

psql:
    docker-compose exec db psql -U myuser mydb