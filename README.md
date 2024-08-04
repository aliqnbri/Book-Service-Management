# **Book Management System**

A simple book management system built using Django and PostgreSQL, without using Django's ORM.

## **Project Overview**

This project provides a basic book management system with the following features:

- User registration and login
- Book suggestion based on user reviews
- Review management (create, read, update, delete)
- User profile management

## **Technical Details**

- Built using Django 3.x
- Uses PostgreSQL as the database
- Does not use Django's ORM (Object-Relational Mapping) system
- Uses custom database queries to interact with the PostgreSQL database
- Uses JWT (JSON Web Tokens) for authentication

## **API Endpoints**

The project provides the following API endpoints:

- `POST /users/register`: Register a new user
- `POST /users/login`: Login an existing user
- `GET /users/{id}`: Get a user's profile
- `GET /users/{id}/suggest`: Get book suggestions for a user
- `POST /reviews`: Create a new review
- `GET /reviews`: Get all reviews for a user
- `GET /reviews/{id}`: Get a single review
- `PUT /reviews/{id}`: Update a review
- `DELETE /reviews/{id}`: Delete a review

## **Database Schema**

The project uses the following database schema:

- `users` table: stores user information
- `reviews` table: stores review information
- `books` table: stores book information (not implemented yet)

## **Installation**

To install the project, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/book-management-system.git`
2. Install the required packages: `pip install -r requirements.txt`
3. Create a new PostgreSQL database and update the `settings.py` file with the database credentials
4. Run the migrations: `python manage.py migrate`
5. Run the development server: `python manage.py runserver`
