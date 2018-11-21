Dataphile
=========

Dataphile is a high-level python package for both data analysis and data processing. It started as
a central repository of common tasks and capabilities used by the author, but has now evolved into
something others might find useful. See [components](#Components) below.


[![GitHub License](http://img.shields.io/badge/license-Apache-blue.svg?style=flat)](https://www.apache.org/licenses/LICENSE-2.0)
[![PyPI Version](https://img.shields.io/pypi/v/dataphile.svg)](https://pypi.org/project/dataphile/)
[![Docs Latest](https://readthedocs.org/projects/dataphile/badge/?version=latest)](https://dataphile.readthedocs.io)

---

<!-- Animated GIF of AutoGUI -->
<img src="https://lentner.io/images/auto_gui_interactive.gif" width="80%"
style="display:block;margin: 0 auto;">

**Figure**: Demonstration of Dataphile's `AutoGUI` feature.

Installation
------------

To install Dataphile for general purposes use Pip:

```
pip install dataphile
```

If you are using Anaconda, install using the above call to pip _from inside your environment_.
There is not as of yet a separate conda package.

Documentation
-------------

Documentation will be available at [dataphile.readthedocs.io](https://dataphile.readthedocs.io).
Currently, development of additional features is a priority, but this is a great place for
contributing to the project.

Contributions
-------------

Contributions are welcome  in the form of  suggestions for additional features,  pull requests with
new features or  bug fixes, etc. If you find  bugs or have questions, open an  _Issue_ here. If and
when the project grows, a  code of conduct will be provided along side  a more comprehensive set of
guidelines for contributing; until then, just be nice.

Road Map
--------

- **additional command line tools**<br>
	Many additional  command line tools  are planned for future  releases including tools  that expose
	database queries and filters.  Generally, just a massive extension of  the UNIX philosophy whereby
	we can compose several functions together with pipes to make unique workflows.

- **data acquisition**<br>
	One of  the motivations for this  package was to  provide an easy-to-use, high-level  interface to
	collecting scientific  data from an externel  device (e.g., over  USB). This, along side  a simple
	live  data visualization  feature would  go a  long  way for  high school  and university  student
	laboratory courses to both aquire and analyze  their data using all open-source tools right inside
	of a [Jupyter Notebook](https://jupyter.org).

- **documentation and package management**<br>
	A quickstart guide along with full documentation of all components needs to be built using Sphinx.

