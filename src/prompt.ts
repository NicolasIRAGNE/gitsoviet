export interface PullRequestSummary {
  title: string;
  body?: string | null;
  number: number;
  html_url?: string | null;
  user?: { login?: string | null } | null;
}

export interface ChangedFileSummary {
  filename: string;
  status?: string;
  additions?: number;
  deletions?: number;
}

interface PromptOptions {
  basePrompt: string;
  repoFullName: string;
  pr: PullRequestSummary;
  files: ChangedFileSummary[];
  maxFiles: number;
}

const truncate = (value: string, limit: number): string => {
  if (value.length <= limit) {
    return value;
  }

  return `${value.slice(0, limit)}…`;
};

const formatFiles = (files: ChangedFileSummary[], maxFiles: number): string => {
  const limited = files.slice(0, maxFiles);
  if (limited.length === 0) {
    return 'No file list available from webhook payload.';
  }

  return limited
    .map((file) => {
      const parts = [file.filename];
      if (file.status) {
        parts.push(`status: ${file.status}`);
      }
      if (typeof file.additions === 'number' || typeof file.deletions === 'number') {
        parts.push(`diff +${file.additions ?? 0}/-${file.deletions ?? 0}`);
      }
      return `- ${parts.join(' | ')}`;
    })
    .join('\n');
};

export const buildPosterPrompt = ({
  basePrompt,
  repoFullName,
  pr,
  files,
  maxFiles,
}: PromptOptions): string => {
  const summary = pr.body?.trim() || 'No description provided.';
  const shortenedSummary = truncate(summary, 500);
  const fileSection = formatFiles(files, maxFiles);

  return `${basePrompt}\n\nRepository: ${repoFullName}\nPull Request #${pr.number}: ${pr.title}\nAuthor: ${pr.user?.login ?? 'unknown contributor'}\n\nPR Summary: ${shortenedSummary}\n\nChanged files:\n${fileSection}`;
};
