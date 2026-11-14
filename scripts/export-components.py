"""Optional HTML partials for integrating the sections into another frontend."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build
pieces={
    'header':lambda:build.nav('/'), 'footer':build.footer, 'hero':build.hero,
    'channel-band':build.channel_band, 'agent-cards':build.solution_wall,
    'workflow-demo':build.story, 'coverage':build.coverage,
    'integrations':build.integrations, 'process':build.process,
    'why-chatversio':build.why, 'faq':build.questions,
    'closing-cta':build.closing, 'service-directory':build.directory,
    'contact':build.contact_page, 'booking':build.booking_page,
}
target=ROOT/'components'; target.mkdir(exist_ok=True)
for name,fn in pieces.items():
    (target/(name+'.html')).write_text(fn(),encoding='utf-8')
print(f'Exported {len(pieces)} reusable HTML sections.')
