from giotto import get_config

from giotto.programs import GiottoProgram, ProgramManifest
from giotto.programs.management import management_manifest
from giotto.contrib.static.programs import StaticServe
from giotto.views import BasicView, jinja_template

from crawl import crawl
from models import Submission

def front():
    session = get_config('db_session')
    return session.query(Submission).filter(Submission.current_rank>0).order_by('current_rank')

manifest = ProgramManifest({
    '': GiottoProgram(
        model=[front],
        #cache=30,
        view=BasicView(
            html=jinja_template('better_front.html'),
        ),
    ),
    'about': GiottoProgram(
        view=BasicView(
            html=jinja_template('about.html')
        ),
    ),
    'crawl': GiottoProgram(
        controllers=['cmd'],
        model=[crawl],
        view=BasicView
    ),
    'mgt': management_manifest,
    'static': StaticServe('/static/'),
})