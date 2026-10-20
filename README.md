# Smart Tourism & Local Culture Discovery Platform

DBMS college project. Frontend: HTML + CSS (no JavaScript, no frameworks).
Backend: Python Flask + Jinja2. Database: MySQL via `mysql-connector-python`.

## 1. Setup on Windows (VS Code + MySQL Workbench)

**Needed once:** Python 3.10+ (tick "Add Python to PATH" in the installer), MySQL Server 8.0.16 or newer, MySQL Workbench, VS Code.

1. **Extract** the ZIP and open the `SmartTourism` folder in VS Code (`File > Open Folder`).
2. **Create the database.** Open MySQL Workbench, connect to your local server, then
   `File > Open SQL Script...` > choose `database.sql` > click the lightning-bolt button (Execute).
   Refresh the schemas panel: you should see `smart_tourism` with 11 tables.
3. **Set your MySQL password.** Open `config.py` and replace `YOUR_MYSQL_PASSWORD` with your own root password.
   (Alternative that keeps the password out of the file: in the terminal run `set DB_PASSWORD=yourpassword` before step 5.)
4. **Install packages.** In VS Code open a terminal (`Terminal > New Terminal`) and run:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   If PowerShell blocks `activate`, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use Command Prompt.
5. **Run the website:**
   ```
   python app.py
   ```
6. Open **http://127.0.0.1:5000** in your browser.

### Demo accounts (created by database.sql)

| Role     | Email                    | Password     |
|----------|--------------------------|--------------|
| Admin    | admin@smarttourism.com   | Admin@123    |
| Business | meera@example.com        | Business@123 |
| Tourist  | aarav@example.com        | Tourist@123  |

(`rajesh@example.com` is also a Business user; `sneha@example.com` and `john@example.com` are tourists, all with the passwords above for their role.)

### Common problems

| Message | Fix |
|---|---|
| "Database problem" page | MySQL is not running, or the password in `config.py` is wrong, or `database.sql` was not imported. |
| `ModuleNotFoundError: mysql` | Activate the venv and run `pip install -r requirements.txt` again. |
| `Unknown database 'smart_tourism'` | Run `database.sql` in Workbench (step 2). |
| Hindi/Marathi text shows as `?` | Re-run `database.sql` (it uses utf8mb4) and make sure it was run as a whole script. |

## 2. Project structure

```
SmartTourism/
  app.py            all Flask routes and SQL queries
  config.py         database settings and secret key
  database.sql      schema + sample data
  requirements.txt
  templates/        Jinja2 HTML pages (base.html is the shared layout)
  static/css/style.css
  static/images/    illustrated SVG images + fallback.svg
```

## 3. Pages and routes

| Page | URL | Template |
|---|---|---|
| Home | `/` | index.html |
| Destinations / detail | `/destinations`, `/destination/<id>` | destinations.html, destination_detail.html |
| Attractions (search + filter) / detail | `/attractions`, `/attraction/<id>` | attractions.html, attraction_detail.html |
| Culture & Heritage | `/culture` | culture.html |
| Local Specialities | `/specialities` | specialities.html |
| Local Businesses | `/businesses` | businesses.html |
| Reviews & Ratings | `/reviews` | reviews.html |
| Search results | `/search?q=` | search_results.html |
| Login / Register / Logout | `/login`, `/register`, `/logout` | login.html, register.html |
| User profile | `/profile` | profile.html |
| About | `/about` | about.html |
| Admin dashboard | `/admin` | admin_dashboard.html |
| Admin CRUD: attractions | `/admin/attractions`, `/add`, `/<id>/edit`, `/<id>/delete` | admin_attractions.html, admin_attraction_form.html |
| Admin CRUD: businesses | `/admin/businesses`, `/add`, `/<id>/edit`, `/<id>/delete` | admin_businesses.html, admin_business_form.html |
| Admin: delete reviews / users | buttons on the dashboard | admin_dashboard.html |
| Language switch | `/language/<code>` (en, hi, mr) | (redirects back) |

## 4. Database design

**Core tables (from the project requirement):** `Users`, `Attractions`, `AttractionTranslations`, `Reviews`.
**Supporting tables:** `Destinations`, `DestinationTranslations`, `CultureItems`, `CultureTranslations`,
`Specialities`, `SpecialityTranslations`, `Businesses`.

Relationships (all 1 : N, enforced with foreign keys):

- Users -> Attractions (`CreatorID`), Users -> Reviews (`UserID`), Users -> Businesses (`OwnerID`)
- Destinations -> Attractions, CultureItems, Specialities, Businesses (`DestinationID`)
- Attractions -> AttractionTranslations, Attractions -> Reviews (`AttractionID`)
- Destinations / CultureItems / Specialities -> their translation tables

Added to the requirement tables: `Attractions.ImageURL` and `Attractions.DestinationID` (needed for the Destinations page).

Constraints: `Email` UNIQUE; `Rating` CHECK 1-5; one review per user per attraction (UNIQUE on `UserID, AttractionID`);
one translation per language (UNIQUE on item + `LanguageCode`); latitude/longitude range checks.
`ON DELETE CASCADE` removes translations/reviews with their attraction; `ON DELETE RESTRICT` stops deleting a user who still owns attractions or businesses.

**How multi-language works:** each translated query joins the translation table twice - once for the selected language and once for English - and uses `COALESCE`, so a missing Hindi/Marathi text falls back to English.

## 5. Security notes (good viva points)

- Passwords are stored only as salted PBKDF2-SHA256 hashes (`generate_password_hash`) and checked with `check_password_hash`.
- All SQL uses `%s` placeholders (parameterised queries), which prevents SQL injection.
- Jinja2 auto-escapes output, so review text cannot inject HTML.
- Login state is kept in the Flask `session` (signed cookie). Admin pages use the `admin_required` decorator.
- Redirect targets (`next`) are checked so they can only point inside the site.
- Known limitation (acceptable for a college project, mention it if asked): forms do not use CSRF tokens. Flask-WTF would add them.
- Before submitting/deploying, change `SECRET_KEY` in `config.py` and turn off `debug=True` in `app.py`.

## 6. About the images

No internet photos are bundled. `static/images/` contains locally generated illustrations (one per attraction, destination, culture item, speciality and business) plus `fallback.svg`, which is shown automatically if any image file is missing.
To use real photos: copy a photo into `static/images/` (for example `ajanta-caves.jpg`), then in Workbench run
`UPDATE Attractions SET ImageURL = 'images/ajanta-caves.jpg' WHERE AttractionID = 1;`
or edit the attraction in the admin panel. A full web address (`https://...`) also works in the Image field.

## 7. Scope notes

- Destinations, culture items and specialities are read-only on the website (managed in SQL); full admin CRUD is provided for attractions (with Hindi/Marathi text), businesses, reviews and users.
- Culture/speciality titles are stored in English (they are proper names); their descriptions are translated.
- The interface labels (menus, buttons) are English; the database content changes with the language selector.
- No payment, booking or live GPS features, as requested. The "View on map" link only opens the stored coordinates in Google Maps.
