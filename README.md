# Matchmaking

A lightweight matchmaking web app that helps users discover potential matches based on mutual age preferences and shared interests.

## What was built

- Profile form for entering name, age, preferred age range, and interests.
- Client-side matching engine with a simple compatibility score.
- Ranked list of potential matches with shared-interest highlights.

## Run locally

Because this is a static app, you can run it with any file server.

```bash
python3 -m http.server 4173
```

Then open: `http://localhost:4173`.

## Host it (fastest option: Netlify Drop)

1. Go to <https://app.netlify.com/drop>.
2. Drag and drop this project folder (or a zip of it).
3. Netlify will instantly publish a live URL.

## Host it from Git (Netlify or Vercel)

1. Push this repo to GitHub/GitLab/Bitbucket.
2. In Netlify or Vercel, import the repo.
3. Use these settings:
   - Build command: *(none)*
   - Publish/output directory: `.`
4. Deploy.

After deployment, add your production URL below:

- Hosted app: `https://<your-url-here>`
