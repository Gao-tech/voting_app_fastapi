# User-Friendly Voting System with Python FastAPI

Inspired by my experiences at Kåren, where I observed challenges in student voting participation, this project aims to address usability concerns in voting systems. The existing tools often discouraged engagement due to their complexity, despite significant investments. This repository presents a voting system built with Python’s FastAPI framework, focusing on simplicity, security, and scalability.

This project also provided a valuable opportunity to learn about data modeling and backend architecture while working with real-world business requirements.

---

## 🏗️ Project Overview

This voting system was designed to prioritize:
- **Ease of Use:** A user-centric interface to simplify voting processes.
- **Security:** Ensuring safe and verified participation.
- **Efficient Data Handling:** Optimized for scalability and performance.

### Key Features
- **User Authentication:** Secure access using JWT to ensure verified voting.
- **Real-Time Voting Feedback:** Immediate vote tallying and result visualization.
- **Business Requirements Logic:** 
  - Users can vote for multiple positions (up to 5).
  - Applicants can apply for up to two positions with priority settings.
- **Data Modeling:** Structured relationships for scalability (e.g., applicants, users, positions, votes).

---

## 🛠️ Implementation Details

### Tools and Technologies
- **[FastAPI](https://fastapi.tiangolo.com/):** Chosen for its performance and asynchronous capabilities, enabling smooth user interactions under high load.
- **[SQLModel](https://sqlmodel.tiangolo.com/):** Built on SQLAlchemy, used for defining complex database relationships.
- **PostgreSQL:** A robust and scalable database solution for secure data management.
- **Pydantic:** Essential for data validation and modeling to align with business requirements.

### Architecture Highlights
- **FastAPI & Async Processing:** Efficient handling of concurrent requests for better performance.
- **Data Persistence:** Complex table relationships modeled using SQLModel, ensuring data integrity.
- **Data Validation:** Pydantic models structured data consistently across the system.

---

## 📂 File Structure

📂 voting_app_fastapi
├── 📁 app
│   ├── 📁 routers            # API route modules
│   │   ├── applicant.py      # Applicant-related endpoints
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── user.py           # User-related endpoints
│   │   ├── vote.py           # Voting-related endpoints
│   ├── config.py             # Configuration settings
│   ├── db.py                 # Database connection setup
│   ├── main.py               # Application entry point
└── requirements.txt          # Python dependencies


---

## 🔍 Testing, Results, and Future Plans

### API Testing
- **Postman:** Used for endpoint verification and ensuring expected responses during development.

### Current Status
- Backend-only implementation. The application provides robust API functionality for secure voting and real-time feedback.

### Future Scope
- **Frontend Development:** Build a React-based frontend to enhance usability and accessibility.
- **Advanced Analytics:** Add analytics for insights into user engagement and voting trends.

---

## 🚀 Lessons Learned

- **Data Modeling:** Designing relationships to meet complex business requirements.
- **Backend Architecture:** Developing scalable, secure, and efficient backend logic.
- **Framework Comparison:** 
  - **Flask:** Previously used for a simpler complaint submission system. 
  - **FastAPI:** Selected for this project due to its performance and scalability for complex systems.

---

## 📂 Access the Code

The code for this voting system is available in this repository. While it's a work in progress, it demonstrates the foundational structure and logic behind the application. Feel free to explore, contribute, or provide feedback!
