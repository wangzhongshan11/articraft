from __future__ import annotations

from fastapi import APIRouter, HTTPException

from viewer.api.dependencies import FileResolverDep, ViewerStoreDep
from viewer.api.file_manager import open_in_file_manager
from viewer.api.schemas import CaseRunEntryResponse, OpenCaseRunFolderResponse

router = APIRouter()


@router.get("/api/case-runs", response_model=list[CaseRunEntryResponse])
async def case_run_entries(store: ViewerStoreDep) -> list[CaseRunEntryResponse]:
    return store.case_runs.list_case_run_entries()


@router.post(
    "/api/case-runs/{case_run_path:path}/open-folder",
    response_model=OpenCaseRunFolderResponse,
)
async def open_case_run_folder(
    case_run_path: str,
    resolver: FileResolverDep,
) -> OpenCaseRunFolderResponse:
    artifact_dir = resolver.resolve_case_run_root(case_run_path)

    try:
        open_in_file_manager(artifact_dir)
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to open case run folder: {exc}",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OpenCaseRunFolderResponse(
        status="opened",
        case_run_path=case_run_path,
        path=str(artifact_dir),
    )
