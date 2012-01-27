# Import Docutils document tree nodes module.
#from docutils import nodes
# Import Directive base class.
#from sphinx.util.compat import Directive
from docutils import nodes

from docutils.parsers.rst import Directive
import os

def setup(app):
    app.add_directive("snippet", Snippet)

#class social(nodes.General, nodes.Element):
#    pass

TEMPLATES = "/home/james/projects/bulbflow.com/www/root/templates"

class Snippet(Directive):

    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = True
    has_content = False

    #def run(self):
    #    name = self.arguments[0]
    #    filename = "%s.html" % name
    #    full_path = os.path.join(os.path.dirname(__file__), "../../../templates", filename)
    #    snippet = open(full_path, 'r').read()
    #    return [nodes.raw(text=snippet, format='html')]

    def _social(self):
        name = self.arguments[0]
        filename = "%s.html" % name
        full_path = os.path.join(os.path.dirname(__file__), TEMPLATES, filename)
        snippet = open(full_path, 'r').read()
        return [nodes.raw(text=snippet, format='html')]

    def _comments(self):
        name = self.arguments[0]
        path = self.arguments[1]
        filename = "%s.html" % name
        full_path = os.path.join(os.path.dirname(__file__), TEMPLATES, filename)
        snippet = open(full_path, 'r').read()
        snippet = snippet.format(path=path)
        return [nodes.raw(text=snippet, format='html')]

    def run(self):
        snippet_map = dict(social=self._social,
                           comments=self._comments)
        name = str(self.arguments[0])
        snippet_func = snippet_map[name]
        return snippet_func()
