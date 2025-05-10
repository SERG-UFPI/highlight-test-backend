import requests

from ..config import GEMINI_API_KEY
from ..logger_config import *

from app.constants import BASE_LOG_CLOC
from app.helpers.utils import save_json

def generate_cluster_insights(project_id, repo_timeseries, cluster_name, cluster_timeseries, cluster_description):
    """
    Generate insights about the test evolution of a repository in relation to a cluster using the Gemini API.
    :param project_id:
    :param repo_timeseries:
    :param cluster_name:
    :param cluster_timeseries:
    :param cluster_description:
    :return:
    """

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key="+GEMINI_API_KEY

    inputs = f"Generate an insights summary (maximum 200 words) about the test evolution of the repository in relation to Cluster {cluster_name}. This cluster is characterized by '{cluster_description}'. The centroid of Cluster {cluster_name} has the following representative time series: {cluster_timeseries}. The repository has the following time series of test evolution: {repo_timeseries}. The repository was grouped into Cluster {cluster_name} based on the similarity of test evolution patterns, measured by [métrica de distância, e.g., Dynamic Time Warping]. Based on this information, provide analytical insights, highlight similarities or deviations between the repository's time series and the cluster's centroid, and explain what this grouping might suggest about the repository’s testing practices over time, such as whether they prioritize early testing, maintain consistent test coverage, or exhibit periods of test degradation."

    payload = {
        "contents": [{"parts": [{"text": inputs}]}]
    }

    output = requests.post(API_URL, json=payload)

    if output is not None and output.status_code == 200:
        try:
            response_data = output.json()
            generated_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            save_json(BASE_LOG_CLOC, f"{project_id}_cluster_insights", {"generated_text": generated_text})
        except (KeyError, TypeError) as e:
            logger.error(f"Error processing the response: {e}")
            logger.error(f"API response: {output}")
            return ("Error processing the response.")
    else:
        return ("Failed to get the API response.")

    return generated_text