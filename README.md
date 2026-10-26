# Ti Gato Gro Plaizir - Django Project

## How to run this project locally (For Collaborators)

1. Clone the repository:
   `git clone https://github.com/chiranjeevramphall-22/TiGatoGroPlaizir.git`

2. Navigate into the folder:
   `cd TiGatoGroPlaizir`

3. Create a virtual environment:
   `python -m venv venv`

4. Activate the virtual environment:
   * Windows: `venv\Scripts\activate`
   * Mac/Linux: `source venv/bin/activate`

5. Install the required packages:
   `pip install django pillow`

6. Run database migrations:
   `python manage.py migrate`

7. Load the initial cake data into the database:
   `python manage.py loaddata cakes.json`

8. Create an Admin account (to access the backend dashboard):
   `python manage.py createsuperuser`
   *(Follow the prompts to set a username, email, and password)*

9. Start the server:
   `python manage.py runserver`

10. Open your browser and go to: `http://127.0.0.1:8000/`

## Project Features
* Customer Registration & Smart Username Suggestions
* Dynamic Cake Catalogue & Availability Tracking
* Standard Ordering with Pickup/Delivery & Payment Options
* Custom Cake Requests with Event Details Modal
* Real-time Order Status Tracking
* Admin Dashboard for Orders, Custom Requests & Cake Management