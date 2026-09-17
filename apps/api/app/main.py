from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.routers import auth, societies, buildings, zones, nodes, telemetry, incidents, valves, maintenance, analytics, alerts, devices, system

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine, SessionLocal, Base
    import app.models  # trigger registration
    from app.models.device import Node, NodeStatus
    
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed basic topology
    db = SessionLocal()
    try:
        from app.models.infrastructure import Society, Building, Zone
        # Create Society
        soc = db.query(Society).first()
        if not soc:
            soc = Society(name="Simplicity Society")
            db.add(soc)
            db.flush()
            
            # Create Building
            bld = Building(society_id=soc.id, name="Building A")
            db.add(bld)
            db.flush()
            
            # Create Zone
            zn = Zone(building_id=bld.id, name="Basement Pipeline")
            db.add(zn)
            db.flush()
            
            # Create Nodes
            nodes = ['NODE-A1-01', 'NODE-A2-02', 'NODE-A3-04', 'NODE-B1-01']
            for nid in nodes:
                db.add(Node(
                    node_id=nid, 
                    zone_id=zn.id, 
                    status=NodeStatus.ONLINE, 
                    is_active=True
                ))
            db.commit()
    except Exception as e:
        logger.error("Failed to seed database", error=str(e))
        db.rollback()
    finally:
        db.close()
        
    logger.info("JalJasoos API starting up", version=settings.APP_VERSION)
    yield
    logger.info("JalJasoos API shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="JalJasoos Water Pipeline Monitoring Platform API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Versioned API prefix
API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Authentication"])
app.include_router(societies.router, prefix=f"{API_PREFIX}/societies", tags=["Societies"])
app.include_router(buildings.router, prefix=f"{API_PREFIX}/buildings", tags=["Buildings"])
app.include_router(zones.router, prefix=f"{API_PREFIX}/zones", tags=["Zones"])
app.include_router(nodes.router, prefix=f"{API_PREFIX}/nodes", tags=["Nodes"])
app.include_router(telemetry.router, prefix=f"{API_PREFIX}/telemetry", tags=["Telemetry"])
app.include_router(incidents.router, prefix=f"{API_PREFIX}/incidents", tags=["Incidents"])
app.include_router(valves.router, prefix=f"{API_PREFIX}/valves", tags=["Valves"])
app.include_router(maintenance.router, prefix=f"{API_PREFIX}/maintenance", tags=["Maintenance"])
app.include_router(analytics.router, prefix=f"{API_PREFIX}/analytics", tags=["Analytics"])
app.include_router(alerts.router, prefix=f"{API_PREFIX}/alerts", tags=["Alerts"])
app.include_router(devices.router, prefix=f"{API_PREFIX}/devices", tags=["Devices"])
app.include_router(system.router, prefix=f"{API_PREFIX}/system", tags=["System"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}

@app.get("/ready", tags=["Health"])
async def readiness_check():
    from app.database import engine
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"status": "not ready", "database": str(e)})
