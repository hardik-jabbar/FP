# (optional) store the key safely instead of hard-coding
echo "GEMINI_API_KEY=AIzaSyBPCkHntDq4VU5G4QlUD2rGr2iuuh2Il_Y" >> .env

npm run dev   # or  npm start

Product Requirements Document (PRD) & Minimum Viable Product (MVP) Outline
Project Name: FarmPower
Version: 1.0 (Initial Release)
Date: 2024-07-29
1. Project Overview & Goals
FarmPower is an integrated digital platform designed to empower farmers and agricultural stakeholders with modern tools and technologies. It offers a comprehensive suite of features including equipment and parts marketplaces, GPS tracking for field planning, crop profitability calculation, service scheduling, and an AI-powered farming assistant. The primary goal is to enhance agricultural productivity, optimize resource management, and foster a connected farming community.
Key Goals:
Enhance Efficiency: Streamline farming operations through digital tools.
Improve Profitability: Provide data-driven insights for better decision-making.
Facilitate Commerce: Create robust marketplaces for agricultural equipment and parts.
Foster Connectivity: Enable seamless communication between users and service providers.
Provide Intelligence: Offer AI-powered assistance for farming-related queries.
2. User Roles & Personas
FarmPower supports distinct user roles with specific permissions and functionalities:
Farmer: The primary end-user. Buys/sells equipment/parts, plans fields, calculates crop profitability, schedules services, interacts with the AI assistant.
Dealer: Sells new/used equipment and parts. Manages listings, responds to inquiries.
Service Provider: Offers agricultural equipment maintenance and other services. Manages service bookings, updates status.
Admin: Manages user accounts, monitors platform activity, and oversees data.
3. Functional Requirements
3.1. User Management (Backend: farmpower_backend_v2/app/routers/users.py, app/models/user.py, app/schemas/user.py, app/services/user_service.py)
User Registration:
POST /users/register: Allows new users to create an account with email, password, full name, and role (default: Farmer).
Includes email existence check.
User Authentication (Login):
POST /users/login/token: Authenticates users with email and password, returning a JWT access token.
Checks for active and verified status.
User Profile Management:
GET /users/me: Retrieve details of the current logged-in user.
GET /users/{user_id}: Retrieve details of any user by ID (authorized for owner or Admin).
PUT /users/{user_id}: Update user details (authorized for owner or Admin).
Account Activation & Verification (OTP):
POST /users/request-verification-otp: Request an OTP for email verification.
POST /users/verify-otp: Verify OTP to activate/verify user account.
Admin User Management:
GET /users/: List all users (Admin only).
DELETE /users/{user_id}: Delete a user (Admin or user deleting their own account).
AdminService.ban_user(), AdminService.unban_user(): Ban/unban users.
3.2. Equipment Marketplace (Backend: farmpower_backend_v2/app/routers/tractors.py, app/models/tractor.py, app/schemas/tractor.py, app/services/tractor_service.py, app/services/s3_service.py)
Tractor Listing:
POST /tractors/: Authenticated users (Farmers, Dealers) can list new tractors for sale. Automatically sets owner_id.
Fields: name, brand, model, year, price, location, description, horsepower, condition.
Tractor Browsing & Search:
GET /tractors/: Browse all available tractors with pagination.
Filters: brand, location, min/max price, owner_id.
Tractor Details:
GET /tractors/{tractor_id}: View detailed information for a specific tractor.
Tractor Listing Management:
PUT /tractors/{tractor_id}: Update an existing tractor listing (authorized for owner or Admin).
DELETE /tractors/{tractor_id}: Remove a tractor listing (authorized for owner or Admin).
Image Upload:
POST /tractors/{tractor_id}/upload-image/: Upload images for a tractor listing (authorized for owner or Admin), stored on S3.
3.3. Parts Marketplace (Backend: farmpower_backend_v2/app/routers/parts.py, app/models/part.py, app/schemas/part.py, app/services/part_service.py, app/services/s3_service.py)
Part Listing:
POST /parts/: Authenticated users (Farmers, Dealers) can list new parts for sale. Automatically sets seller_id.
Fields: name, description, category, part_number, brand, compatibility (tractor brand/model), condition, price, quantity, location.
Part Browsing & Search:
GET /parts/: Browse all available parts with pagination.
Filters: category, tractor_brand, condition, min/max price, location, seller_id.
Part Details:
GET /parts/{part_id}: View detailed information for a specific part.
Part Listing Management:
PUT /parts/{part_id}: Update an existing part listing (authorized for seller or Admin).
DELETE /parts/{part_id}: Remove a part listing (authorized for seller or Admin).
Image Upload:
POST /parts/{part_id}/upload-image/: Upload images for a part listing (authorized for seller or Admin), stored on S3.
3.4. GPS Tracking & Field Planning (Frontend: FARMPOWER/gps-tracking.html, Backend: farmpower_backend_v2/app/routers/fields.py, app/models/field.py, app/models/land_usage_plan.py, app/schemas/field.py, app/schemas/land_usage_plan.py, app/services/field_service.py)
Field Management:
POST /fields/: Authenticated users can create new field entries.
GET /fields/: Get all fields owned by the current user.
GET /fields/{field_id}: Get details of a specific field (authorized for owner or Admin).
PUT /fields/{field_id}: Update field details (authorized for owner or Admin).
DELETE /fields/{field_id}: Delete a field (authorized for owner or Admin).
Fields: name, GeoJSON coordinates, area (hectares), crop info, soil type.
Land Usage Plan Management:
POST /fields/{field_id}/plans/: Create a new land usage plan for a specific field.
GET /fields/{field_id}/plans/: List all plans for a specific field.
GET /fields/plans/{plan_id}: Get details of a specific plan (authorized for owner of parent field or Admin).
PUT /fields/plans/{plan_id}: Update a plan (authorized for owner of parent field or Admin).
DELETE /fields/plans/{plan_id}: Delete a plan (authorized for owner of parent field or Admin).
Fields: plan name, plan details (JSON), start/end dates.
Map Visualization (Frontend):
Displays equipment locations (dummy data for now).
Displays field boundaries on a Mapbox map.
Allows drawing field boundaries using Mapbox GL Draw.
Controls for map layers (streets, satellite, outdoors), showing/hiding boundaries/equipment.
Lists active equipment and defined fields.
Zoom to equipment/field functionality.
3.5. Crop Calculator & Profitability Analysis (Frontend: FARMPOWER/crop-calculator.html (inferred), Backend: farmpower_backend_v2/app/routers/crops.py, app/routers/crop_calculator.py, app/models/crop.py, app/models/crop_calculator.py, app/schemas/crop.py, app/schemas/crop_calculator.py, app/services/crop_service.py)
Crop Entry Management:
POST /crops/: Authenticated users can create new crop entries with associated costs and yield projections.
GET /crops/: Get all crop entries created by the current user.
GET /crops/{crop_id}: Get details of a specific crop entry (authorized for owner or Admin).
PUT /crops/{crop_id}: Update crop entry details (authorized for owner or Admin).
DELETE /crops/{crop_id}: Delete a crop entry (authorized for owner or Admin).
Fields: crop name, variety, seed/fertilizer/pesticide/machinery/labor/other costs per hectare, expected yield, yield unit, market price per unit, notes, optional field ID link.
Profitability Calculation:
GET /crops/{crop_id}/profit: Calculate and return profitability analysis for a specific crop entry (authorized for owner or Admin).
POST /api/crop-profit/calculate: API for general profit calculation (frontend-driven, not tied to a saved crop entry).
Calculation History:
POST /api/crop-profit/save: Save a crop profit calculation to the database.
GET /api/crop-profit/history: Get history of crop profit calculations.
3.6. Service Scheduling (Backend: farmpower_backend_v2/app/routers/services.py, app/models/service_booking.py, app/schemas/service_booking.py, app/services/service_booking_service.py)
Service Booking:
POST /service-bookings/: Authenticated users can create new service bookings. Automatically sets user_id.
Fields: tractor ID (optional), service type, description, scheduled date, optional service provider ID, notes.
Booking Listing:
GET /service-bookings/:
Regular users see their own bookings.
Service Providers see bookings assigned to them (view_as_provider=true).
Admins see all bookings.
Booking Details:
GET /service-bookings/{booking_id}: Get details of a specific booking (accessible by customer, assigned provider, or Admin).
Booking Updates:
PUT /service-bookings/{booking_id}: Update booking details (customer can update if PENDING, provider can update status/notes, Admin can update any).
PATCH /service-bookings/{booking_id}/status: Update booking status (assigned provider or Admin; customer can cancel).
Booking Cancellation/Deletion:
DELETE /service-bookings/{booking_id}: Customer can cancel PENDING/CONFIRMED bookings; Admin can delete any.
3.7. Messaging (Backend: farmpower_backend_v2/app/routers/messages.py, app/models/message.py, app/schemas/message.py, app/services/message_service.py)
Send Message:
POST /messages/: Authenticated users can send messages to other users. Automatically sets sender_id and generates conversation_id.
Conversation Listing:
GET /messages/conversations/: Get a list of all conversations for the current user, showing the other participant and the last message.
View Messages in Conversation:
GET /messages/conversation/{conversation_id}: Get messages for a specific conversation (user must be a participant). Messages are returned oldest first.
Mark as Read:
POST /messages/conversation/{conversation_id}/read: Mark all messages in a conversation as read by the current user.
3.8. Notifications (Backend: farmpower_backend_v2/app/routers/notifications.py, app/models/notification.py, app/schemas/notification.py, app/services/notification_service.py)
Create Notification (Internal/Admin):
POST /notifications/: Create a new notification for a specific user (Admin only).
View Notifications:
GET /notifications/: Get notifications for the current user with pagination and optional unread_only filter.
Mark Notification as Read:
PATCH /notifications/{notification_id}/read: Mark a specific notification as read.
POST /notifications/read-all: Mark all unread notifications as read for the current user.
3.9. AI Farming Chatbot (ai-farming-chatbot/, integrated with FARMPOWER/gps-tracking.html)
Chat Interface (Frontend):
A floating AI chat button (#ai-chat-button) on gps-tracking.html.
A modal chat window (#ai-chat-modal) for interacting with the chatbot.
User input field and send button.
Displays chat messages (user and AI).
Chat API (Backend: ai-farming-chatbot/src/server.js, src/routes/api.js, src/chatbot/chatgpt.js)
POST /api/chat: Sends user queries to the ChatGPT API.
Receives and formats responses from ChatGPT.
Core Capabilities (from ai-farming-chatbot/README.md):
Provides information on farming, tractors, parts, agriculture, crops, GPS, land mapping, improving crop yield.
4. Non-Functional Requirements (NFRs)
Performance:
API response times for critical operations (login, listing retrieval) should be under 500ms.
Frontend load times should be optimized for a smooth user experience.
Security:
Robust user authentication (JWT).
Password hashing (bcrypt).
Protection against common web vulnerabilities (OWASP Top 10).
Secure storage of sensitive data (e.g., S3 for images).
Authorization checks for all API endpoints based on user roles and ownership.
Scalability:
Backend designed with FastAPI and SQLAlchemy, enabling potential scaling.
Database (PostgreSQL) chosen for scalability.
S3 for scalable media storage.
Consideration for future WebSocket integration for real-time features.
Usability:
Intuitive and responsive user interface (Tailwind CSS).
Clear navigation and accessible features.
Maintainability:
Modular code structure (routers, services, schemas, models).
Clear documentation (code comments, API docs).
Reliability:
Error handling and logging.
Database transaction management.
5. High-Level Technical Architecture
The FarmPower ecosystem consists of three main components:
FarmPower Frontend (HTML, CSS, JavaScript):
Technology: Pure HTML, Tailwind CSS, JavaScript.
Functionality: User interface for all modules (Marketplaces, GPS Tracking, Crop Calculator, Service Scheduling, Messaging, Notifications, User Profile). Makes API calls to the farmpower_backend_v2 and ai-farming-chatbot backends.
Deployment: Static files served by a web server (e.g., Nginx, or potentially directly by FastAPI in production if configured).
FarmPower Backend (Python FastAPI):
Technology: Python 3, FastAPI, SQLAlchemy (ORM), PostgreSQL (Database), Passlib (password hashing), Python-Jose (JWT).
Functionality: Provides RESTful APIs for all core business logic, including user management, marketplace operations (tractors, parts), field management, crop calculations, service bookings, messaging, and notifications. Interacts with the PostgreSQL database and S3 for storage.
Deployment: Uvicorn ASGI server.
AI Farming Chatbot (Node.js Express):
Technology: Node.js, Express.js, Axios, dotenv, ChatGPT API.
Functionality: Acts as a proxy and handler for AI-powered farming queries. Receives requests from the FarmPower frontend, interacts with the ChatGPT API, and returns responses.
Deployment: Node.js server.
Interaction Flow:
Frontend (FarmPower) sends requests to the farmpower_backend_v2 for core application data and actions (e.g., /users, /tractors, /fields).
Frontend (FarmPower) sends chat-specific requests to the ai-farming-chatbot backend (e.g., /api/chat).
The farmpower_backend_v2 interacts with PostgreSQL for data persistence and S3 for image storage.
The ai-farming-chatbot interacts with the external ChatGPT API.
Mermaid Syntax Error
View diagram source
6. Minimum Viable Product (MVP) Definition
The MVP focuses on delivering core value propositions, allowing users to perform essential tasks across key modules. It prioritizes user acquisition and initial feature validation.
MVP Core Features:
User Authentication & Profile:
User Registration (Farmer role only for MVP).
Login/Logout.
View Own Profile (/users/me).
Basic Email Verification (OTP).
Equipment Marketplace (Tractors):
Browse All Tractor Listings.
View Detailed Tractor Listings.
Ability for Farmers to List a Tractor for Sale.
Basic Listing Management (Edit/Delete own listings).
Image Upload for Tractors.
GPS Tracking & Basic Field Management:
Interactive Map displaying dummy equipment locations.
Ability to Add New Fields with Name, Area, Crop Type, and GeoJSON boundaries (drawn on map).
Display created fields on the map.
List fields in a sidebar.
Map layer controls.
Crop Calculator (Basic Calculation):
Manual input for crop parameters (costs, yield, price).
Calculate and display total cost, revenue, profit, and profit margin.
(Stretch Goal for MVP: Save/View Calculation History).
AI Farming Assistant (Chatbot):
Integrated chatbot interface on at least one key page (e.g., GPS tracking page).
Ability to send text queries.
Receive basic responses from the ChatGPT API related to farming.
Out of Scope for MVP:
Parts Marketplace.
Service Scheduling.
Comprehensive Messaging and Notification system (only basic message sending for now).
Admin dashboard functionalities beyond user ban/unban.
Advanced search filters beyond basic ones.
Real-time GPS tracking (dummy data in MVP).
Complex land usage planning features.
User reviews, ratings, or transaction flows.
Password reset functionality.
Advanced user roles (Dealer, Service Provider) beyond basic Farmer.
7. Future Enhancements
Advanced User Roles: Full implementation of Dealer and Service Provider roles with dedicated dashboards and workflows.
Parts Marketplace: Complete implementation with buying/selling workflows.
Service Scheduling: Full booking, assignment, status tracking, and provider availability management.
Real-time Features: Live GPS tracking via WebSockets, real-time chat, instant notifications.
Transaction Management: Secure payment processing, order tracking for marketplaces.
Data Analytics & Reporting: In-depth insights on crop performance, equipment utilization, market trends.
Mobile Applications: Native iOS/Android apps.
Farm Management Integrations: Connecting with external farm management software, weather APIs, IoT devices.
User Reviews & Ratings: For equipment, parts, and service providers.
User Favorites/Watchlists: For tracking specific equipment, parts, or fields.
Notifications: Push notifications, email integration for transactional alerts.
Community Features: Forums, groups, knowledge base.
Advanced AI Capabilities: Predictive analytics for crop yield, disease detection, personalized recommendations.
Localization: Support for multiple languages and regional agricultural practices.