# Connecting: Web vs Desktop

Both entry points — `louieai()` and `louie()` — take a `server_url` that points at the
Louie server you want to talk to. Louie Web and Louie Desktop are
different servers on different addresses, so this is the one setting you must get right
before anything else works.

| Where Louie runs | `server_url` | Graphistry server for auth |
|------------------|--------------|----------------------------|
| **Louie Cloud (web)** | `https://den.louie.ai` | `hub.graphistry.com` |
| **Enterprise Louie (web)** | `https://louie.your-company.com` | `your-company.graphistry.com` |
| **Louie Desktop (local app)** | `http://127.0.0.1:10013` | whatever the desktop app is paired with |

The default is `https://den.louie.ai`, so web users on the free tier can leave
`server_url` unset. **Desktop users must set it explicitly** — the desktop app listens on
port `10013` on the loopback interface and nothing else will reach it.

## Louie Web

```python
import os

import graphistry
import louieai

# Louie Cloud (free tier)
graphistry.register(api=3, server="hub.graphistry.com",
                    username=os.environ["GRAPHISTRY_USERNAME"],
                    password=os.environ["GRAPHISTRY_PASSWORD"])
lui = louieai(server_url="https://den.louie.ai")  # default, can be omitted

# Enterprise deployment — both servers must come from the same deployment
graphistry.register(api=3, server="your-company.graphistry.com",
                    username=os.environ["GRAPHISTRY_USERNAME"],
                    password=os.environ["GRAPHISTRY_PASSWORD"])
lui = louieai(server_url="https://louie.your-company.com")
```

## Louie Desktop

Start the Louie Desktop app, then point the client at its local port:

```python
import louieai

lui = louieai(server_url="http://127.0.0.1:10013")
lui("What's in my data?")
```

Some desktop builds expose `/auth/anonymous` for a local session with no Graphistry
login. When that is enabled, you can skip credentials entirely:

```python
from louieai import louie

lui = louie(server_url="http://127.0.0.1:10013", anonymous=True)
```

If the endpoint is disabled, the client raises a clear error — fall back to the same
Graphistry credentials your desktop app is paired with. See the
[Authentication Guide](../guides/authentication.md#method-7-anonymous-desktop-authentication-optional)
for details.

### Thread links on desktop

`lui.url` adapts to where the server lives. A local server produces a `louie://` deep
link that opens the desktop app; a web server produces a normal https link:

```python
lui("Analyze customer churn")
print(lui.url)
# Desktop: louie://n/<thread-id>
# Web:     https://den.louie.ai/?dthread=<thread-id>
```

To override the deep link — for example when you run a team server on localhost and want
browser links — pass `frontend_url`:

```python
import louieai

lui = louieai(server_url="http://127.0.0.1:10013",
              frontend_url="http://localhost:5173")
lui("Analyze customer churn")
print(lui.url)  # http://localhost:5173/?dthread=<thread-id>
```

## Environment variables

`LOUIE_URL` sets the same value without touching code, which is the easiest way to move a
notebook between desktop and web:

```bash
# Desktop
export LOUIE_URL="http://127.0.0.1:10013"

# Web (enterprise)
export LOUIE_URL="https://louie.your-company.com"
```

```python
from louieai.notebook import lui  # picks up LOUIE_URL
lui("Hello")
```

## Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| `Connection refused` on `127.0.0.1:10013` | Louie Desktop is not running, or it is running on a different port |
| Auth errors against a local URL | The desktop app is paired with a different Graphistry server than your credentials |
| `lui.url` returns `louie://…` and you wanted a browser link | You are connected to a local server; pass `frontend_url` to override |
| Queries go to the cloud when you meant desktop | `server_url`/`LOUIE_URL` is unset, so the default `https://den.louie.ai` is used |

## Next steps

- [Authentication](authentication.md) — credentials for each deployment
- [Quick Start](quick-start.md) — your first queries
