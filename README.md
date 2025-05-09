# RETS real estate performance tracker
- hosted on render 
- link: https://base-1kn8.onrender.com/

A comprehensive performance tracking and analytics application built with Django.
## Features

- Performance tracking and analytics
- Data visualization and reporting
- User authentication and authorization
- Property management system
- Document management
- Media handling
- Real-time data processing

## Tech Stack

### Backend
- Django 5.1.6
- sqlite
- Gunicorn
- WhiteNoise for static files
- Social Auth for authentication

### Data Processing & Analytics
- NumPy
- Pandas
- Matplotlib
- Seaborn
- Scikit-learn

### Additional Tools
- Pillow for image processing
- Requests for API integration
- Python-dateutil for date handling

## Project Structure

```
├── base/                  # Base application components
├── performanceTracker/    # Main application logic
├── static/               # Static files
├── staticfiles/          # Collected static files
├── media/                # User-uploaded media
├── task_documents/       # Document storage
├── templates/            # HTML templates
├── property_images/      # Property-related images
├── manage.py            # Django management script
└── requirements.txt     # Project dependencies
```

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   - Create a `.env` file
   - Add necessary configuration variables

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Deployment


1. Set up environment variables on your hosting platform
2. Configure the database URL
3. Run migrations on the production server
4. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request



## Contact

andrewgathuto7@gmail.com
