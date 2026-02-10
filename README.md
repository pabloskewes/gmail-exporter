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

### Finding the Thread ID

**Option 1: Bookmarklet (recommended)**

Create a browser bookmark with this as the URL:

```javascript
javascript:(function(){var id=document.querySelector('[role="main"] [data-legacy-thread-id]')?.getAttribute('data-legacy-thread-id');if(id){navigator.clipboard.writeText('gmail-exporter '+id);alert('Comando copiado:\ngmail-exporter '+id+'\n\nPégalo en la terminal')}else{alert('No se encontró thread ID. Asegúrate de estar en un hilo de Gmail.')}})();
```

Then:
1. Open a Gmail thread
2. Click the bookmark
3. Paste the command in your terminal

**Option 2: Manual**

Open a Gmail thread from your inbox (not search results). Sometimes the URL shows the ID:
`https://mail.google.com/mail/u/0/#inbox/19367d3d02f9a599` → thread ID is `19367d3d02f9a599`

If the URL doesn't show it, use the bookmarklet or run this in the browser console:
```javascript
document.querySelector('[role="main"] [data-legacy-thread-id]').getAttribute('data-legacy-thread-id')
```

### First Run

On first run, a browser window will open for OAuth authorization. The token is saved to `~/.config/gmail-exporter/token.json` for subsequent runs.

## Debug

`gmail-exporter --debug THREAD_ID` pretty-prints the raw message structure (for development). See `notes/journals/001-init-repo/02-message-structure.md` for documented schema.

## Output

- One `.md` file per thread, named from the subject (special chars sanitized)
- Default output directory: `./exports/`
- Each message shows From and Date; quoted replies (`.gmail_quote`) are stripped
- Code blocks are preserved as fenced Markdown (triple backticks)
