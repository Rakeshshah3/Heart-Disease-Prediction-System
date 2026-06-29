from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import FileResponse
import pickle
import numpy as np
from pydantic import BaseModel
from services.pdf_service import generate_pdf
from Schema.schemas import InputData
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ✅ AUTH IMPORT
from auth.auth_routes import router as auth_router
from auth.auth import get_current_user

# ✅ DB IMPORT
from database.database import SessionLocal
from database.models import Prediction

# ==========================
# LOAD ENV
# ==========================
load_dotenv()

app = FastAPI(
    title="Heart Disease Prediction API",
    version="3.0.0"
)

# ✅ CONNECT AUTH ROUTES
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# LOAD MODEL
# ==========================
try:
    model = pickle.load(open("model/model.pkl", "rb"))
    print("✅ Model loaded successfully")
except Exception as e:
    print("❌ Model loading failed:", e)
    raise RuntimeError(f"Error loading model: {str(e)}")


# ==========================
# ROOT
# ==========================
@app.get("/")
def home():
    return {"message": "API is running 🚀"}


# ==========================
# 📄 PDF REQUEST MODEL
# ==========================
class PDFRequest(BaseModel):
    data: dict
    prediction: int
    weekly_plan: dict


# ==========================
# 🔄 CONVERT PLAN → TEXT
# ==========================
def convert_plan_to_suggestions(plan: dict):
    suggestions = []

    for day, details in plan.items():
        suggestions.append(f"{day}:")
        suggestions.append(f"Diet: {details.get('diet')}")
        suggestions.append(f"Exercise: {details.get('exercise')}")
        suggestions.append(f"Precautions: {details.get('precautions')}")
        suggestions.append("")

    return suggestions


# ==========================
# 🔥 SAFE PLAN GENERATOR
# ==========================
def safe_generate_plan(data, prediction, risk):

    fallback_plan = {
        "Monday": {"diet": "Eat fruits and vegetables, avoid oily food.", "exercise": "20 min brisk walking.", "precautions": "Monitor BP and reduce stress."},
        "Tuesday": {"diet": "Include lean protein and low-fat dairy.", "exercise": "Cycling 20 min.", "precautions": "Drink plenty of water."},
        "Wednesday": {"diet": "Whole grains, reduce salt intake.", "exercise": "Yoga and breathing exercises.", "precautions": "Check blood sugar."},
        "Thursday": {"diet": "Healthy fats like nuts and avocado.", "exercise": "Light cardio 30 min.", "precautions": "Avoid heavy exertion."},
        "Friday": {"diet": "High fiber foods like beans.", "exercise": "Jogging or walking.", "precautions": "Monitor BP."},
        "Saturday": {"diet": "Omega-3 foods like fish.", "exercise": "Aerobics.", "precautions": "Avoid junk food."},
        "Sunday": {"diet": "Balanced diet with fruits.", "exercise": "Rest + light stretching.", "precautions": "Relax and stay stress-free."}
    }

    try:
        from services.ai_service import generate_weekly_plan

        print("🤖 Calling AI...")
        ai_plan = generate_weekly_plan(data, prediction, risk)

        if ai_plan and isinstance(ai_plan, dict):
            print("✅ AI SUCCESS")
            return ai_plan

    except Exception as e:
        print("❌ AI ERROR:", e)

    print("⚠️ Using fallback plan")
    return fallback_plan


# ==========================
# FEATURE PREP
# ==========================
def prepare_features(data: InputData):
    return np.array([[
        data.age, data.sex, data.cp, data.trestbps,
        data.chol, data.fbs, data.restecg,
        data.thalach, data.exang, data.oldpeak, data.slope
    ]])


# ==========================
# ✅ PREDICT (SECURED + SAVED)
# ==========================
@app.post("/predict")
def predict(data: InputData, user=Depends(get_current_user)):
    try:
        input_data = prepare_features(data)

        prediction = int(model.predict(input_data)[0])

        risk = 0
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(input_data)
            risk = round(float(prob[0][1]) * 100, 2)

        weekly_plan = safe_generate_plan(data, prediction, risk)

        # ✅ SAVE TO DB
        db = SessionLocal()
        new_entry = Prediction(
            user_email=user["sub"],
            prediction=prediction,
            risk=risk
        )
        db.add(new_entry)
        db.commit()
        db.close()

        return {
            "prediction": prediction,
            "risk": risk,
            "weekly_plan": weekly_plan
        }

    except Exception as e:
        print("❌ PREDICT ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# ✅ SUGGESTION (SECURED)
# ==========================
@app.post("/suggestion")
def suggestion(data: InputData, user=Depends(get_current_user)):
    try:
        input_data = prepare_features(data)

        prediction = int(model.predict(input_data)[0])

        risk = 0
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(input_data)
            risk = round(float(prob[0][1]) * 100, 2)

        weekly_plan = safe_generate_plan(data, prediction, risk)

        return {
            "prediction": prediction,
            "risk": risk,
            "weekly_plan": weekly_plan
        }

    except Exception as e:
        print("❌ SUGGESTION ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================
# 📄 DOWNLOAD PDF (SECURED)
# ==========================
@app.post("/download-pdf")
def download_pdf(req: PDFRequest, user=Depends(get_current_user)):
    try:
        suggestions = convert_plan_to_suggestions(req.weekly_plan)

        file_path = generate_pdf(
            req.data,
            req.prediction,
            suggestions
        )

        return FileResponse(
            path=file_path,
            filename="heart_report.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        print("❌ PDF ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))