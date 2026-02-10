# gmail-exporter

Export Gmail threads to Markdown files. Removes redundant quoted content and preserves code blocks.

## Setup

1. Get `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/): create OAuth 2.0 credentials (Desktop app) and download.
2. Create config dir and place credentials there:
   ```bash
   mkdir -p ~/.config/gmail-exporter
   mv ~/Downloads/credentials.json ~/.config/gmail-exporter/
   ```
3. Install globally (optional): `uv tool install .` from project root. Then run `gmail-exporter` from anywhere.

## Usage

```bash
# From project
uv run python -m gmail_exporter.main <THREAD_ID> [-o ./exports]

# Or after uv tool install
gmail-exporter <THREAD_ID> [-o ./exports]
```

**Finding the thread ID:** Open a Gmail thread in the browser; the URL contains the ID:
`https://mail.google.com/mail/u/0/#inbox/18c5f2a3b4d9e8f7` → thread ID is `18c5f2a3b4d9e8f7`

On first run, a browser window will open for OAuth authorization. The token is saved to `~/.config/gmail-exporter/token.json` for subsequent runs.

## Output

- One `.md` file per thread, named from the subject (special chars sanitized)
- Default output directory: `./exports/`
- Each message shows From and Date; quoted replies (`.gmail_quote`) are stripped
- Code blocks are preserved as fenced Markdown (triple backticks)
