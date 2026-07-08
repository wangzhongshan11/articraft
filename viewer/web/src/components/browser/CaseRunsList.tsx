import { useEffect, useMemo, useState, type JSX } from "react";
import { FolderOpen, MoreVertical } from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import type { CaseRunEntry, ViewerSelection } from "@/lib/types";
import { useViewer, useViewerDispatch } from "@/lib/viewer-context";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip";
import { openCaseRunFolder } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function truncateWithEllipsis(value: string, maxLength = 88): string {
  const normalized = value.replace(/\s+/g, " ").trim();
  if (!normalized) return "";
  if (normalized.length <= maxLength) {
    return normalized;
  }
  return `${normalized.slice(0, maxLength).trimEnd()}...`;
}

function formatTimeAgo(dateString: string | null): string | null {
  if (!dateString) return null;
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) return null;

  const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

function statusDotClass(status: string | null): string {
  switch ((status ?? "").toLowerCase()) {
    case "failed":
      return "bg-[var(--destructive)]";
    case "success":
      return "bg-[var(--success)]";
    default:
      return "bg-[var(--text-tertiary)]";
  }
}

function isCaseRunSelected(selection: ViewerSelection | null, entry: CaseRunEntry): boolean {
  return selection?.kind === "case_run" && selection.caseRunPath === entry.case_run_path;
}

function matchesSearch(entry: CaseRunEntry, query: string): boolean {
  if (!query) {
    return true;
  }

  const haystack = [
    entry.title,
    entry.prompt_preview,
    entry.case_id,
    entry.suite,
    entry.run_token,
    entry.model_id,
    entry.provider,
    entry.status,
    entry.case_run_path,
  ]
    .filter((value): value is string => Boolean(value))
    .join(" ")
    .toLowerCase();

  return haystack.includes(query.toLowerCase());
}

function CaseRunListItem({ entry }: { entry: CaseRunEntry }): JSX.Element {
  const { selection } = useViewer();
  const dispatch = useViewerDispatch();
  const isSelected = isCaseRunSelected(selection, entry);
  const [menuOpen, setMenuOpen] = useState(false);
  const [openState, setOpenState] = useState<"idle" | "opened" | "error">("idle");
  const summaryText = truncateWithEllipsis(entry.prompt_preview || entry.title || entry.case_id);
  const metadata = [
    entry.suite,
    entry.case_id,
    entry.model_id,
    entry.turn_count !== null ? `${entry.turn_count} turns` : null,
    entry.total_cost_usd != null ? `$${entry.total_cost_usd.toFixed(4)}` : null,
    formatTimeAgo(entry.updated_at),
  ].filter((value): value is string => Boolean(value));

  return (
    <div
      className={cn(
        "group relative border-b border-[var(--border-subtle)] px-3 py-2.5 transition-colors",
        isSelected ? "bg-[var(--surface-2)]" : "hover:bg-[var(--surface-1)]",
      )}
    >
      <button
        type="button"
        onClick={() =>
          dispatch({
            type: "SELECT_ITEM",
            payload: { kind: "case_run", caseRunPath: entry.case_run_path },
          })
        }
        className="block w-full text-left"
      >
        <div className="flex items-start gap-2">
          <span className={cn("mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full", statusDotClass(entry.status))} />
          <div className="min-w-0 flex-1">
            <div className="flex items-center gap-1.5">
              <p className="truncate text-[11px] font-medium text-[var(--text-primary)]">{entry.case_id}</p>
              {entry.suite ? (
                <Badge variant="secondary" className="h-4 px-1 text-[9px] uppercase tracking-wide">
                  {entry.suite}
                </Badge>
              ) : null}
            </div>
            <p className="mt-0.5 line-clamp-2 text-[10px] leading-relaxed text-[var(--text-secondary)]">
              {summaryText}
            </p>
            <p className="mt-1 font-mono text-[9px] text-[var(--text-quaternary)]">{entry.run_token}</p>
            {metadata.length > 0 ? (
              <p className="mt-1 text-[9px] text-[var(--text-tertiary)]">{metadata.join(" · ")}</p>
            ) : null}
          </div>
        </div>
      </button>

      <div className="absolute right-2 top-2 opacity-0 transition-opacity group-hover:opacity-100">
        <DropdownMenu open={menuOpen} onOpenChange={setMenuOpen}>
          <DropdownMenuTrigger asChild>
            <button
              type="button"
              aria-label={`Open actions for ${entry.case_id}`}
              className={cn(
                "flex size-6 items-center justify-center rounded-md text-[var(--text-tertiary)] hover:bg-[var(--surface-0)] hover:text-[var(--text-primary)]",
                menuOpen ? "bg-[var(--surface-0)] text-[var(--text-primary)] opacity-100" : "",
              )}
            >
              <MoreVertical className="h-3.5 w-3.5" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuItem
              onClick={async () => {
                try {
                  await openCaseRunFolder(entry.case_run_path);
                  setOpenState("opened");
                } catch {
                  setOpenState("error");
                } finally {
                  setMenuOpen(false);
                }
              }}
            >
              <FolderOpen className="mr-2 h-3.5 w-3.5" />
              Open folder
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {openState === "opened" ? (
        <Tooltip>
          <TooltipTrigger asChild>
            <span className="sr-only">Opened case run folder</span>
          </TooltipTrigger>
          <TooltipContent side="left">Opened case run folder</TooltipContent>
        </Tooltip>
      ) : null}
      {openState === "error" ? (
        <p className="mt-1 text-[9px] text-[var(--destructive)]">Failed to open folder</p>
      ) : null}
    </div>
  );
}

type CaseRunsListProps = {
  onCountsChange?: (counts: { visible: number; total: number }) => void;
};

export function CaseRunsList({ onCountsChange }: CaseRunsListProps): JSX.Element {
  const { bootstrap, searchQuery } = useViewer();

  const entries = useMemo(() => {
    const allEntries = bootstrap?.case_run_entries ?? [];
    const query = searchQuery.trim();
    return allEntries.filter((entry) => matchesSearch(entry, query));
  }, [bootstrap?.case_run_entries, searchQuery]);

  useEffect(() => {
    onCountsChange?.({
      visible: entries.length,
      total: bootstrap?.case_run_entries.length ?? 0,
    });
  }, [bootstrap?.case_run_entries.length, entries.length, onCountsChange]);

  if (!bootstrap) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-[11px] text-[var(--text-quaternary)]">Loading case runs…</p>
      </div>
    );
  }

  if ((bootstrap.case_run_entries?.length ?? 0) === 0) {
    return (
      <div className="flex flex-1 items-center justify-center px-4 text-center">
        <p className="text-[11px] text-[var(--text-quaternary)]">
          No benchmark case runs found under test_cases/**/runs/.
        </p>
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center px-4 text-center">
        <p className="text-[11px] text-[var(--text-quaternary)]">No matching case runs</p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div>
        {entries.map((entry) => (
          <CaseRunListItem key={entry.case_run_path} entry={entry} />
        ))}
      </div>
    </ScrollArea>
  );
}
