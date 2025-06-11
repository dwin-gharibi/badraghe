from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from starlette.responses import RedirectResponse

from app.db import connect_db, close_db, execute_query
from app.config import settings
from app.routes import auth, users, city, tickets, reservations, discounts, features, notifications, payments, reports, roles, service_providers, support, vehicles, referrals, reviews
from app.utils.security_util import verify_password, hash_password
from app.utils.jwt_util import create_access_token
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

import sentry_sdk

sentry_sdk.init(
    dsn="https://1b98d8e0edde7e0273ed7ae280912869@sentry.hamravesh.com/8514",
    traces_sample_rate=1.0,
)


tags_metadata = [
    {
        "name": "Auth",
        "description": "Authentication and authorization related operations like login, register, and token management.",
        "externalDocs": {
            "description": "Full Auth API Docs",
            "url": "https://hamgit.ir/dngi2005/badraghe/"
        }
    },
    {
        "name": "Users",
        "description": "User profile management, account settings, and user data operations.",
        "externalDocs": {
            "description": "Full Users API Docs",
            "url": "https://hamgit.ir/dngi2005/badraghe/"
        }
    },
    {
        "name": "Cities",
        "description": "Endpoints to manage cities and geographic location data.",
        "externalDocs": {
            "description": "Full Cities API Docs",
            "url": "https://hamgit.ir/dngi2005/badraghe/"
        }
    },
    {
        "name": "Tickets",
        "description": "Manage travel tickets including flights, trains, and buses. Includes filtering, search, and booking details.",
        "externalDocs": {
            "description": "Full Tickets API Docs",
            "url": "https://hamgit.ir/dngi2005/badraghe/"
        }
    },
    {
        "name": "Reservations",
        "description": "Handle ticket reservations, cancellations, payments, and refunds.",
        "externalDocs": {
            "description": "Full Reservations API Docs",
            "url": "https://hamgit.ir/dngi2005/badraghe/"
        }
    },
    {
        "name": "Discounts",
        "description": "Manage discount codes, promotions, and related offers for users during booking.",
        "externalDocs": {
            "description": "Complete Discounts API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/discounts-docs"
        }
    },
    {
        "name": "Features",
        "description": "Additional features and enhancements offered by the platform.",
        "externalDocs": {
            "description": "Complete Features API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/features-docs"
        }
    },
    {
        "name": "Notifications",
        "description": "Manage sending and tracking notifications and alerts for users.",
        "externalDocs": {
            "description": "Complete Notifications API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/notifications-docs"
        }
    },
    {
        "name": "Payments",
        "description": "Process payments, refunds, and payment verification for ticket bookings and other transactions.",
        "externalDocs": {
            "description": "Complete Payments API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/payments-docs"
        }
    },
    {
        "name": "Reports",
        "description": "Manage issue reporting, user feedback, and ticket problem tracking.",
        "externalDocs": {
            "description": "Complete Reports API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/reports-docs"
        }
    },
    {
        "name": "Roles",
        "description": "Role-based access control, permissions management, and user role assignments.",
        "externalDocs": {
            "description": "Complete Roles API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/roles-docs"
        }
    },
    {
        "name": "Service Providers",
        "description": "Manage third-party service providers, integrations, and partner data.",
        "externalDocs": {
            "description": "Complete Service Providers API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/service-providers-docs"
        }
    },
    {
        "name": "Support Tickets",
        "description": "Customer support and issue ticketing system endpoints.",
        "externalDocs": {
            "description": "Complete Support Tickets API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/support-docs"
        }
    },
    {
        "name": "Vehicles",
        "description": "Management of vehicle data related to transport and travel bookings.",
        "externalDocs": {
            "description": "Complete Vehicles API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/vehicles-docs"
        }
    },
    {
        "name": "System",
        "description": "System-level endpoints for health checks, authentication token generation, and general utilities.",
        "externalDocs": {
            "description": "System API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/system-docs"
        }
    },
    {
        "name": "User Referrals",
        "description": "Endpoints for managing user referrals, including creation, listing, counting, and deletion.",
        "externalDocs": {
            "description": "Referral API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/referrals-docs"
        }
    },
    {
        "name": "Ticket Reviews",
        "description": "Endpoints for user reviews on travel tickets, including submission, updating, stats, and retrieval.",
        "externalDocs": {
            "description": "Reviews API documentation",
            "url": "https://hamgit.ir/dngi2005/badraghe/reviews-docs"
        }
    }
]

app = FastAPI(
    title="Badraghe API",
    description="A modern travel reservation platform API, supporting ticket booking, user management, and payment processing.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Dwin Gharibi",
        "url": "https://dwin.codes",
        "email": "me@dwin.codes",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, tags=["Users"])
app.include_router(city.router, tags=["Cities"])
app.include_router(tickets.router, tags=["Tickets"])
app.include_router(reservations.router, tags=["Reservations"])

app.include_router(discounts.router, tags=["Discounts"])
app.include_router(features.router, tags=["Features"])
app.include_router(notifications.router, tags=["Notifications"])
app.include_router(payments.router, tags=["Payments"])

app.include_router(support.router, tags=["Support Tickets"])
app.include_router(vehicles.router, tags=["Vehicles"])

app.include_router(reports.router, tags=["Reports"])
app.include_router(roles.router, tags=["Roles"])
app.include_router(service_providers.router, tags=["Service Providers"])

app.include_router(reviews.router, tags=["Ticket Reviews"])
app.include_router(referrals.router, tags=["User Referrals"])

@app.get("/", tags=["System"])
async def root():
    return RedirectResponse("/docs")

@app.get("/health", tags=["System"], summary="Health check and welcome message")
async def health_check():
    return {"status": "healthy"}

@app.post("/token", tags=["System"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    await connect_db()

    user = await execute_query(
        "SELECT id, password FROM users WHERE email = %s", 
        (form_data.username,),
        fetch_one=True
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    token = create_access_token({"user_id": user["id"]})

    return {"access_token": token, "token_type": "bearer"}