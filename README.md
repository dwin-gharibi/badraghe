# Badraghe - Online Travel Ticket Selling Platform

**Badraghe** is a modern and dynamic platform built for efficiently managing and selling travel tickets online. Whether you're booking a **plane ticket**, a **train ride**, or a **bus journey**, Badraghe provides a streamlined experience for **travelers** and **transport carriers** alike. From browsing schedules to making secure payments, Badraghe aims to simplify the travel booking process for all.

---

## 🌟 **Key Features**

### **For Travelers:**
1. **Search and Book Tickets**
   - Quickly search for available travel routes across multiple modes of transportation.
   - Browse schedules, prices, and seat availability in real-time.

2. **Detailed Itineraries**
   - Get up-to-date information about departure and arrival times, route stops, and travel durations.

3. **Secure Bookings**
   - Reserve and purchase tickets with confidence using secure payment gateways like **Zarinpal**.

4. **User-Friendly Dashboard**
   - Manage your travel history, review ticket reservations, and receive trip reminders.

5. **Multi-Device Access**
   - Seamlessly book tickets on desktop, tablet, or mobile devices with ease.

6. **Multi-Transport Integration**
   - Search for tickets across buses, trains, and airlines, all on the same platform.

---

### **For Transportation Companies:**
1. **Route and Schedule Management**
   - Create and manage route schedules for buses, airlines, or trains.
   - Set pricing levels (economy, business, etc.) and enable flexible seat availability.

2. **Real-Time Booking System**
   - Eliminate overbooking with real-time updates on availability.
   - Automatically block reserved and purchased seats.

3. **Revenue and Analytics**
   - Get detailed reports on ticket sales, customer trends, and route performance.
   - Track financial summaries, cancellations, and refunds effortlessly.

4. **Customer Relationship Management (CRM)**
   - Manage customer profiles and inquiries with an integrated CRM tool.
   - Communicate directly with travelers about any updates or changes.

5. **Promotional Features**
   - Launch discounts or loyalty programs through the platform to attract more travelers.

6. **Scalability**
   - Designed to handle high demand during busy travel periods or promotional campaigns.

---

## 🤔 **Who Can Benefit from Badraghe?**

### **Travelers:**
- Book transportation tickets for buses, airlines, trains, and more on one platform.
- View schedules, compare prices, and choose the option that works best for you.

### **Transportation Companies:**
- Manage your ticket inventory, revenue, and routes without requiring additional technical knowledge.
- Scale your operations with support for advanced booking systems.

### **Travel Agencies:**
- Integrate the Badraghe platform into your agency for seamless customer bookings and reservation handling.

---

## 🤖 **Why Choose Badraghe?**

- **Comprehensive Travel Platform:** Offers multi-transport ticketing for all major travel options.
- **Ease of Use:** Intuitive design to simplify ticket browsing and purchasing.
- **Secure Transactions:** Ensures all payments and customer details are securely processed and encrypted.
- **Revenue Insights:** Gain clear visibility into your business's performance with reporting tools.
- **Customer Support:** Built-in tools ensure easy communication and satisfaction.
- **Scalability:** Support for routes, companies, and customers across the globe.

---

## ⚙️ **System Architecture**

### 1. **Backend API (Branch: `badraghe-API`)**
- Built with **Python** (Flask) to ensure secure and fast API services.
- Handles:
   - User authentication and roles (traveler/operator/admin).
   - Travel route management, ticket bookings, and CRM.
   - Payment integration (e.g., Zarinpal).
   - Notifications for upcoming trips and booking details.

### 2. **Database (Branch: `badraghe-DB`)**
- **Type:** Relational database (PostgreSQL).
- Maintains:
   - A scalable schema to store routes, seat availability, and prices.
   - Transactional consistency for bookings, payments, and refunds.

### 3. **User Interface (Branch: `badraghe-UI`)**
- Built with a combination of **React.js** and **TailwindCss**.
- Provides:
   - A sleek design for browsing routes and booking tickets.
   - Convenient dashboards for both customers and transportation companies.
   - Mobile-first design, ensuring responsiveness on all devices.

---

## 📚 **Core Booking Features**

### **1. Multi-Modal Ticketing**
- Integration of various transport modes (buses, trains, airlines).

### **2. Search Functionality**
- Search by route, date, time, or transport mode.
  
### **3. Reservation and Payment**
- Hold tickets for up to 10 minutes for payment processing.
- Simplified payment process with reliable gateways.

### **4. Notifications**
- Get reminders for ticket payment, departure times, or cancellations.
- Email notifications after successful bookings.

### **5. Discounts and Loyalty**
- Implement dynamic pricing models and offer discounts for early booking.

### **6. Real-Time Updates**
- Ensure ticket availability and pricing remain accurate with live updates.

---

## 🚀 **Getting Started**

### Prerequisites
- **Backend:** Python environment (3.9 or later).
- **Frontend:** Node.js and npm installed.
- **Database:** PostgreSQL version 13 or later.

### Installation

#### Step 1: Clone the Repository
```bash
git clone https://github.com/dwin-gharibi/badraghe.git
cd badraghe
```

#### Step 2: Backend Setup
```bash
cd badraghe-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure Environment Variables
```dotenv
DATABASE_URL=your_database_url
PAYMENT_GATEWAY_KEY=your_payment_key
EMAIL_SMTP=your_smtp_settings
```

#### Step 4: Frontend Installation
```bash
cd badraghe-ui
npm install
npm start
```

---

## 🧑‍💻 **Developer Guide**

### Project Structure
- **`badraghe-api/`**: Backend services for route and ticket management.
- **`badraghe-db/`**: Database schema files and management scripts.
- **`badraghe-ui/`**: React.js-based frontend for users and operators.

### Testing

- Backend:
  ```bash
  cd badraghe-api
  pytest
  ```

- Frontend:
  ```bash
  cd badraghe-ui
  npm test
  ```

---

## 🤝 **Contributing**

We welcome contributions. Here’s how you can help:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Submit a pull request with a clear description.

---

## 📞 **Contact**
- GitHub Issues: [Submit a Ticket](https://github.com/dwin-gharibi/badraghe/issues)

**Thank you for choosing Badraghe! Simplify travel ticketing today.**