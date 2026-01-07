"""Cluster management endpoints."""

import logging

from fastapi import APIRouter, Request

from ..services.clusters import list_clusters_async
from ..services.user import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/clusters')
async def get_clusters(request: Request):
  """Get available Databricks clusters.

  Returns clusters sorted by: running first, "shared" in name second, alphabetically.
  Results are cached for 5 minutes with background refresh.
  """
  # Validate user is authenticated
  await get_current_user(request)

  # Get clusters (cached with async refresh)
  clusters = await list_clusters_async()

  return clusters
