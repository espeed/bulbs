import os
import io
import re
import string
import sre_parse
import sre_compile
from collections import OrderedDict, namedtuple
from sre_constants import BRANCH, SUBPATTERN
import hashlib
from . import utils

# GroovyScripts is the only public class

#
# The scanner code came from the TED project.
#

# TODO: Simplify this. You don't need group pattern detection.



Method = namedtuple('Method', ['definition', 'signature', 'body', 'sha1'])

class LastUpdatedOrderedDict(OrderedDict):
    """Store items in the order the keys were last added."""

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        OrderedDict.__setitem__(self, key, value)


class GroovyScripts(object):
    """
    Store and manage an index of Gremlin-Groovy scripts.

    :parm config: Config object.
    :type config: bulbs.Config

    :param file_path: Path to the base Groovy scripts file.
    :type file_path: str

    :ivar config: Config object.

    :ivar source_files: List containing the absolute paths to the script files,
                        in the order they were added.
    :ivar methods: LastUpdatedOrderedDict mapping Groovy method names to the 
                   Python Method object, which is a namedtuple containing the 
                   Groovy script's definition, signature, body, and sha1.

    .. note:: Use the update() method to add subsequent script files. 
              Order matters. Groovy methods are overridden if subsequently added
              files contain the same method name as a previously added file.

    """
    #: Relative path to the default script file
    default_file = "gremlin.groovy"

    def __init__(self, config, file_path=None):
        self.config = config

        self.source_file_map = OrderedDict()   # source_file_map[file_path] = namespace

        # may have model-specific namespaces
        # methods format: methods[method_name] = method_object
        self.namespace_map = OrderedDict()     # namespace_map[namespace] = methods

        if file_path is None:
            file_path = self._get_default_file()
        # default_namespace is derifed from the default_file so
        # default_namespace will be "gremlin" assuming you don't change default_file
        # or override default_file by passing in an explicit file_path
        self.default_namespace = self._get_filename(file_path) 
        self.update(file_path, self.default_namespace)


    def get(self, method_name, namespace=None):
        """
        Returns the Groovy script with the method name.
        
        :param method_name: Method name of a Groovy script.
        :type method_name: str

        :rtype: str

        """
        # Example: my_method                # uses default_namespace
        #          my_method, my_namespace  # pass in namespace as an arg
        #          my_namespace:my_method   # pass in  namespace via a method_name prefix
        method = self.get_method(method_name, namespace)
        script = method.signature if self.config.server_scripts is True else method.body 
        #script = self._build_script(method_definition, method_signature)
        return script

    def get_methods(self, namespace):
        return self.namespace_map[namespace]

    def get_method(self, method_name, namespace=None):
        """
        Returns a Python namedtuple for the Groovy script with the method name.
        
        :param method_name: Name of a Groovy method.
        :type method_name: str

        :rtype: bulbs.groovy.Method

        """
        namespace, method_name = self._get_namespace_and_method_name(method_name, namespace)
        methods = self.get_methods(namespace)
        return methods[method_name]
 
    def update(self, file_path, namespace=None):
        """
        Updates the script index with the Groovy methods in the script file.

        :rtype: None

        """
        file_path = os.path.abspath(file_path)
        methods = self._get_methods(file_path)
        if namespace is None:
            namespace = self._get_filename(file_path)
        self._maybe_create_namespace(namespace)
        self.source_file_map[file_path] = namespace
        self.namespace_map[namespace].update(methods)

    def refresh(self):
        """
        Refreshes the script index by re-reading the Groovy source files.

        :rtype: None

        """
        for file_path in self.source_file_map:
            namespace = self.source_file_map[file_path]
            methods = self._get_methods(file_path)
            self.namespace_map[namespace].update(methods)

    def _maybe_create_namespace(self, namespace):
        if namespace not in self.namespace_map:
            methods = LastUpdatedOrderedDict()
            self.namespace_map[namespace] = methods

    def _get_filename(self, file_path):
        base_name = os.path.basename(file_path)
        file_name, file_ext = os.path.splitext(base_name)
        return file_name

    def _get_namespace_and_method_name(self, method_name, namespace=None):
        if namespace is None:
            namespace = self.default_namespace
        parts = method_name.split(":") 
        if len(parts) == 2:
            # a namespace explicitly set in method_name takes precedent
            namespace = parts[0]
            method_name = parts[1]
        return namespace, method_name

    def _get_methods(self,file_path):
        return Parser(file_path).get_methods()

    def _get_default_file(self):
        file_path = utils.get_file_path(__file__, self.default_file)
        return file_path

    def _build_script(definition, signature): 
        # This method isn't be used right now...
        # This method is not current (rework it to suit needs).
        script = """
        try {
          current_sha1 = methods[name]
        } catch(e) {
          current_sha1 = null
          methods = [:]
          methods[name] = sha1
        }
        if (current_sha1 == sha1) 
          %s

        try { 
          return %s
        } catch(e) {

          return %s 
        }""" % (signature, definition, signature)
        return script



