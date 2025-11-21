import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Property, Lead, Viewing, Favorite, User, MaintenanceRequest, Agent

app = FastAPI(title="Mouqab Al Noor Real Estate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Mouqab Al Noor API is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


# --------- Public Search Endpoints ---------
class SearchFilters(BaseModel):
    q: Optional[str] = None
    location: Optional[str] = None
    city: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    featured: Optional[bool] = None


@app.post("/properties/search")
def search_properties(filters: SearchFilters):
    query = {}
    if filters.q:
        query["$or"] = [
            {"title_en": {"$regex": filters.q, "$options": "i"}},
            {"description_en": {"$regex": filters.q, "$options": "i"}},
        ]
    if filters.location:
        query["location"] = {"$regex": filters.location, "$options": "i"}
    if filters.city:
        query["city"] = {"$regex": filters.city, "$options": "i"}
    if filters.property_type:
        query["property_type"] = filters.property_type
    if filters.bedrooms is not None:
        query["bedrooms"] = {"$gte": filters.bedrooms}
    if filters.bathrooms is not None:
        query["bathrooms"] = {"$gte": filters.bathrooms}
    price_cond = {}
    if filters.min_price is not None:
        price_cond["$gte"] = filters.min_price
    if filters.max_price is not None:
        price_cond["$lte"] = filters.max_price
    if price_cond:
        query["price"] = price_cond
    if filters.featured is not None:
        query["featured"] = filters.featured

    try:
        results = get_documents("property", query, limit=100)
        for doc in results:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])  # type: ignore
        return {"items": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Property CRUD (basic) ---------
@app.post("/properties")
def create_property(payload: Property):
    try:
        inserted_id = create_document("property", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/properties/{property_id}")
def get_property(property_id: str):
    from bson import ObjectId
    try:
        doc = db["property"].find_one({"_id": ObjectId(property_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Property not found")
        doc["_id"] = str(doc["_id"])  # type: ignore
        return doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Leads, Viewings, Favorites ---------
@app.post("/leads")
def create_lead(payload: Lead):
    try:
        inserted_id = create_document("lead", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/viewings")
def create_viewing(payload: Viewing):
    try:
        inserted_id = create_document("viewing", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/favorites")
def add_favorite(payload: Favorite):
    try:
        inserted_id = create_document("favorite", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/favorites/{user_id}")
def list_favorites(user_id: str):
    try:
        favs = get_documents("favorite", {"user_id": user_id}, limit=200)
        for f in favs:
            if "_id" in f:
                f["_id"] = str(f["_id"])  # type: ignore
        return {"items": favs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------- Building Maintenance ---------
@app.post("/maintenance-requests")
def create_maintenance(payload: MaintenanceRequest):
    try:
        inserted_id = create_document("maintenancerequest", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/maintenance-requests")
def list_maintenance(status: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    try:
        items = get_documents("maintenancerequest", query, limit=200)
        for it in items:
            if "_id" in it:
                it["_id"] = str(it["_id"])  # type: ignore
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/maintenance-requests/{request_id}")
def update_maintenance_status(request_id: str, status: str):
    from bson import ObjectId
    try:
        res = db["maintenancerequest"].update_one({"_id": ObjectId(request_id)}, {"$set": {"status": status}})
        if res.matched_count == 0:
            raise HTTPException(status_code=404, detail="Maintenance request not found")
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---- Admin basics (demo login) ----
class LoginPayload(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(_: LoginPayload):
    return {"token": "demo-token"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
