"""
Bulbs
-----

Bulbs is a Python persistence framework for graph databases that 
connects to Neo4j Server, Rexster, OrientDB, Lightsocket, and more.

"""
import sys
from setuptools import Command, setup, find_packages

class run_audit(Command):
    """Audits source code using PyFlakes for following issues:
       - Names which are used but not defined or used before they are defined.
       - Names which are redefined without having been used.
    """
    description = "Audit source code with PyFlakes"
    user_options = []

    def initialize_options(self):
        all = None

    def finalize_options(self):
        pass

    def run(self):
        import os, sys
        try:
            import pyflakes.scripts.pyflakes as flakes
        except ImportError:
            print("Audit requires PyFlakes installed in your system.")
            sys.exit(-1)

        dirs = ['bulbs', 'tests']
        # Add example directories
        #for dir in ['blog',]:
        #    dirs.append(os.path.join('examples', dir))
        # TODO: Add test subdirectories
        warns = 0
        for dir in dirs:
            for filename in os.listdir(dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    warns += flakes.checkPath(os.path.join(dir, filename))
        if warns > 0:
            print(("Audit finished with total %d warnings." % warns))
        else:
            print("No problems found in sourcecode.")

def run_tests():
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from bulbs_tests import suite
    return suite()

# Python 3
install_requires = ['distribute', 'httplib2>=0.7.2', 'pyyaml>=3.10', 'six', 'omnijson']
if sys.version < '3':
    install_requires.append('python-dateutil==1.5')
else:
    # argparse is in 3.2 but not 3.1
    install_requires.append('argparse')
    install_requires.append('python-dateutil>=2')


setup (
    name = 'bulbs',
    version = '0.3.29',
    url = 'https://github.com/espeed/bulbs',
    license = 'BSD',
    author = 'James Thornton',
    author_email = 'james@jamesthornton.com',
    description = 'A Python persistence framework for graph databases that '
                  'connects to Neo4j Server, Rexster, OrientDB, Lightsocket.',
    long_description = __doc__,
    keywords = "graph database DB persistence framework rexster gremlin cypher neo4j orientdb",   
    packages = find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires, 
    classifiers = [
        "Programming Language :: Python",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Database",
        "Topic :: Database :: Front-Ends",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        ],
    cmdclass={'audit': run_audit},
    test_suite='__main__.run_tests'
)
