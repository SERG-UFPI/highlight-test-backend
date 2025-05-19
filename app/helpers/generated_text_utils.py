import requests

from .. import crud
from ..config import GEMINI_API_KEY
from ..logger_config import *

def generate_cluster_insights(repo_timeseries, cluster_name, cluster_timeseries, cluster_description):
    """
    Generate insights about the evolution of a repository in relation to a cluster using the Gemini API.
    :param repo_timeseries:
    :param cluster_name:
    :param cluster_timeseries:
    :param cluster_description:
    :return:
    """
    api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+GEMINI_API_KEY

    inputs = f"Generate an insights summary (maximum 200 words) about the test evolution of the repository in relation to Cluster {cluster_name}. This cluster is characterized by '{cluster_description}'. The centroid of Cluster {cluster_name} has the following representative time series: {cluster_timeseries}. The repository has the following time series of test evolution: {repo_timeseries}. The repository was grouped into Cluster {cluster_name} based on the similarity of test evolution patterns, measured by [métrica de distância, e.g., Dynamic Time Warping]. Based on this information, provide analytical insights, highlight similarities or deviations between the repository's time series and the cluster's centroid, and explain what this grouping might suggest about the repository’s testing practices over time, such as whether they prioritize early testing, maintain consistent test coverage, or exhibit periods of test degradation."

    payload = {
        "contents": [{"parts": [{"text": inputs}]}]
    }

    output = requests.post(api_url, json=payload)

    if output is not None and output.status_code == 200:
        try:
            response_data = output.json()
            generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, TypeError) as e:
            logger.error(f"Error processing the response: {e}")
            logger.error(f"API response: {output}")
            return ("Error processing the response.")
    else:
        return ("Failed to get the API response.")

    return generated_text

def get_insights(project_id, repo_timeseries, cluster_name, cluster_timeseries, cluster_description, db):
    """
    Get insights about the evolution of a repository in relation to a cluster.
    :param project_id:
    :param repo_timeseries:
    :param cluster_name:
    :param cluster_timeseries:
    :param cluster_description:
    :param db:
    :return:
    """
    cluster_insights = crud.get_insights_by_pipeline(db, project_id)

    if cluster_insights:
        return cluster_insights.generated_text

    generated_text = generate_cluster_insights(repo_timeseries, cluster_name, cluster_timeseries, cluster_description)

    save_insights(project_id, generated_text, db)

    return generated_text

def save_insights(project_id, generated_text, db):
    """
    Save the generated insights to the database.
    :param project_id:
    :param generated_text:
    :param db:
    :return:
    """
    insight_entry = {
            "pipeline_id": project_id,
            "generated_text": generated_text
    }

    crud.create_insights(db, insight_entry)