from fastapi import FastAPI
from fastapi_pagination import add_pagination

from . import models
from .config import FRONTEND_URL
from .constants import *
from .helpers.import_dataset_utils import generate_metrics, save_commits, save_code_metrics, \
    save_competence_and_base_items, save_test_datas, save_project_dimensions, save_correlation, save_insights, \
    save_commit_message_item, save_maintenance_activity_summaries
from .routers.dashboards import general
from .database import engine
from .routers.auths import auth, permissions
from .routers.cruds import repository, additional_data, pipeline, user, term
from .routers.community import community_repository
from .helpers.utils import create_default_diretories
from .tasks import clone, extract_commits, generate_time_series, calculate_metrics, co_evolution_analysis
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    FRONTEND_URL,
    FRONTEND_URL+"/*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#create directories
create_default_diretories([
        BASE_RESULTS_PATH,
        BASE_PROJECTS,
        BASE_LOG_COMMITS,
        BASE_LOG_PERIOD_REVISIONS,
        BASE_LOG_REVISIONS,
        BASE_LOG_TEST_FILE,
        BASE_LOG_LOC,
        BASE_LOG_CLOC,
        BASE_LOG_PROJECT_DIMENSION,
        BASE_LOG_MAINTENANCE_ACTIVITIES,
        BASE_SUMMARY_MAINTENANCE_ACTIVITIES,
        BASE_LOG_CO_EVOLUTION
    ])

#permissions
app.include_router(permissions.router)

#community
app.include_router(community_repository.router)

#crud
app.include_router(auth.router)
app.include_router(repository.router)
app.include_router(additional_data.router)
app.include_router(pipeline.router)
app.include_router(term.router)
app.include_router(user.router)

#process
app.include_router(clone.router)
app.include_router(extract_commits.router)
app.include_router(generate_time_series.router)
app.include_router(calculate_metrics.router)
app.include_router(co_evolution_analysis.router)

#dashboard
app.include_router(general.router)

#pagination
add_pagination(app)

@app.get("/")
async def root():
    return {"message": "Ok!"}