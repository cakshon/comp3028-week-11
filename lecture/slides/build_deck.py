from pathlib import Path
out=Path(__file__).resolve().parent/'COMP3028_Lecture11_Docker_LocalLoop.tex'
frames=[]
def add(title, body, fragile=False, subtitle=None):
    opt='[fragile]' if fragile else ''
    sub='' if subtitle is None else r'\framesubtitle{'+subtitle+'}\n'
    frames.append(r'\begin{frame}'+opt+'\n'+r'\frametitle{'+title+'}'+'\n'+sub+body.strip()+'\n'+r'\end{frame}'+'\n')
def code(s):
    return '\\begin{lstlisting}\n'+s.strip()+'\n\\end{lstlisting}\n'
P=r'''\documentclass[aspectratio=169,10pt]{beamer}
\usetheme{Boadilla}
\usefonttheme{professionalfonts}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{booktabs}
\usepackage{array}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{hyperref}
\definecolor{navy}{HTML}{153047}
\definecolor{docker}{HTML}{087DB7}
\definecolor{teal}{HTML}{008E91}
\definecolor{pale}{HTML}{EDF6FA}
\definecolor{codebg}{HTML}{F3F7FA}
\definecolor{coderule}{HTML}{CADDE6}
\definecolor{warm}{HTML}{E38B38}
\setbeamercolor{structure}{fg=docker}
\setbeamercolor{normal text}{fg=navy,bg=white}
\setbeamercolor{frametitle}{fg=white,bg=navy}
\setbeamercolor{block title}{fg=white,bg=docker}
\setbeamercolor{block body}{fg=navy,bg=pale}
\setbeamercolor{alerted text}{fg=warm}
\setbeamertemplate{navigation symbols}{}
\setbeamertemplate{items}[circle]
\setbeamertemplate{footline}{\hfill\scriptsize COMP3028 | Lecture 11 | Docker + Node.js\quad\insertframenumber/\inserttotalframenumber\hspace{0.35cm}\vspace{0.12cm}}
\setbeamersize{text margin left=0.72cm,text margin right=0.72cm}
\setlength{\parskip}{3pt}
\lstset{basicstyle=\ttfamily\scriptsize,backgroundcolor=\color{codebg},frame=single,rulecolor=\color{coderule},breaklines=true,showstringspaces=false,keepspaces=true,columns=fullflexible,aboveskip=0.4em,belowskip=0.4em,xleftmargin=0.2em,xrightmargin=0.2em}
\newcommand{\goal}[1]{\begin{block}{Checkpoint}#1\end{block}}
\newcommand{\smallsource}[1]{{\tiny\color{gray}#1}}
\title[Docker + Node.js]{Developing and Distributing Applications with Docker}
\subtitle{Lecture 11 | COMP3028 Software Construction}
\author{Hands-on lab: LocalLoop Community Food Rescue Platform}
\date{Spring 2026 teaching materials}
\begin{document}
'''
frames.append(r'''\begin{frame}[plain]
\vspace*{0.65cm}
{\color{docker}\rule{3cm}{0.09cm}}\\[0.25cm]
{\Huge\bfseries Developing and Distributing\\ Applications with Docker}\\[0.25cm]
{\Large COMP3028 -- Software Construction | Lecture 11}\\[0.40cm]
{\large Node.js hands-on: LocalLoop Food Rescue API}\\[0.25cm]
\begin{block}{Build \(\rightarrow\) Run \(\rightarrow\) Test \(\rightarrow\) Share}
No previous Docker experience required. Uses plain Node.js and built-in testing tools.
\end{block}
\vfill
{\small Spring 2026 | 16:9 | Beginner-friendly workshop}
\end{frame}
''')
add('Today: the big picture',r'''
\begin{columns}[T]
\column{0.54\textwidth}
\textbf{Lecture ideas (approx. 35 min)}
\begin{enumerate}\item The deployment problem\item Images vs. containers\item Dockerfiles, networking, volumes\item Registries and distribution\end{enumerate}
\column{0.44\textwidth}
\textbf{Guided lab (approx. 75 min)}
\begin{enumerate}\item Run and test Node.js\item Build and run an image\item Debug and use Compose\item Tag and share an image\end{enumerate}
\end{columns}
\vspace{0.25cm}
\goal{By the end: run the same LocalLoop application locally and in Docker, explain each step, and prepare a shareable version.}
''')
add('Learning outcomes',r'''
By the end of Lecture 11 you should be able to:
\begin{enumerate}
\item Explain \textbf{image}, \textbf{container}, \textbf{Dockerfile}, \textbf{registry} and \textbf{Compose}.
\item Package a Node.js HTTP API into a reproducible Docker image.
\item Run, inspect, test, stop and troubleshoot containers.
\item Configure published ports and environment variables safely.
\item Tag, push and pull a versioned image (or export/import offline).
\item Identify production limitations of the classroom prototype.
\end{enumerate}
\vspace{0.2cm}\smallsource{Links to COMP3028 practices: web services, testing, secure deployment and code reviews.}
''')
add('The real-world problem',r'''
\begin{columns}[T]
\column{0.50\textwidth}
\begin{block}{Developer laptop}
\begin{itemize}\item ``It works on my machine.''\item Different Node.js versions\item Missing libraries and configuration\item Accidental dependence on local files\end{itemize}
\end{block}
\column{0.50\textwidth}
\begin{block}{Tutor / deployment host}
\begin{itemize}\item Different operating system\item Different installed packages\item Port is already occupied\item Application will not start\end{itemize}
\end{block}
\end{columns}
\vspace{0.2cm}
\textbf{Question:} How can we package the runtime and application so someone else can start it consistently?
''')
add('Case study: LocalLoop',r'''
\begin{block}{Official Spring 2026 scenario}
A council commissions an online food-rescue platform to connect surplus-food businesses with community organisations, volunteers and residents.
\end{block}
\begin{itemize}
\item Publish surplus-food listings with pickup information.
\item Discover and reserve available food.
\item Manage user permissions, safety information and notifications.
\item Track food-rescue impact.
\end{itemize}
\textbf{Today's slice:} a tiny teaching API for \emph{listing, reservation and health checks}---not the full seven-function system.
\smallsource{Source: COMP3028-SPR26-Case-Study.pdf (provided with the unit).}
''')
add('From source code to running service',r'''
\centering
\begin{tikzpicture}[node distance=0.38cm, every node/.style={align=center},box/.style={draw=docker,rounded corners=3pt,fill=pale,minimum width=2.30cm,minimum height=1.28cm,font=\small},arr/.style={-{Latex[length=2mm]},thick,draw=navy}]
\node[box] (src) {\textbf{Source}\\\texttt{app.js}\\\texttt{package.json}};
\node[box,right=of src] (df) {\textbf{Dockerfile}\\Build instructions};
\node[box,right=of df] (im) {\textbf{Image}\\App + Node runtime};
\node[box,right=of im] (reg) {\textbf{Registry}\\Docker Hub};
\draw[arr] (src)--(df);\draw[arr] (df)--node[above,font=\tiny]{build}(im);\draw[arr] (im)--node[above,font=\tiny]{push}(reg);
\node[box,below=0.9cm of im] (ct) {\textbf{Container}\\Running process};
\draw[arr] (im)--node[right,font=\tiny]{run}(ct);
\node[box,below=0.9cm of reg] (team) {\textbf{Teammate}\\Pull and run};
\draw[arr] (reg)--(team);\draw[arr] (team)--(ct);
\end{tikzpicture}
\par\vspace{0.3cm}
\textbf{Key idea:} Docker builds a portable \emph{image}; running an image starts a \emph{container}.
''')
add('Image, container and Dockerfile',r'''
\begin{tabular}{p{0.18\textwidth}p{0.35\textwidth}p{0.34\textwidth}}\toprule
\textbf{Term}&\textbf{Meaning}&\textbf{Everyday analogy}\\\midrule
Dockerfile&Recipe to assemble software layers&Cooking instructions\\
Image&Immutable packaged application + runtime&Prepared meal / template\\
Container&Running instance of an image&Meal being served / running copy\\
Registry&Service that stores and distributes images&Shared catalogue\\
Compose&Defines how services run together&Operating plan\\\bottomrule
\end{tabular}
\vspace{0.35cm}
\goal{You can create several separate containers from one image. Their in-memory data is not automatically shared.}
''')
add('Containers vs. virtual machines',r'''
\begin{columns}[T]
\column{0.5\textwidth}
\begin{block}{Virtual machine}
\begin{itemize}\item Guest operating system\item Separate kernel abstraction\item Often heavier startup/storage\end{itemize}
\end{block}
\column{0.5\textwidth}
\begin{block}{Container}
\begin{itemize}\item Isolated application processes\item Shares host kernel through the container platform\item Often lighter and faster to launch\end{itemize}
\end{block}
\end{columns}
\smallskip
Docker Desktop typically runs Linux containers inside a lightweight Linux VM on Windows/macOS. \textbf{Containers are not a complete security boundary or a replacement for application security.}
''')
add('What Docker does / does not do',r'''
\begin{columns}[T]
\column{0.5\textwidth}
\begin{block}{Docker helps with}
\begin{itemize}\item Packaging runtime and dependencies\item Environment consistency\item Repeatable startup\item Image versioning and sharing\end{itemize}
\end{block}
\column{0.5\textwidth}
\begin{block}{Docker does not automatically}
\begin{itemize}\item Fix faulty application code\item Make an unsafe API secure\item Persist data without storage design\item Guarantee performance or availability\end{itemize}
\end{block}
\end{columns}
\goal{Containerisation improves delivery; engineering quality still depends on code, tests and operations.}
''')
add('Lab setup: what you need',r'''
\begin{itemize}
\item \textbf{Docker Desktop} (Windows/macOS) or Docker Engine + Compose plugin (Linux); start the engine.
\item \textbf{Node.js 22 or later} for running tests locally (lab image uses Node 24 LTS).
\item A terminal: PowerShell, macOS Terminal or a Linux shell.
\item The supplied \texttt{localloop-api} lab folder (no npm packages to download).
\item Internet for the \emph{first} image pull and optional Docker Hub sharing.
\end{itemize}
\vspace{0.2cm}
\smallsource{Node.js 24 remains supported as Maintenance LTS as of Nov. 2026; Node.js 26 is Active LTS. Source: nodejs.org release schedule.}
''')
add('Lab 0: verify your tools',code('docker --version\ndocker info\ndocker compose version\nnode --version\nnpm --version')+r'''
\textbf{Expected:} Docker version displayed; \texttt{docker info} prints server details; \texttt{docker compose version} works.
\begin{alertblock}{Common beginner issue}
If \texttt{docker info} says ``Cannot connect to the Docker daemon'', start Docker Desktop / Engine and retry.
\end{alertblock}
\goal{Before continuing: you can run \texttt{docker info} without an error.}
''',True)
add('Lab project files',r'''
\begin{columns}[T]
\column{0.53\textwidth}
\begin{block}{Folder layout}
\texttt{localloop-api/}\\
\hspace{0.25cm}\texttt{src/app.js}\\
\hspace{0.25cm}\texttt{src/server.js}\\
\hspace{0.25cm}\texttt{test/app.test.js}\\
\hspace{0.25cm}\texttt{package.json}\\
\hspace{0.25cm}\texttt{package-lock.json}\\
\hspace{0.25cm}\texttt{Dockerfile}\\
\hspace{0.25cm}\texttt{.dockerignore}\\
\hspace{0.25cm}\texttt{compose.yaml}
\end{block}
\column{0.45\textwidth}
\textbf{Why so few files?}
\begin{itemize}
\item Uses Node's built-in HTTP API\item No extra npm dependencies\item Built-in \texttt{node:test} tests\item Focus is Docker lifecycle\end{itemize}
\end{columns}
''')
add('Lab 1.1: run the Node.js project',code('cd localloop-api\nnpm ci\nnpm test\nnpm start')+r'''
\begin{itemize}
\item \texttt{npm ci}: installs precisely from the included lockfile (no extra packages needed here).
\item \texttt{npm test}: runs three automated API tests.
\item \texttt{npm start}: starts the API on port 3000.
\end{itemize}
\goal{Terminal prints ``LocalLoop API listening on port 3000''. Keep this terminal open.}
''',True)
add('Lab 1.2: use the browser',r'''
Open these addresses:
\begin{enumerate}
\item \url{http://localhost:3000/} --- application name/version.
\item \url{http://localhost:3000/health} --- \texttt{\{"status":"ok"\}}.
\item \url{http://localhost:3000/api/listings} --- existing food listing.
\item \url{http://localhost:3000/api/stats} --- listing counts.
\end{enumerate}
\vspace{0.15cm}
\begin{block}{Remember}
A browser address bar is useful for \textbf{GET}. To send \textbf{POST}, use a terminal or API client.
\end{block}
\goal{Your local API responds before you start Docker.}
''')
add('LocalLoop API: the request map',r'''
\small
\begin{tabular}{p{0.11\textwidth}p{0.43\textwidth}p{0.32\textwidth}}\toprule
\textbf{Method}&\textbf{Path}&\textbf{Purpose}\\\midrule
GET&\texttt{/health}&Read health status\\
GET&\texttt{/api/listings}&View available data\\
GET&\texttt{/api/stats}&View summary counts\\
POST&\texttt{/api/listings}&Create a listing\\
POST&\texttt{/api/listings/:id/reserve}&Reserve a listing\\\bottomrule
\end{tabular}
\vspace{0.25cm}
\textbf{HTTP responses:} 200 (OK), 201 (created), 400 (bad data), 404 (missing), 409 (conflict).
\smallsource{Learning simplification: accounts, permissions, database persistence and safety approval are deliberately not implemented.}
''')
add('Lab 1.3: create a food listing',code('curl -X POST http://localhost:3000/api/listings \\\n  -H "Content-Type: application/json" \\\n  -d \'{"title":"Fruit box","quantity":4,\n       "pickupLocation":"Campus library"}\'')+r'''
\textbf{macOS/Linux / Bash example above.} For Windows PowerShell, see the next slide.
\goal{Expected: HTTP 201 and a new JSON object with \texttt{status:"available"}.}
''',True)
add('Windows PowerShell: POST request',code('$body = @{ title = "Fruit box"; quantity = 4;\n  pickupLocation = "Campus library" } | ConvertTo-Json\nInvoke-RestMethod -Uri http://localhost:3000/api/listings `\n  -Method Post -ContentType "application/json" -Body $body')+r'''
\begin{block}{Two shell syntaxes}
Use \texttt{curl} in Bash, or \texttt{Invoke-RestMethod} in PowerShell. Do not mix the line-continuation characters (\texttt{\textbackslash} vs. backtick).
\end{block}
''',True)
add('Lab 1.4: reserve and validate',code('# Reserve the listing with ID 1\ncurl -X POST http://localhost:3000/api/listings/1/reserve\n\n# Run it again: the same reservation must be rejected\ncurl -X POST http://localhost:3000/api/listings/1/reserve\n\n# Recheck counts\ncurl http://localhost:3000/api/stats')+r'''
\textbf{Expected:} First reservation \texttt{200}; second returns a JSON conflict (HTTP \texttt{409}).
\goal{Explain why returning 409 is better than silently reserving the same food twice.}
''',True)
add('What makes the demo event-driven?',code("const events = new EventEmitter();\nevents.on('listing.created', item => {\n  console.log('Created', item.id);\n});\n\n// When an item is created:\nevents.emit('listing.created', item);")+r'''
\begin{itemize}
\item A \textbf{producer} emits a domain event.
\item A \textbf{listener} responds without changing the HTTP route's purpose.
\item Here, events only write logs; they are \emph{not} durable messages.
\end{itemize}
\smallsource{For the full LocalLoop platform, notifications or audit processing could become separate services.}
''',True)
add('Knowledge check: before containerising',r'''
\begin{enumerate}
\item What must be running for \texttt{localhost:3000} to respond?
\item Is \texttt{GET /api/listings} a read or a write operation?
\item Why is the data lost when we restart the teaching API?
\item What does \texttt{npm test} verify in this project?
\end{enumerate}
\vspace{0.4cm}
\goal{Stop the locally running server using \texttt{Ctrl+C} to free port 3000 before the Docker lab.}
''')
add('Dockerfile: our packaging recipe',code('FROM node:24-alpine\nWORKDIR /app\nENV NODE_ENV=production\nCOPY package*.json ./\nRUN npm ci --omit=dev\nCOPY --chown=node:node src ./src\nUSER node\nEXPOSE 3000\nCMD ["node", "src/server.js"]')+r'''
\textbf{Build-time:} \texttt{FROM}, \texttt{COPY}, \texttt{RUN}. \quad \textbf{Run-time:} \texttt{USER}, \texttt{CMD}; \texttt{EXPOSE} documents an intended port.
''',True)
add('Read a Dockerfile like a recipe',r'''
\small
\begin{tabular}{p{0.24\textwidth}p{0.69\textwidth}}\toprule
\textbf{Instruction}&\textbf{Meaning}\\\midrule
\texttt{FROM}&Start from a Node.js base image\\
\texttt{WORKDIR}&Set working directory inside image\\
\texttt{COPY}&Copy project files into image\\
\texttt{RUN}&Execute command \emph{while building} (install packages)\\
\texttt{ENV}&Set a runtime environment variable\\
\texttt{USER}&Run the application as non-root \texttt{node} user\\
\texttt{EXPOSE}&Document application port; \emph{does not} publish it\\
\texttt{CMD}&Default command when container starts\\\bottomrule
\end{tabular}
\vspace{0.12cm}
\smallsource{Official reference: https://docs.docker.com/reference/dockerfile/}
''')
add('Why we need .dockerignore',code('**/node_modules\n.git\n.env\n.env.*\n**/.npmrc\ncoverage\n*.log\ntest')+r'''
\begin{itemize}
\item Makes build context smaller, cleaner and faster.
\item Helps avoid copying local dependencies, secrets, history and tests into runtime images.
\item This does \textbf{not} replace proper secret management or code review.
\end{itemize}
''',True)
add('Lab 2.1: build your image',code('docker build -t localloop-api:1.0 .\ndocker images')+r'''
\textbf{Read the command:}
\begin{itemize}
\item \texttt{docker build}: build from the current directory's Dockerfile.
\item \texttt{-t localloop-api:1.0}: assign a name and version tag.
\item \texttt{.}: build context = current folder.
\end{itemize}
\goal{The image named \texttt{localloop-api:1.0} appears in \texttt{docker images}.}
''',True)
add('Build layers and caching',r'''
\begin{enumerate}
\item Base image layer (\texttt{node:24-alpine}).
\item Project manifests copied (\texttt{package.json}, lockfile).
\item Dependencies prepared (\texttt{npm ci}).
\item Application source copied.
\end{enumerate}
\begin{block}{Small change, faster rebuild}
If only \texttt{src/app.js} changes, Docker can often reuse earlier dependency layers. The order of \texttt{COPY} steps matters.
\end{block}
\goal{Change a response string, rebuild as \texttt{1.1} and observe which steps are cached.}
''')
add('Lab 2.2: run a container',code('docker run -d --name localloop \\\n  -p 3000:3000 localloop-api:1.0\n\ndocker ps\ndocker logs localloop')+r'''
\begin{itemize}
\item \texttt{-d}: detached/background mode.
\item \texttt{--name}: convenient container identifier.
\item \texttt{-p HOST:CONTAINER}: publish port to host.
\end{itemize}
\goal{Browse \url{http://localhost:3000/health}: you should get the same JSON as before.}
''',True)
add('Port mapping visualised',r'''
\centering
\begin{tikzpicture}[node distance=0.8cm,box/.style={draw=docker,rounded corners,fill=pale,minimum width=3.3cm,minimum height=1.55cm,align=center},arr/.style={-{Latex},very thick,draw=teal}]
\node[box] (host) at (-4.2,0) {\textbf{Your computer / browser}\\\texttt{localhost:3000}};
\node[box] (ct) at (4.2,0) {\textbf{Container}\\Node listens on \texttt{0.0.0.0:3000}};
\draw[arr] (host.east) -- node[above,fill=white,inner sep=3pt]{\texttt{-p 3000:3000}} node[below,fill=white,inner sep=2pt]{\scriptsize HOST : CONTAINER} (ct.west);
\end{tikzpicture}
\vspace{0.45cm}
\begin{alertblock}{Important difference}
\texttt{EXPOSE 3000} in a Dockerfile is \emph{documentation}; \texttt{-p 3000:3000} publishes the port.
\end{alertblock}
''')
add('Lab 2.3: inspect the running container',code('docker ps\ndocker logs localloop\ndocker exec localloop node --version\ndocker inspect localloop')+r'''
\begin{itemize}
\item \texttt{ps}: which containers are running?
\item \texttt{logs}: what did the application print?
\item \texttt{exec}: run a process in a running container.
\item \texttt{inspect}: detailed JSON configuration and metadata.
\end{itemize}
\goal{Find the image tag and port mapping for your container.}
''',True)
add('Lab 2.4: stop and remove',code('docker stop localloop\ndocker ps -a\ndocker rm localloop')+r'''
\begin{block}{What remains?}
The \textbf{image} remains in \texttt{docker images}; the named \textbf{container} has been removed.
\end{block}
\textbf{Try again:} run a new container from \texttt{localloop-api:1.0}. It begins with the original in-memory listing, not your earlier changes.
''',True)
add('Container state is usually ephemeral',r'''
\begin{columns}[T]
\column{0.5\textwidth}
\begin{block}{In our teaching API}
\begin{itemize}\item Listings stored in a JavaScript array\item New process starts with fresh array\item Another container has a different copy\end{itemize}
\end{block}
\column{0.5\textwidth}
\begin{block}{In a real LocalLoop system}
\begin{itemize}\item Store records in a database\item Use volumes for stateful services\item Define backups and recovery\end{itemize}
\end{block}
\end{columns}
\textbf{Rule:} never rely on a container's writable layer for durable business data.
''')
add('Troubleshooting: 5 common problems',r'''
\scriptsize
\begin{tabular}{p{0.40\textwidth}p{0.52\textwidth}}\toprule
\textbf{Symptom}&\textbf{First check / remedy}\\\midrule
Cannot connect to Docker daemon&Start Docker Desktop or Engine; \texttt{docker info}\\
Port 3000 already allocated&Stop local Node server/container or use \texttt{-p 3001:3000}\\
Cannot find Dockerfile&Use project root: \texttt{cd localloop-api}\\
Cannot reach application&Run \texttt{docker ps}, \texttt{docker logs}; check \texttt{-p}\\
Image build fails at npm ci&Verify matching \texttt{package.json} and \texttt{package-lock.json}\\\bottomrule
\end{tabular}
\vspace{0.25cm}
\goal{Debug in layers: engine \(\rightarrow\) image \(\rightarrow\) container \(\rightarrow\) port \(\rightarrow\) application.}
''')
add('Lab 3: why Compose?',r'''
Instead of memorising a long \texttt{docker run} command, describe the service once in \texttt{compose.yaml}.
\begin{block}{Compose is useful when}
\begin{itemize}
\item A project has several services (API + database + worker).
\item A team needs repeatable local setup.
\item Configuration, ports, environment and dependencies should be versioned.
\end{itemize}
\end{block}
\textbf{Today:} one API service, as a stepping stone to multi-container systems.
''')
add('Compose configuration',code('services:\n  api:\n    build: .\n    image: localloop-api:1.0\n    ports:\n      - "3000:3000"\n    environment:\n      PORT: "3000"\n      NODE_ENV: production\n    restart: unless-stopped')+r'''
\textbf{Interpretation:} build the API image, publish port 3000, and set configuration.
\smallsource{Use modern \texttt{docker compose} (with a space), not legacy \texttt{docker-compose}.}
''',True)
add('Lab 3.1: run with Compose',code('docker compose config\ndocker compose up --build -d\ndocker compose ps\ndocker compose logs api\n\n# When finished:\ndocker compose down')+r'''
\begin{itemize}
\item \texttt{config}: validate and show the resolved configuration.
\item \texttt{up --build -d}: build and start the service.
\item \texttt{down}: remove Compose-created containers/network.
\end{itemize}
\goal{Start with Compose and verify \url{http://localhost:3000/health}.}
''',True)
add('Environment configuration',r'''
\begin{columns}[T]
\column{0.50\textwidth}
\begin{block}{Good practice}
\begin{itemize}\item Use \texttt{PORT} and \texttt{NODE\_ENV} as configuration\item Keep dev and production settings separate\item Prefer explicit ports and names\end{itemize}
\end{block}
\column{0.50\textwidth}
\begin{alertblock}{Avoid}
\begin{itemize}\item Passwords in Dockerfiles\item API keys in images / Git\item Logging sensitive information\end{itemize}
\end{alertblock}
\end{columns}
For real deployment, use a secrets manager or Docker/Compose secrets where appropriate; \texttt{ENV} is \emph{not} a secret vault.
''')
add('Test and review before distribution',r'''
\begin{enumerate}
\item \textbf{Source quality:} code review and static inspection.
\item \textbf{Functional tests:} run \texttt{npm test} and verify API behaviour.
\item \textbf{Container smoke test:} start image and test \texttt{/health}.
\item \textbf{Runtime inspection:} check logs, user, port and configuration.
\item \textbf{Security review:} exclude secrets, validate inputs, use least privilege.
\end{enumerate}
\begin{block}{COMP3028 connection}
For code reviews, discuss a Dockerfile or Compose PR as seriously as application code: correctness, security, maintainability and test evidence.
\end{block}
''')
add('Security basics for a Node image',r'''
\begin{itemize}
\item Use a \textbf{supported LTS} Node base image; update and rebuild regularly.
\item Prefer non-root \texttt{USER node}; restrict exposed network interfaces.
\item Exclude credentials, \texttt{.env} and private files from images.
\item Use a lockfile and \texttt{npm ci}; review dependencies when added.
\item Apply API authentication, authorisation, input validation and safe error handling.
\item Consider image scanning and fixed immutable digests in real deployments.
\end{itemize}
\smallsource{Docker best practices: https://docs.docker.com/build/building/best-practices/}
''')
add('Images need names and versions',r'''
\centering
{\LARGE\ttfamily yourname/localloop-api:1.0}\\[0.4cm]
\begin{tabular}{lll}\toprule
\textbf{Part}&\textbf{Example}&\textbf{Role}\\\midrule
Namespace&\texttt{yourname}&Docker Hub account / organisation\\
Repository&\texttt{localloop-api}&Application image name\\
Tag&\texttt{1.0}&Version label\\\bottomrule
\end{tabular}
\vspace{0.3cm}
\begin{alertblock}{Versioning habit}
Prefer explicit tags such as \texttt{1.0} or a commit-derived tag over relying on \texttt{latest}.
\end{alertblock}
''')
add('Lab 4.1: publish to Docker Hub (optional)',code('# Replace YOUR_ID with your own Docker Hub username\ndocker login\ndocker tag localloop-api:1.0 YOUR_ID/localloop-api:1.0\ndocker push YOUR_ID/localloop-api:1.0')+r'''
\begin{itemize}
\item You need a Docker Hub account and permission to push the repository.
\item Keep images free of credentials and private project data.
\item If campus network blocks Hub, use the offline method next.
\end{itemize}
\goal{Your account's repository page shows a \texttt{1.0} image tag (if you opt in).}
''',True)
add('Lab 4.2: pull and run the shared image',code('docker pull YOUR_ID/localloop-api:1.0\ndocker run --rm -p 3001:3000 \\\n  YOUR_ID/localloop-api:1.0')+r'''
\textbf{Now open:} \url{http://localhost:3001/health}
\begin{block}{Why 3001?}
The host port can differ from the port inside the container. This also avoids conflict if port 3000 is already used.
\end{block}
\smallsource{In class, you can pull a teammate's image if it is publicly accessible or you have appropriate access.}
''',True)
add('Alternative: distribute an image offline',code('# On sending computer\ndocker save -o localloop-api-1.0.tar localloop-api:1.0\n\n# Transfer the .tar through an approved channel\n# On receiving computer\ndocker load -i localloop-api-1.0.tar\ndocker run --rm -p 3001:3000 localloop-api:1.0')+r'''
\textbf{Trade-off:} useful without a registry, but large files and manual version tracking.
\smallsource{Be careful with large tar files and never package secrets.}
''',True)
add('Live exercise: Docker trouble ticket',r'''
\begin{block}{Scenario}
A student runs \texttt{docker run -p 3000:3000 localloop-api:1.0}, but gets ``port is already allocated''.
\end{block}
\textbf{Task (3 min):}
\begin{enumerate}
\item Identify at least two plausible processes holding the host port.
\item Find a safe way to run the container without stopping other services.
\item State the new browser URL.
\end{enumerate}
\vspace{0.2cm}
\goal{Answer: publish \texttt{-p 3001:3000}; browse \texttt{localhost:3001}. Also inspect running containers and local Node processes.}
''')
add('Extension tasks: choose one',r'''
\begin{enumerate}
\item \textbf{Basic:} Add \texttt{GET /api/listings/available} and a matching test. Rebuild as \texttt{1.1}.
\item \textbf{Intermediate:} Add a validated category field; include it in creation and response.
\item \textbf{Intermediate:} Add a health-check instruction or Compose service healthcheck.
\item \textbf{Advanced:} Introduce a database service and persistent storage; justify data lifecycle.
\end{enumerate}
\vspace{0.25cm}
\textbf{Evidence:} source change, passing test, image tag, and output from the running container.
''')
add('Week 11 vs. assessment requirements',r'''
\begin{block}{What this lab is}
A supported practice activity connecting application development, testing, containerisation, service configuration and distribution.
\end{block}
\begin{alertblock}{What it is not}
A new official Assessment 2 marking rule. Continue to follow the official code-review brief, vUWS submission instructions and Learning Guide rubric.
\end{alertblock}
\textbf{Useful PR discussion:} explain why Dockerfile changes are safe, what commands prove they work, and what issues remain.
''')
add('Student demonstration checklist',r'''
\begin{enumerate}
\item \texttt{npm test} passes.
\item \texttt{docker build -t localloop-api:1.0 .} succeeds.
\item \texttt{docker run -p 3000:3000 ...} starts an accessible service.
\item \texttt{/health}, \texttt{/api/listings} and reserve flow respond correctly.
\item \texttt{docker ps} and \texttt{docker logs} show evidence.
\item \texttt{docker compose up --build -d} works.
\item Can explain \texttt{Dockerfile}, \texttt{.dockerignore}, image tag and port map.
\end{enumerate}
\goal{Show understanding rather than only screenshots or copied commands.}
''')
add('Quick knowledge check',r'''
\begin{enumerate}
\item What is the difference between an \textbf{image} and a \textbf{container}?
\item Why copy \texttt{package*.json} before \texttt{src/}?
\item Why does \texttt{EXPOSE 3000} not make the API publicly reachable?
\item How is \texttt{docker compose up} different from \texttt{docker build}?
\item How would you deliver the \texttt{1.0} image to another computer?
\end{enumerate}
\vspace{0.3cm}
\textbf{Exit ticket:} Write one Docker command and explain it in your own words.
''')
add('Recap: 5 commands to remember',code('npm test\ndocker build -t localloop-api:1.0 .\ndocker run --rm -p 3000:3000 localloop-api:1.0\ndocker compose up --build -d\ndocker tag localloop-api:1.0 YOUR_ID/localloop-api:1.0')+r'''
\centering\large Source \(\rightarrow\) Test \(\rightarrow\) Image \(\rightarrow\) Container \(\rightarrow\) Distribution
''',True)
add('Official reading and documentation',r'''
\small
\begin{itemize}
\item \textbf{Docker Docs.} Node.js guide: \url{https://docs.docker.com/guides/nodejs/}
\item \textbf{Docker Docs.} Dockerfile reference: \url{https://docs.docker.com/reference/dockerfile/}
\item \textbf{Docker Docs.} Compose quickstart: \url{https://docs.docker.com/compose/gettingstarted/}
\item \textbf{Docker Docs.} Image sharing: \url{https://docs.docker.com/docker-hub/repos/manage/hub-images/push/}
\item \textbf{Node.js.} Release schedule: \url{https://nodejs.org/en/about/previous-releases}
\item \textbf{Unit documents.} COMP3028-SPR26 Case Study and Assessment 2 Code Review brief.
\end{itemize}
\vspace{0.25cm}\textbf{Note:} Technical instructions checked against official documentation in November 2026.
''')
add('Questions and next steps',r'''
\begin{center}
{\huge\color{docker}\bfseries Build once. Run consistently. Share deliberately.}\\[0.6cm]
{\large Next: containerise a feature of your team's LocalLoop application.}\\[0.3cm]
\textbf{Discuss:} Which services deserve their own containers? Which data must persist?
\end{center}
''')
tex=P+'\n'.join(frames)+'\n\\end{document}\n'
out.write_text(tex,encoding='utf-8')
print(out, 'frames', len(frames), 'bytes', len(tex))
