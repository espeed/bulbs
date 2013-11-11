import os
import io
import yaml 
from string import Template
from .utils import get_file_path

# You only need this for Gremlin scripts if the server doesn't implement param 
# bindings; otherwise, use groovy.py with gremlin.groovy -- it's several 
# hunderd times faster. Cypher is handled differently on the server side so 
# there there is no performance issue.

class Yaml(object):
    """Load Gremlin or Cypher YAML templates from a .yaml source file."""

    def __init__(self,file_name=None):
        self.file_name = self._get_file_name(file_name)
        self.templates = self._get_templates(self.file_name)

    def get(self,name,params={}):
        """Return a Gremlin script or Cypher query, generated from the params."""
        template = self.templates.get(name)
        #params = self._quote_params(params)
        return template.substitute(params)

    def update(self,file_name):
        new_templates = self._get_templates(file_name)
        self.templates.update(new_templates)
        
    def refresh(self):
        """Refresh the stored templates from the YAML source."""
        self.templates = self._get_templates()

    def _get_file_name(self,file_name):
        if file_name is None:
            dir_name = os.path.dirname(__file__)
            file_name = get_file_path(dir_name,"gremlin.yaml")
        return file_name

    def _get_templates(self,file_name):
        templates = dict()
        with io.open(file_name, encoding='utf-8') as f:
            yaml_map = yaml.load(f)    
            for name in yaml_map: # Python 3
                template = yaml_map[name] 
                templates[name] = Template(template)
        return templates

    #def _quote_params(self,params):
    #    quoted_tuple = map(self._quote,params.items())
    #    params = dict(quoted_tuple)
    #    return params

    #def _quote(self,pair):
    #    key, value = pair
    #    if type(value) == str:
    #        value = "'%s'" % value
    #    elif value is None:
    #        value = ""
    #    return key, value
