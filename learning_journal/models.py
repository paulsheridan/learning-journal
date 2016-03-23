from datetime import datetime
from jinja2 import Markup
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import ZopeTransactionExtension
import markdown

from pyramid.security import (
    Allow,
    Everyone,
    Authenticated,
    )

from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime,
)

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)


class MyRoot(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, Authenticated, 'edit')]


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode(120))
    text = Column(Unicode)
    created = Column(DateTime, default=datetime.utcnow)

    @property
    def rendered_text(self):
        return render_markdown(self.text)


def render_markdown(content):
    output = Markup(markdown.markdown(content))
    return output
