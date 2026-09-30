#!/usr/bin/env python3
"""Generate the Task 2 evidence PDF (requires the reportlab Python package)."""
from datetime import datetime, timezone
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted

root = Path(__file__).resolve().parents[1]
evidence = root / 'docs/task-2/evidence'
output = root / 'docs/task-2/Task-2-Containerization-Report.pdf'
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='SmallText', parent=styles['BodyText'], fontSize=9, leading=13))
styles.add(ParagraphStyle(name='CodeSmall', fontName='Courier', fontSize=8, leading=11))
story = []
def title(text): story.append(Paragraph(escape(text), styles['Title']))
def heading(text): story.append(Paragraph(escape(text), styles['Heading2']))
def para(text): story.append(Paragraph(text, styles['BodyText'])); story.append(Spacer(1, 3*mm))
def code(text): story.append(Preformatted(text, styles['CodeSmall'])); story.append(Spacer(1,3*mm))
def table(rows, widths):
    formatted = [[Paragraph(escape(str(c)), styles['SmallText']) for c in row] for row in rows]
    t = Table(formatted, colWidths=widths, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef8')),
                          ('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),0.4,colors.lightgrey),
                          ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
                          ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(t);story.append(Spacer(1,4*mm))

title('Progree DevOps Internship')
heading('Task 2: Application Containerization & Asset Optimization')
para('<b>Intern:</b> Haseeb Ullah<br/><b>Environment:</b> Ubuntu, Docker Engine, Docker Compose<br/><b>Evidence captured:</b> '+datetime.now(timezone.utc).strftime('%d %B %Y (UTC)'))
para('This project packages the existing Wanderlust travel blog into four cooperating containers. The DevOps contribution covers multi-stage images, configuration, networking, persistent storage, health checks, verification, and documentation.')
para('<b>Application attribution:</b> Wanderlust by Krishna R Acharya and contributors, MIT license. The original application, license, and history are retained. This report does not claim authorship of the upstream web application.')
heading('Requirement coverage')
table([
 ['Requirement','Delivered implementation'],
 ['Multi-dependency runtime stack','React frontend served by Nginx, Express API, MongoDB, and Redis.'],
 ['Multi-stage Dockerfiles','Frontend build/runtime stages; backend dependency/runtime stages.'],
 ['Image footprint optimization','Alpine bases, production-only API dependencies, static frontend assets, narrow COPY rules, and .dockerignore files.'],
 ['Secure environment configuration','Non-secret environment settings plus per-service, read-only secret files. Database application user is separate from root.'],
 ['Functional port routing','127.0.0.1:8080 maps to the frontend; /api requests proxy to backend:5000. Database/cache ports stay internal.'],
], [145,350])
heading('Architecture')
code('Browser: localhost:8080\n        |\n        v\nNginx frontend:8080 -- /api --> Express backend:5000\n                                    |           |\n                                    v           v\n                               MongoDB:27017  Redis:6379\n                                    |\n                               Named volume')
para('MongoDB and Redis use an internal Docker network. Only the backend joins both the web and data networks. The demo exposes only the frontend on localhost.')
story.append(PageBreak())

title('Build and runtime design')
heading('Frontend')
para('Node installs locked dependencies and compiles TypeScript and Vite assets in a build stage. The final non-root Nginx image receives only the compiled dist directory and routing configuration. It supports direct client-side routes and compresses eligible responses. Browser requests use relative API URLs.')
heading('Backend')
para('A dependency stage installs production dependencies with npm ci --omit=dev. The runtime stage copies only the dependency tree and required application files. Nodemon remains a development dependency. Node runs directly as a non-root user with a read-only root filesystem.')
heading('Runtime settings and credentials')
table([
 ['Setting','Purpose'],
 ['WEB_PORT=8080','Host port, configurable in the ignored root .env file.'],
 ['MONGO_HOST / MONGO_DATABASE / MONGO_USER','Internal database connection metadata.'],
 ['MONGO_PASSWORD_FILE','Read-only application database credential mount.'],
 ['REDIS_URL / REDIS_PASSWORD_FILE','Internal cache URL and mounted password.'],
 ['JWT_SECRET_FILE','Mounted signing secret for the email/password backend.'],
 ['COOKIE_SECURE=false','Local HTTP demonstration; use HTTPS and secure cookies for a public deployment.'],
], [225,270])
para('The setup script generates random credentials without displaying them. The .secrets directory is private on the host and excluded from Git. Compose mounts are local files, not an encrypted vault. The backend never receives the database root password. MongoDB initializes users only when its data volume is empty.')
heading('Reliability and application fixes')
para('Docker health checks verify startup readiness. The API waits for its dependencies and closes connections on SIGTERM. MongoDB keeps data in named volumes; Redis remains disposable cache. An inherited cache-invalidation bug was reproduced and fixed so updated or deleted posts no longer remain in cached lists. Credential-bearing database URLs are excluded from logs.')
heading('Start and verify')
code('python3 scripts/setup-local.py\ndocker compose up -d --build --wait --wait-timeout 180\npython3 scripts/seed-demo.py\npython3 scripts/verify-task2.py --recreate\npython3 scripts/capture-evidence.py')
story.append(PageBreak())

title('Measured verification results')
rows = json.loads((evidence / 'image-sizes.json').read_text())
bytag = {r['image']:r for r in rows}
b = bytag['progree-wanderlust-backend:baseline']['size_bytes']
r = bytag['progree-wanderlust-backend:task2']['size_bytes']
f = bytag['progree-wanderlust-frontend:build-stage']['size_bytes']
g = bytag['progree-wanderlust-frontend:task2']['size_bytes']
table([['Comparison','Before (MiB)','Runtime (MiB)','Reduction'],
       ['Backend baseline vs runtime',f'{b/1024**2:.2f}',f'{r/1024**2:.2f}',f'{(1-r/b)*100:.1f}%'],
       ['Frontend build stage vs runtime',f'{f/1024**2:.2f}',f'{g/1024**2:.2f}',f'{(1-g/f)*100:.1f}%']], [205,95,100,95])
para('Values are Docker image inspect .Size measurements from this engine, converted to MiB. They are not measurements of unique disk savings. The backend baseline includes development dependencies; the frontend comparison removes its build toolchain. Base images are pinned to tested digests. Raw image IDs and sizes are retained in evidence/image-sizes.json.')
heading('Functional checks')
for line in (evidence/'verification.txt').read_text().splitlines():
    if line.startswith('PASS:'):
        story.append(Paragraph(escape(line), styles['SmallText']));story.append(Spacer(1,2*mm))
heading('Configuration checks')
for line in (evidence/'configuration-checks.txt').read_text().splitlines():
    story.append(Paragraph(escape(line), styles['SmallText']));story.append(Spacer(1,2*mm))
heading('Scope and limitations')
para('This is a localhost containerization demo. The inherited post API has no authorization requirement. The upstream sign-in/sign-up screens are placeholders; backend email/password endpoints were verified separately. OAuth requires provider credentials and was not configured. Application dependency modernization and production security assessment are outside Task 2.')
story.append(PageBreak())

title('Application evidence')
heading('Homepage with database-backed demo posts')
story.append(Image(str(evidence/'homepage.png'),width=495,height=495*1100/1440))
para('Captured from the running application at http://localhost:8080 using headless Chrome. The rendered demo posts were loaded from MongoDB through the Nginx proxy and Express API.')
heading('Container status')
status=json.loads((evidence/'container-status.json').read_text())
table([['Service','Health','Host access']]+[[s['service'],s['health'],'127.0.0.1:8080' if s['service']=='frontend' else 'Internal only'] for s in sorted(status['services'],key=lambda x:x['service'])],[160,140,195])
para('The recreation test removed and replaced all four containers while retaining named volumes, then retrieved the same updated post. Temporary test posts and accounts were cleaned up. Demo posts remain for review.')
story.append(PageBreak())

title('Create-post page and project handoff')
story.append(Image(str(evidence/'create-post.png'),width=495,height=495*1100/1440))
para('Direct navigation to /add-blog renders the React form, verifying Nginx\'s single-page-application fallback. API create/read/update/delete behavior is recorded in verification.txt.')
heading('Project and evidence locations')
para('Local directory: /home/ubuntu/devops/progree-devops-internship<br/>Portfolio repository name: progree-devops-internship<br/>Guide: docs/task-2/README.md<br/>Evidence: docs/task-2/evidence/<br/>Stop while keeping data: docker compose down')
para('Task 2 is complete based on the recorded checks. Tasks 3 and 4 are separate work. Combine this evidence with the other completed tasks into ONE final PDF for the organizer\'s Google Form by the stated deadline of 5 October 2026. This document has not been submitted.')
heading('References')
para('Docker multi-stage builds: https://docs.docker.com/build/building/multi-stage/<br/>Docker Compose secrets: https://docs.docker.com/compose/how-tos/use-secrets/<br/>Original application: https://github.com/krishnaacharyaa/wanderlust')

def footer(canvas, doc):
    canvas.saveState();canvas.setFont('Helvetica',8);canvas.setFillColor(colors.grey)
    canvas.drawString(18*mm,12*mm,'Haseeb Ullah | Progree DevOps Internship | Task 2')
    canvas.drawRightString(A4[0]-18*mm,12*mm,str(doc.page));canvas.restoreState()
SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18*mm,leftMargin=18*mm,
                  topMargin=16*mm,bottomMargin=20*mm,title='Task 2 - Application Containerization',
                  author='Haseeb Ullah').build(story,onFirstPage=footer,onLaterPages=footer)
print(output)
