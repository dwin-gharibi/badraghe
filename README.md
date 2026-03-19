# Badraghe - Online Travel Ticket Selling Platform

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white" />
  <img alt="Django" src="https://img.shields.io/badge/Django-4.0+-green.svg?logo=django&logoColor=white" />
  <img alt="React" src="https://img.shields.io/badge/React-18.0+-61DAFB.svg?logo=react&logoColor=white" />
  <img alt="MySQL" src="https://img.shields.io/badge/MySQL-5.7+-orange.svg?logo=mysql&logoColor=white" />
  <img alt="Docker" src="https://img.shields.io/badge/Docker-20.10+-2496ED.svg?logo=docker&logoColor=white" />
  <img alt="GitLab CI/CD" src="https://img.shields.io/badge/GitLab-CI/CD-FC6D26.svg?logo=gitlab&logoColor=white" />
</p>


Welcome to **Badraghe**, a comprehensive online booking platform that allows users to search, reserve, and manage tickets seamlessly. Whether it's **airline tickets**, **train journeys**, or **bus rides**, Badraghe ensures real-time availability, secure transactions, and a user-friendly interface.

🌐 **Live Demo:** [Badraghe Platform](https://badraghe.dwin.codes/)

---

## 🚀 New Features and Integrations

### 📡 **API Endpoint**
- **Base URL**: [https://api.badraghe.dwin.codes/](https://api.badraghe.dwin.codes/)  
- A robust API powering backend services for ticket bookings, reservations, payments, and notifications.

![API Endpoint](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe_API.png)

---

### 🔁 **GitLab CI/CD Integration**
Seamlessly deploy, migrate, and seed the project with integrated **GitLab CI/CD pipelines** for continuous delivery.

![GitLab CI/CD](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe_CI_CD.png)

---

### 📊 **Badraghe Metabase Dashboard**
Monitor and analyze operational metrics (ticket sales, user activity, performance) in one centralized Metabase dashboard.  
🔗 [Metabase Dashboard](https://metabase.badraghe.dwin.codes/)

![Metabase](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe-Metabase2.png)

---

### 🛠️ **PhpMyAdmin Access**
Use **PhpMyAdmin** for database administration tasks like migrations, queries, and data validations.  
🔗 [PhpMyAdmin](https://phpmyadmin.badraghe.dwin.codes/)

![PhpMyAdmin](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe-Phpmyadmin.png)

---

### 📦 **CLI Seeders for Database Setup**
Seed the database with realistic dummy data using Badraghe’s **Python CLI utility**.

![CLI Seeders](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/CLI_Seeders.png)

---

### 🧩 **Badraghe Updamus Monitoring**
Monitor the health of all deployed services in real-time using **Updamus**.  
🔗 [Updamus Monitoring](https://my.updamus.com/symlink/37fc914f-f097-4925-8e2d-769fb4d6cecc)

![Updamus](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe-Updamus.png)

---

## 🌟 **Platform Features**

### 🧾 **Core Features**
- **Real-Time Ticket Booking**: Up-to-date ticket availability and instant reservation confirmations.
- **Secure Transactions**: Built-in integration with secure payment gateways like Zarinpal.
- **Multi-Transport Support**: Book across buses, trains, and airlines on one platform.
- **Flexible Reservations**: Supports one-way, round-trip, and multi-city bookings.

### 📋 **Administrator Features**
- Monitor ticket sales with live dashboards.
- Manage routes, schedules, and dynamic pricing models.
- Automate notifications for payment reminders, cancellations, and changes.

### 🖥️ **Developer Features**
- **RESTful API Support** for frontend integrations.
- GitLab CI/CD for continuous testing and deployment.
- Docker Compose files to replicate production-ready environments.

---

## **System Architecture**

### 1. **API Backend (`badraghe-api`)**
- Manages business logic, ticket processing, and API endpoints.
- Key Features:
  - RESTful API integration.
  - Authentication and role-based access control.
  - Processes secure payment transactions.

---

### 2. **Database (`badraghe-db`)**
- Central repository for handling tickets, reservations, and payments.
- Uses **MySQL** for relational data consistency.

---

### 3. **Entity Relationship Models (`badraghe-er`)**
- Provides the structure for the database, ensuring a clear relationship between entities:
  - Users
  - Tickets
  - Reservations
  - Transactions

---

### 4. **User Interface (`badraghe-ui`)**
- Fully responsive **React.js-based frontend** optimized for travelers and admin users.

---

## 📋 **Entity Relationship Diagram (ERD)**

The following ER diagram showcases the relationships between users, tickets, reservations, and transactions:

![ERDiagram](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/Badraghe-ERD.png)

---

## 🚀 **Setup & Usage**

### 🌐 **Prerequisites**
Before setting up the platform, ensure the following tools are installed:
- ✅ **Docker & Docker Compose**
- ✅ **Python 3.8+**
- ✅ **pip** (for Python dependencies)

---

### 🚧 **Backend Setup**
```bash
# Clone the Badraghe repository
git clone https://github.com/dwin-gharibi/badraghe.git
cd badraghe

# Navigate to the API Backend
cd badraghe-api

# Setup the Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create the `.env` file for backend configurations:

```plaintext
DATABASE_URL=mysql://user:password@mysql_server/badraghe_main
PAYMENT_GATEWAY_KEY=your_zarinpal_key
SMTP_SERVER=smtp.example.com
SMTP_USER=username
SMTP_PASSWORD=password
```

---

### 🐳 **Start Services with Docker**
```bash
# For MySQL and PhpMyAdmin
docker-compose up -d
```

Access PhpMyAdmin at [localhost:8080](http://localhost:8080) with:
- **Server**: `mysql`
- **Username**: `user`
- **Password**: `password`

---

### 🔬 **Testing the Project (`test.py`)**

Run tests using the **unittest** framework to validate database migrations, data constraints, and transactions.

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest test.py
```

---

## 📊 **Monitoring Tools**

### **1. Metabase Dashboard**  
- Track business performance metrics like customer bookings and revenue.

### **2. Updamus Service Monitoring**  
- Real-time service uptime monitoring.

### **3. GitLab CI/CD Pipelines**  
- Continuous deployment for backend and frontend builds.

---

## 🤝 **Contributing**
We welcome contributions to make **Badraghe** better! Steps to contribute:
1. **Fork the Repository**
2. Create a **feature branch**
3. Submit a PR for review.

---

## 📧 **Support and Contact**

For questions, issues, or feature requests:
- Open a GitHub Issue: [Badraghe Issues](https://github.com/dwin-gharibi/badraghe/issues)

---

![Badraghe Logo](https://cloud-data.s3.ir-thr-at1.arvanstorage.ir/badraghe-logo.png)

**Thank you for choosing Badraghe! Simplify your travel ticketing today.**