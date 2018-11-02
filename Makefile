

docs: docs.html docs.latex docs.latexpdf
docs.html:
	cd docs && make html
docs.latex:
	cd docs && make latex
docs.latexpdf:
	cd docs && make latexpdf
docs.serve:
	cd docs/build/html && python3 -m http.server
