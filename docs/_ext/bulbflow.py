# Import Docutils document tree nodes module.
#from docutils import nodes
# Import Directive base class.
from sphinx.util.compat import Directive
#from docutils.parsers.rst import Directive

def setup(app):
    app.add_directive("social", Social)

class Social(Directive):

    def run(self):
        filename = "%s/social.html"
        full_path = os.path.join(os.path.dirname(__file__), "../templates", filename)
        html = open(full_path, 'r').read()
        return "HELLO"

