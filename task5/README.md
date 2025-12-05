# 🚀 **Advanced Data Generation & Analytics System**

A fully-featured, professional-grade data engineering project showcasing realistic data generation, anomaly detection, automated reporting, and a modern analytics dashboard.

This README has been **expanded, renamed, and rewritten** to match a polished portfolio-ready project.

---

# 🌐 **Project: AetherMine Data Engineering Platform**

*A next-generation system for synthetic data generation + analytics, suitable for real production workflows.*

![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Apps Script](https://img.shields.io/badge/Google%20Apps%20Script-Automation-blue)
![React](https://img.shields.io/badge/React-Frontend-blue)
![Data%20Engineering](https://img.shields.io/badge/Data%20Engineering-ETL-orange)

---

# 📖 **Table of Contents**

* Overview
* Key Features
* Architecture
* Google Sheets Generator
* Data Analytics Dashboard
* Screenshots
* How to Install
* How to Use
* Folder Structure
* Future Improvements
* Author

---

# 🌍 **Overview**

**AetherMine** is a completely modular data engineering system consisting of:

### **1️⃣ Data Generator (Google Sheets + Apps Script)**

Produces highly realistic mine-production datasets with:

* smoothing
* seasonal effects
* anomaly events
* uniform/normal distributions
* correlations and trends

### **2️⃣ Interactive Web Dashboard (React)**

Used to import data, calculate statistics, detect anomalies, visualize trends, and generate a full PDF report.

This project demonstrates **ETL thinking, statistical analysis, data visualization, and automation** — perfect for portfolio use.

---

# ✨ **Key Features**

## 🔧 **Part I — Google Sheets Data Generator**

* Custom mine names
* Adjustable date range
* Uniform & Normal distributions
* Realistic smoothing & correlations
* Weekly production modifiers
* Trend amplification
* Up to 4 anomaly events (spikes/drops)
* Gaussian-based event curves
* Auto-updating charts
* CSV export

---

## 📊 **Part II — Web Analytics Dashboard**

* Import CSV
* Compute mean, median, std dev, IQR
* Anomaly detection (IQR, MA, z-score, Grubbs)
* Line, bar & stacked charts
* Polynomial trendlines (1–4)
* Fully responsive UI
* PDF report generation

---

# 🏗️ **Architecture**

```
Google Sheet (Generator)
      ↓ CSV Export
React Dashboard → Statistical Analysis → PDF Report
```

---

# 📑 **Google Sheets Generator**

Uses Google Apps Script to simulate realistic industrial output with:

* random generation + constraints
* weekly modulation
* anomaly curve injection
* multi-mine support

---

# 📈 **Data Analytics Dashboard**

Technologies:

* React + Vite
* Chart.js / Recharts
* jsPDF

---

# 🖼️ **Screenshots**

![Screenshot 1](brave_screenshot_localhost (3).png)
![Screenshot 2](brave_screenshot_localhost (4).png)

---

# 🔌 **How to Install**

### Google Sheets

1. Open Sheet → Extensions → Apps Script
2. Paste full code into `Code.gs`
3. Save & reload

### Dashboard

```bash
npm install
npm run dev
```

---

# ▶️ **How to Use**

### Generator

1. Set parameters
2. Click Generate Data
3. Export CSV

### Dashboard

1. Upload CSV
2. View charts & anomalies
3. Export PDF report

---

# 📁 **Folder Structure**

```
/
├── Code.gs
├── README.md
├── brave_screenshot_localhost (3).png
├── brave_screenshot_localhost (4).png
├── src/
└── public/
```

---

# 🔮 **Future Improvements**

* API sync
* Real-time dashboard streaming
* ML-based prediction

---

# 👤 **Author**

**Khaled Soliman** — Data Engineer & Automation Developer.
