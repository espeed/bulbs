import os
import re
import sre_parse
import sre_compile
from sre_constants import BRANCH, SUBPATTERN
import hashlib
from . import utils

# GroovyScripts is the only public class

#
# The scanner code came from the TED project.
#

# TODO: Simplify this. You don't need group pattern detection.


class GroovyScripts(object):
    """
    Store and manage an index of Gremlin-Groovy scripts.

    :param file_path: Path to the base Groovy scripts file.
    :type file_path: str

    :ivar source_files: List containing the absolute paths to the script files,
                        in the order they were added.
    :ivar methods: Dict mapping Groovy method names to the actual scripts.

    .. note:: Use the update() method to add subsequent script files. 
              Order matters. Groovy methods are overridden if subsequently added
              files contain the same method name as a previously added file.

    """
    #: Relative path to the default script file
    default_file = "gremlin.groovy"

    def __init__(self, file_path=None):
        self.source_files = list()  # an ordered set might be better

        # methods format: methods[method_name] = method_body
        self.methods = dict()

        if file_path is None:
            file_path = self._get_default_file()
        self.update(file_path)

    def get(self, method_name):
        """
        Returns the Groovy script with the method name.
        
        :param method_name: Method name of a Groovy script.
        :type method_name: str

        :rtype: str

        """
        return self.methods[method_name]
        #script = self._build_script(method_definition, method_signature)
        #return script

    def update(self, file_path):
        """
        Updates the script index with the Groovy methods in the script file.

        :rtype: None

        """
        file_path = os.path.abspath(file_path)
        methods = self._get_methods(file_path)
        self._add_source_file(file_path)
        self.methods.update(methods)

    def refresh(self):
        """
        Refreshes the script index by re-reading the Groovy source files.

        :rtype: None

        """
        for file_path in self.source_files:
            methods = self._get_methods(file_path)
            self.methods.update(methods)

    def _add_source_file(self,file_path):
        # order matters (last in takes precedence if it overrides a method)
        self.source_files.append(file_path)

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
        fin = open(file_path, 'r')    
        for line in fin:
            self.get_item(fin,line)

    
class Parser(object):

    def __init__(self, groovy_file):
        self.methods = {}
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
        #sha1 = self._get_sha1(method_definition)
        #self.methods[method_name] = (method_signature, method_definition, sha1)
        self.methods[method_name] = method_body

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
        sha1 = hashlib.sha1()
        sha1.update(method_definition)
        return sha1.hexdigest()




#print Parser("gremlin.groovy").get_methods()
