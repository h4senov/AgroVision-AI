# 🚜 Agrovision AI - Ağıllı Ferma İdarəetmə Sistemi

**Agrovision AI**, müasir kənd təsərrüfatı texnologiyalarını bir araya gətirən, fermerlər üçün nəzərdə tutulmuş rəqəmsal idarəetmə platformasıdır. Layihə həm korporativ tanıtım (Landing Page), həm də daxili idarəetmə paneli (Dashboard) hissələrindən ibarətdir.

## 📊 Dashboard Analitikası
Layihənin əsas gücü onun məlumat vizuallaşdırma qabiliyyətindədir. Aşağıdakı şəkildən göründüyü kimi, sistem fermerə kritik qərarlar vermək üçün real vaxt rejimində datalar təqdim edir:

* **Aktiv Monitorinq:** Sahələrin sayı, orta temperatur (24°C) və torpaq nəmliyi (68%) kimi göstəricilər anlıq izlənilir.
* **Xəbərdarlıq Sistemi:** Diqqət tələb edən hallar (Xəbərdarlıqlar: 3) qırmızı rənglə vurğulanır.
* **Trend Analizi:** Temperaturun gün ərzində dəyişməsi və torpağın pH balansı qrafiklərlə təhlil olunur.



## 🌟 Əsas Funksiyalar

### 1. **Qonaqlar üçün (Landing Page)**
* **Haqqımızda:** Şirkətin ümumi məlumatları və hədəfləri.
* **Karyera:** Aktiv vakansiyaların izlənilməsi.
* **İstehsalat:** Cihazlarımız və keyfiyyət standartlarımız haqqında məlumat.
* **Media:** Ən son xəbərlər və yeniliklər.

### 2. **Fermerlər üçün (User Panel)**
* **Dashboard:** Bütün təsərrüfatın ümumi mənzərəsi.
* **Sahə və Bitki İdarəetməsi:** Əkinlərin və sahələrin rəqəmsal qeydiyyatı.
* **Sensorlar və Suvarma:** IoT cihazlarından gələn nəmlik və temperatur datalarına əsasən suvarma idarəsi.
* **Anbar:** Toxum, gübrə və texniki avadanlıqların inventar qeydiyyatı.

### 3. **İdarəetmə (Admin Panel)**
* **Məhsul İdarəetməsi:** Yeni məhsulların və cihazların əlavə edilməsi.
* **Xəbər və Vakansiya:** Saytın məzmununun admin tərəfindən idarə olunması.
* **Profil İdarəsi:** Admin üçün xüsusi sürətli keçid linkləri.

## 🛠️ Texnologiyalar
* **Backend:** Python / Django
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
* **Vizuallaşdırma:** Chart.js
* **İkonlar:** FontAwesome 6
* **Dillər:** Django i18n (Azərbaycan dili dəstəyi ilə)



## 🚀 Quraşdırma
```bash
# Repozitoriyanı yükləyin
git clone https://github.com/h4senov/AgroVision-AI.git

# Virtual mühit yaradın
python -m venv venv
smartfarm_env\Scripts\activate

# Kitabxanaları yükləyin
pip install -r requirements.txt

# Serveri başladın
python manage.py runserver
