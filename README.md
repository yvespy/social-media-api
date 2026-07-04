# Social Media REST API

A fully featured RESTful API for a social media platform built with Django and Django REST Framework.

## Features

- **User Registration & Authentication** (JWT)
- **User Profiles** with search
- **Follow/Unfollow** other users
- **Post Creation & Retrieval**
- **Likes and Comments** on posts
- **Permissions**: update/delete only your own content
- **Optional**: Scheduled posts with Celery (if enabled)
- **Fully documented** using Swagger (`drf-spectacular`)

## Stack

- Python 3.10+
- Django 5.x
- Django REST Framework
- SQLite
- drf-spectacular (OpenAPI docs)
- Django SimpleJWT


---

## Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-username/social-api.git
cd social-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
2. **Running with Docker**

```bash
docker build -t social-api .
docker run -d -p 8000:8000 --name social-api-container social-api
```
## Authentication

This API uses JWT (JSON Web Tokens).
- **Login** (`POST /api/token/`)
- **Refresh** (`POST /api/token/refresh/`)
- Include token in requests:
```bash
Authorization: Bearer <your_token>
```
## API Documentation
Interactive API docs available at:
```bash
http://localhost:8000/api/schema/swagger-ui/
```
(OpenAPI via drf-spectacular)
## Endpoints Overview
### Auth
- (`POST /api/users/register/`) - Register new user 
- (`POST /api/users/token/`) - Get JWT token
- (`POST /api/users/token/refresh/`) - Refresh token

### Users
- (`GET /api/users/`) - List/search users 
- (`GET /api/users/<id>/`) - Retrieve user profile

### Profile (own)
- (`GET /api/users/profile/`) - Get current user's profile 
- (`PATCH /api/users/profile/`) - Update current user's profile

### Followers / Following
- (`POST /api/follow/`) - Follow a user 
- (`POST /api/follow/unfollow/`) - Unfollow a user
- (`GET /api/users/<id>/followers/`) - Get followers
- (`GET /api/users/<id>/following/`) - Get followings

### Posts
- (`GET /api/posts/`) - List posts (searchable by title)
- (`POST /api/posts/`) - Create a new post
- (`GET /api/posts/<id>/`) - Retrieve post details
- (`PATCH /api/posts/<id>/`) - Update own post
- (`DELETE /api/posts/<id>/`) - Delete own post

### Comments
- (`GET /api/comments/`) - List comments
- (`POST /api/comments/`) - Add comment
- (`GET /api/comments/<id>/`) - Retrieve comment
- (`PATCH /api/comments/<id>/`) - Update own comment
- (`DELETE /api/comments/<id>/`) - Delete own comment

## Comments
- Authenticated users only can create, update, delete posts and comments.
- Users can only modify or delete their own posts/comments/profiles.
- Unauthenticated users can read-only.