class Scanner:
    def __init__(self, lexicon, flags=0):
        self.lexicon = lexicon
        self.group_pattern = self._get_group_pattern(flags)
        
    def _get_group_pattern(self,flags):
        # combine phrases into a compound pattern
        patterns = []
        sub_pattern = sre_parse.Pattern()
        sub_pattern.flags = flags
        for phrase, action in self.lexicon:
            patterns.append(sre_parse.SubPattern(sub_pattern, [
                (SUBPATTERN, (len(patterns) + 1, sre_parse.parse(phrase, flags))),
                ]))
        sub_pattern.groups = len(patterns) + 1
        group_pattern = sre_parse.SubPattern(sub_pattern, [(BRANCH, (None, patterns))])
        return sre_compile.compile(group_pattern)

    def get_multiline(self,f,m):
        content = []
        next_line = ''
        while not re.search("^}",next_line):
            content.append(next_line)
            try:
                next_line = next(f)    
            except StopIteration:
                # This will happen at end of file
                next_line = None
                break
        content = "".join(content)       
        return content, next_line

    def get_item(self,f,line):
        # IMPORTANT: Each item needs to be added sequentially 
        # to make sure the record data is grouped properly
        # so make sure you add content by calling callback()
        # before doing any recursive calls
        match = self.group_pattern.scanner(line).match() 
        if not match:
            return
        callback = self.lexicon[match.lastindex-1][1]
        if "def" in match.group():
            # this is a multi-line get
            first_line = match.group()
            body, current_line = self.get_multiline(f,match)
            sections = [first_line, body, current_line]
            content = "\n".join(sections).strip()
            callback(self,content)
            if current_line:
                self.get_item(f,current_line)
        else:
            callback(self,match.group(1))

    def scan(self,file_path):
        fin = io.open(file_path, 'r', encoding='utf-8')    
        for line in fin:
            self.get_item(fin,line)

    
class Parser(object):

    def __init__(self, groovy_file):
        self.methods = OrderedDict()
        # handler format: (pattern, callback)
        handlers = [ ("^def( .*)", self.add_method), ]
        Scanner(handlers).scan(groovy_file)

    def get_methods(self):
        return self.methods

    # Scanner Callback
    def add_method(self,scanner,token):
        method_definition = token
        method_signature = self._get_method_signature(method_definition)
        method_name = self._get_method_name(method_signature)
        method_body = self._get_method_body(method_definition)
        # NOTE: Not using sha1, signature, or the full method right now
        # because of the way the GSE works. It's easier to handle version
        # control by just using the method_body, which the GSE compiles,
        # creates a class out of, and stores in a classMap for reuse.
        # You can't do imports inside Groovy methods so just using the func body 
        sha1 = self._get_sha1(method_definition)
        #self.methods[method_name] = (method_signature, method_definition, sha1)
        method = Method(method_definition, method_signature, method_body, sha1)
        self.methods[method_name] = method

    def _get_method_signature(self,method_definition):
        pattern = '^def(.*){'
        return re.search(pattern,method_definition).group(1).strip()
            
    def _get_method_name(self,method_signature):
        pattern = '^(.*)\('
        return re.search(pattern,method_signature).group(1).strip()

    def _get_method_body(self,method_definition):
        # remove the first and last lines, and return just the method body
        lines = method_definition.split('\n')
        body_lines = lines[+1:-1]
        method_body = "\n".join(body_lines).strip()
        return method_body

    def _get_sha1(self,method_definition):
        # this is used to detect version changes
        method_definition_bytes = method_definition.encode('utf-8')
        sha1 = hashlib.sha1()
        sha1.update(method_definition_bytes)
        return sha1.hexdigest()




#print Parser("gremlin.groovy").get_methods()
