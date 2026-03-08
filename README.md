# DailyMerge

![Demo](assets/main_page.png)

![Demo](assets/profile_page.png)

![Demo](assets/source_form.png)

**DailyMerge** is a Django-based news aggregator website that collects articles from RSS feeds. The data is normalized, stored in a database, and displayed on the main page while it remains relevant. Outdated articles are automatically removed to keep the news fresh.


## Main Features 

- Aggregates news from RSS feeds
- Scheduled background fetching and automatic removal of outdated articles
- Admin panel for managing sources, categories, and articles
- User registration and authentication
- User profile for managing filters, categories, and sources
- Shared objects optimization between users
- Password management (reset and change password)
- CRUD operations 
- Category-based filtering
- Asynchronous validation of article images

## Installation

1. Clone the repo
```sh
git clone https://github.com/Yelahin/dailymerge.git
```

2. Navigate to the project root (where `manage.py` is located)

```sh
cd dailymerge
```

3. Create .env file and set up variables


```
DJANGO_SECRET=
DJANGO_ALLOWED_HOSTS=127.0.0.1, localhost
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

4. Start Docker Compose and create superuser

```sh
docker compose up --build -d
```

```sh
docker exec -it django python manage.py createsuperuser
```

## Built with

Core technologies and libraries used in this project.


- ![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)

- ![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)

- ![Celery](https://img.shields.io/badge/celery-%23a9cc54.svg?style=for-the-badge&logo=celery&logoColor=white)


- ![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)

- ![image](https://img.shields.io/badge/Docker%20Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

- ![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)


- ![image](https://img.shields.io/badge/redis-CC0000.svg?&style=for-the-badge&logo=redis&logoColor=white)

<hr>

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

