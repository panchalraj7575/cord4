# Category-Product-User API

## Overview

This is a Django rest framework based API that provides functionality for category and product management, user authentication. The API supports CRUD operations, authentication via JWT, and bulk upload of categories and products.

## Features

- **User Authentication:** JWT-based authentication with token generation.
- **Admin Controls:** As per the documentation.
- **Public Access:** As per the documentation.
- **Soft Deletion:** As per the documentation.
- **Bulk Upload:** Admins can bulk upload categories and products with auto-mapping.

## Technologies Used

- Django REST Framework (DRF)
- PostgreSQL
- JWT Authentication

### Prerequisites

- Python
- PostgreSQL
- Virtual Environment (recommended)

### Steps

1. Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. set .env file before step 3.

3. Run seed.py file: It will manage requirements, migrations, superuser.

   ```sh
   python seed.py
   ```

4. Run the server:

   ```sh
   python manage.py runserver
   ```
