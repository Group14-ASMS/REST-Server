all: debug

debug:
	python run.py

test:
	py.test -vv test.py

.PHONY: clean
clean:
	-@rm app.db
	-@find . -name '*.pyc' -exec rm {} \;
