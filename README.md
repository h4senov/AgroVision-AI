<div align="center">

<img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white"/>
<img src="https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white"/>
<img src="https://img.shields.io/badge/Chart.js-FF6384?style=for-the-badge&logo=chartdotjs&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>

</div>

---

> 🌐 **Language / Dil:**
> [🇦🇿 Azərbaycan dili](#-agrovision-ai---ağıllı-ferma-idarəetmə-sistemi) · [🇬🇧 English](#-agrovision-ai---smart-farm-management-system)

---

# 🇦🇿 AgroVision AI — Ağıllı Ferma İdarəetmə Sistemi

**AgroVision AI** müasir kənd təsərrüfatı texnologiyalarını bir platformada birləşdirən rəqəmsal ferma idarəetmə sistemidir. Sistem həm korporativ tanıtım (Landing Page), həm də daxili idarəetmə paneli (Dashboard) hissələrindən ibarətdir.

---

## 📸 Ekran görüntüləri

| Dashboard | Mobil Görünüş |
|-----------|--------------|
| <img width="500" src="https://github.com/user-attachments/assets/f35ed2d8-353d-487f-9810-c20a02b39d0f" /> | <img width="200" src="https://github.com/user-attachments/assets/dece4e6b-aee9-4f21-a7f2-3e127c764a0e" /> |

## 🌟 Əsas Funksiyalar

### 🏠 Qonaq (Landing Page)
- **Haqqımızda** — şirkət məlumatları və hədəflər
- **Karyera** — aktiv vakansiyalar
- **Media** — xəbərlər və yeniliklər
- **Əlaqə** — əlaqə formu

### 👨‍🌾 Fermer Paneli (Dashboard)
- **Dashboard** — bütün təsərrüfatın real vaxt mənzərəsi
- **Sahə İdarəetməsi** — sahələrin xəritəsi, pH, torpaq növü
- **Bitki İdarəetməsi** — əkinlər, böyümə mərhələsi, yığım proqnozu
- **Suvarma** — planlaşdırılmış və tamamlanmış suvarmalar, IoT inteqrasiyası
- **Sensorlar** — IoT cihazlarından real vaxt data
- **Anbar** — toxum, gübrə, avadanlıq inventarı
- **Hava** — sahə üzrə hava proqnozu və tarixi məlumatlar
- **Canlı Status Widget** — real vaxt göstəriciləri (sahələr, sensorlar, su istifadəsi)

### ⚙️ Admin Paneli
- Xəbər və vakansiya idarəetməsi
- Məhsul kataloqu
- İstifadəçi sessiya monitorinqi

---

## 🛠️ Texnologiyalar

| Qat | Texnologiya |
|-----|-------------|
| Backend | Python 3.13, Django 5.x |
| Frontend | HTML5, CSS3, JavaScript ES6+ |
| UI Framework | Bootstrap 5.3 |
| Qrafiklər | Chart.js |
| İkonlar | FontAwesome 6 |
| Email | Gmail SMTP |
| Deploy | PythonAnywhere |
| i18n | Django i18n (AZ / EN) |

---

## 🚀 Quraşdırma

```bash
# 1. Reponu yükləyin
git clone https://github.com/h4senov/AgroVision-AI.git
cd AgroVision-AI

# 2. Virtual mühit yaradın
python -m venv smartfarm_env

# Windows
smartfarm_env\Scripts\activate

# Linux / macOS
source smartfarm_env/bin/activate

# 3. Asılılıqları yükləyin
pip install -r requirements.txt

# 4. Layihə qovluğuna keçin
cd smart_farm

# 5. .env faylı yaradın
cp .env.example .env
# .env faylında EMAIL_HOST_USER və EMAIL_HOST_PASSWORD yazın

# 6. Verilənlər bazasını qurun
python manage.py migrate

# 7. Statik faylları toplayın
python manage.py collectstatic

# 8. Serveri başladın
python manage.py runserver
```

---

## ⚙️ Mühit Dəyişənləri

`.env` faylında aşağıdakıları yazın:

```env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📁 Layihə Strukturu

```
AgroVision-AI/
└── smart_farm/
    ├── core/          # Dashboard, ana səhifə, API
    ├── fields/        # Sahə idarəetməsi
    ├── plants/        # Bitki idarəetməsi
    ├── irrigation/    # Suvarma sistemi
    ├── sensors/       # IoT sensorlar
    ├── inventory/     # Anbar idarəetməsi
    ├── weather/       # Hava məlumatları
    ├── users/         # Auth, profil, sessiya
    ├── news/          # Xəbər sistemi
    ├── careers/       # Vakansiya sistemi
    ├── pages/         # Statik səhifələr
    ├── products/      # Məhsul kataloqu
    └── templates/     # HTML şablonları
```

---

## 👨‍💻 Müəllif

**h4senov** — [GitHub](https://github.com/h4senov)

---

---

# 🇬🇧 AgroVision AI — Smart Farm Management System

**AgroVision AI** is a digital farm management platform that brings together modern agricultural technologies in one place. The system includes both a corporate landing page and a full-featured internal dashboard.

---

## 🌟 Key Features

### 🏠 Guest (Landing Page)
- **About** — company info and goals
- **Careers** — active job listings
- **Media** — latest news
- **Contact** — contact form

### 👨‍🌾 Farmer Dashboard
- **Dashboard** — real-time overview of the entire farm
- **Field Management** — field map, pH levels, soil type
- **Plant Management** — crops, growth stages, harvest forecasting
- **Irrigation** — scheduled and completed irrigation, IoT integration
- **Sensors** — real-time data from IoT devices
- **Inventory** — seeds, fertilizers, equipment tracking
- **Weather** — per-field weather forecasts and historical data
- **Live Status Widget** — real-time indicators (fields, sensors, water usage)

### ⚙️ Admin Panel
- News and vacancy management
- Product catalog
- User session monitoring

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.13, Django 5.x |
| Frontend | HTML5, CSS3, JavaScript ES6+ |
| UI Framework | Bootstrap 5.3 |
| Charts | Chart.js |
| Icons | FontAwesome 6 |
| Email | Gmail SMTP |
| Deployment | PythonAnywhere |
| i18n | Django i18n (AZ / EN) |

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/h4senov/AgroVision-AI.git
cd AgroVision-AI

# 2. Create virtual environment
python -m venv smartfarm_env

# Windows
smartfarm_env\Scripts\activate

# Linux / macOS
source smartfarm_env/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Navigate to project directory
cd smart_farm

# 5. Create .env file
cp .env.example .env
# Fill in EMAIL_HOST_USER and EMAIL_HOST_PASSWORD

# 6. Run migrations
python manage.py migrate

# 7. Collect static files
python manage.py collectstatic

# 8. Start the server
python manage.py runserver
```

---

## ⚙️ Environment Variables

Create a `.env` file with the following:

```env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 📁 Project Structure

```
AgroVision-AI/
└── smart_farm/
    ├── core/          # Dashboard, home, API endpoints
    ├── fields/        # Field management
    ├── plants/        # Plant management
    ├── irrigation/    # Irrigation system
    ├── sensors/       # IoT sensors
    ├── inventory/     # Inventory management
    ├── weather/       # Weather data
    ├── users/         # Auth, profile, sessions
    ├── news/          # News system
    ├── careers/       # Vacancy system
    ├── pages/         # Static pages
    ├── products/      # Product catalog
    └── templates/     # HTML templates
```

---

## 📊 Language Stats

![HTML](https://img.shields.io/badge/HTML-44.8%25-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-22.5%25-1572B6?style=flat-square&logo=css3&logoColor=white)
![Python](https://img.shields.io/badge/Python-18.3%25-3776AB?style=flat-square&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-14.4%25-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

---

## 👨‍💻 Author

**h4senov** — [GitHub](https://github.com/h4senov)

---

<div align="center">
  <sub>Built with ❤️ for farmers · 2026</sub>
</div>
