"""Pipeline tools - Manage Spark Declarative Pipelines (SDP)."""
from typing import List, Optional, Dict, Any

from databricks_mcp_core.spark_declarative_pipelines.pipelines import (
    create_pipeline as _create_pipeline,
    get_pipeline as _get_pipeline,
    update_pipeline as _update_pipeline,
    delete_pipeline as _delete_pipeline,
    start_update as _start_update,
    get_update as _get_update,
    stop_pipeline as _stop_pipeline,
    get_pipeline_events as _get_pipeline_events,
)

from ..server import mcp


@mcp.tool
def create_pipeline(
    name: str,
    root_path: str,
    catalog: str,
    schema: str,
    workspace_notebook_paths: List[str],
    serverless: bool = True,
) -> Dict[str, Any]:
    """
    Create a new Spark Declarative Pipeline.

    Args:
        name: Pipeline name
        root_path: Root workspace path (e.g., "/Workspace/Users/user@example.com/my_pipeline")
        catalog: Unity Catalog name
        schema: Schema name for output tables
        workspace_notebook_paths: List of workspace file paths for pipeline source
        serverless: Use serverless compute (default: True)

    Returns:
        Dictionary with pipeline_id of the created pipeline.
    """
    result = _create_pipeline(
        name=name,
        root_path=root_path,
        catalog=catalog,
        schema=schema,
        workspace_notebook_paths=workspace_notebook_paths,
        serverless=serverless,
    )
    return {"pipeline_id": result.pipeline_id}


@mcp.tool
def get_pipeline(pipeline_id: str) -> Dict[str, Any]:
    """
    Get pipeline details and configuration.

    Args:
        pipeline_id: Pipeline ID

    Returns:
        Dictionary with pipeline configuration and state.
    """
    result = _get_pipeline(pipeline_id=pipeline_id)
    return result.as_dict() if hasattr(result, 'as_dict') else vars(result)


@mcp.tool
def update_pipeline(
    pipeline_id: str,
    name: Optional[str] = None,
    root_path: Optional[str] = None,
    catalog: Optional[str] = None,
    schema: Optional[str] = None,
    workspace_notebook_paths: Optional[List[str]] = None,
    serverless: Optional[bool] = None,
) -> Dict[str, str]:
    """
    Update pipeline configuration.

    Args:
        pipeline_id: Pipeline ID
        name: New pipeline name
        root_path: New root workspace path
        catalog: New catalog name
        schema: New schema name
        workspace_notebook_paths: New list of workspace file paths
        serverless: New serverless setting

    Returns:
        Dictionary with status message.
    """
    _update_pipeline(
        pipeline_id=pipeline_id,
        name=name,
        root_path=root_path,
        catalog=catalog,
        schema=schema,
        workspace_notebook_paths=workspace_notebook_paths,
        serverless=serverless,
    )
    return {"status": "updated"}


@mcp.tool
def delete_pipeline(pipeline_id: str) -> Dict[str, str]:
    """
    Delete a pipeline.

    Args:
        pipeline_id: Pipeline ID

    Returns:
        Dictionary with status message.
    """
    _delete_pipeline(pipeline_id=pipeline_id)
    return {"status": "deleted"}


@mcp.tool
def start_update(
    pipeline_id: str,
    refresh_selection: Optional[List[str]] = None,
    full_refresh: bool = False,
    full_refresh_selection: Optional[List[str]] = None,
    validate_only: bool = False,
) -> Dict[str, str]:
    """
    Start a pipeline update or dry-run validation.

    Args:
        pipeline_id: Pipeline ID
        refresh_selection: List of table names to refresh
        full_refresh: If True, performs full refresh of all tables
        full_refresh_selection: List of table names for full refresh
        validate_only: If True, validates without updating data (dry run)

    Returns:
        Dictionary with update_id for polling status.
    """
    update_id = _start_update(
        pipeline_id=pipeline_id,
        refresh_selection=refresh_selection,
        full_refresh=full_refresh,
        full_refresh_selection=full_refresh_selection,
        validate_only=validate_only,
    )
    return {"update_id": update_id}


@mcp.tool
def get_update(pipeline_id: str, update_id: str) -> Dict[str, Any]:
    """
    Get pipeline update status and results.

    Args:
        pipeline_id: Pipeline ID
        update_id: Update ID from start_update

    Returns:
        Dictionary with update status (QUEUED, RUNNING, COMPLETED, FAILED, etc.)
    """
    result = _get_update(pipeline_id=pipeline_id, update_id=update_id)
    return result.as_dict() if hasattr(result, 'as_dict') else vars(result)


@mcp.tool
def stop_pipeline(pipeline_id: str) -> Dict[str, str]:
    """
    Stop a running pipeline.

    Args:
        pipeline_id: Pipeline ID

    Returns:
        Dictionary with status message.
    """
    _stop_pipeline(pipeline_id=pipeline_id)
    return {"status": "stopped"}


@mcp.tool
def get_pipeline_events(
    pipeline_id: str,
    max_results: int = 100,
) -> List[Dict[str, Any]]:
    """
    Get pipeline events, issues, and error messages.

    Use this to debug pipeline failures.

    Args:
        pipeline_id: Pipeline ID
        max_results: Maximum number of events to return (default: 100)

    Returns:
        List of event dictionaries with error details.
    """
    events = _get_pipeline_events(pipeline_id=pipeline_id, max_results=max_results)
    return [e.as_dict() if hasattr(e, 'as_dict') else vars(e) for e in events]
